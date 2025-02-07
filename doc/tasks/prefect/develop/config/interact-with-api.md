# 在 Python 中管理运行元数据

[`PrefectClient`](https://prefect-python-sdk-docs.netlify.app/prefect/client/) 提供了许多方法，简化了执行操作的过程，例如：

- 重新安排延迟的流程运行
- 从工作区获取最后 `N` 个已完成的流程运行

`PrefectClient` 是异步上下文管理器。以下是使用示例：

```python
from prefect import get_client


async with get_client() as client:
    response = await client.hello()
    print(response.json()) # 👋
```

## 示例

### 重新安排延迟的流程运行

为了批量重新安排延迟的流程运行，删除这些延迟的流程运行并以一个带有延迟的“已计划”状态创建新的流程运行。例如，如果你不小心将许多部署的流程运行安排到一个不活跃的工作池中，这会很有用。

以下示例将名为 `healthcheck-storage-test` 的部署的最后三个延迟的流程运行重新安排在它们原始预期开始时间六小时后运行。同时，它也会删除该部署的任何剩余延迟的流程运行。

```python
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional


from prefect import get_client
from prefect.client.schemas.filters import (
    DeploymentFilter, FlowRunFilter
)
from prefect.client.schemas.objects import FlowRun
from prefect.client.schemas.sorting import FlowRunSort
from prefect.states import Scheduled

async def reschedule_late_flow_runs(
    deployment_name: str,
    delay: timedelta,
    most_recent_n: int,
    delete_remaining: bool = True,
    states: Optional[list[str]] = None
) -> list[FlowRun]:
    if not states:
        states = ["Late"]

    async with get_client() as client:
        flow_runs = await client.read_flow_runs(
            flow_run_filter=FlowRunFilter(
                state=dict(name=dict(any_=states)),
                expected_start_time=dict(
                    before_=datetime.now(timezone.utc)
                ),
            ),
            deployment_filter=DeploymentFilter(
                name={'like_': deployment_name}
            ),
            sort=FlowRunSort.START_TIME_DESC,
            limit=most_recent_n if not delete_remaining else None
        )

        if not flow_runs:
            print(f"No flow runs found in states: {states!r}")
            return []
        
        rescheduled_flow_runs = []
        for i, run in enumerate(flow_runs):
            await client.delete_flow_run(flow_run_id=run.id)
            if i < most_recent_n:
                new_run = await client.create_flow_run_from_deployment(
                    deployment_id=run.deployment_id,
                    state=Scheduled(
                        scheduled_time=run.expected_start_time + delay
                    ),
                )
                rescheduled_flow_runs.append(new_run)
            
        return rescheduled_flow_runs


if __name__ == "__main__":
    rescheduled_flow_runs = asyncio.run(
        reschedule_late_flow_runs(
            deployment_name="healthcheck-storage-test",
            delay=timedelta(hours=6),
            most_recent_n=3,
        )
    )
    
    print(f"Rescheduled {len(rescheduled_flow_runs)} flow runs")
        
    assert all(
        run.state.is_scheduled() for run in rescheduled_flow_runs
    )
    assert all(
        run.expected_start_time > datetime.now(timezone.utc)
        for run in rescheduled_flow_runs
    )
```

### 从你的工作空间获取最后 `N` 个已完成的流程运行

要从你的工作空间获取最后`N`个已完成的流程运行，请使用`read_flow_runs`和`prefect.client.schemas`。
这个例子将展示如何从你的工作空间获取最后三个已完成的流程运行：

```python
import asyncio
from typing import Optional

from prefect import get_client
from prefect.client.schemas.filters import FlowRunFilter
from prefect.client.schemas.objects import FlowRun
from prefect.client.schemas.sorting import FlowRunSort


async def get_most_recent_flow_runs(
    n: int = 3,
    states: Optional[list[str]] = None
) -> list[FlowRun]:
    if not states:
        states = ["COMPLETED"]
    
    async with get_client() as client:
        return await client.read_flow_runs(
            flow_run_filter=FlowRunFilter(
                state={'type': {'any_': states}}
            ),
            sort=FlowRunSort.END_TIME_DESC,
            limit=n,
        )


if __name__ == "__main__":
    last_3_flow_runs: list[FlowRun] = asyncio.run(
        get_most_recent_flow_runs()
    )
    print(last_3_flow_runs)
    
    assert all(
        run.state.is_completed() for run in last_3_flow_runs
    )
    assert (
        end_times := [run.end_time for run in last_3_flow_runs]
    ) == sorted(end_times, reverse=True)
```

与其从整个工作空间中获取最后三个，您还可以使用 `DeploymentFilter` 来获取特定部署的最后三个已完成的流程运行。

### 通过客户端将所有正在运行的流程转换为已取消状态

使用 `get_client` 将多个运行设置为“已取消”状态。
下面的代码在脚本运行时取消所有处于“待处理”、“运行中”、“计划中”或“延迟”状态的流程运行。

```python
import anyio


from prefect import get_client
from prefect.client.schemas.filters import FlowRunFilter, FlowRunFilterState, FlowRunFilterStateName
from prefect.client.schemas.objects import StateType

async def list_flow_runs_with_states(states: list[str]):
    async with get_client() as client:
        flow_runs = await client.read_flow_runs(
            flow_run_filter=FlowRunFilter(
                state=FlowRunFilterState(
                    name=FlowRunFilterStateName(any_=states)
                )
            )
        )
    return flow_runs


async def cancel_flow_runs(flow_runs):
    async with get_client() as client:
        for idx, flow_run in enumerate(flow_runs):
            print(f"[{idx + 1}] Cancelling flow run '{flow_run.name}' with ID '{flow_run.id}'")
            state_updates = {}
            state_updates.setdefault("name", "Cancelled")
            state_updates.setdefault("type", StateType.CANCELLED)
            state = flow_run.state.copy(update=state_updates)
            await client.set_flow_run_state(flow_run.id, state, force=True)


async def bulk_cancel_flow_runs():
    states = ["Pending", "Running", "Scheduled", "Late"]
    flow_runs = await list_flow_runs_with_states(states)

    while len(flow_runs) > 0:
        print(f"Cancelling {len(flow_runs)} flow runs\n")
        await cancel_flow_runs(flow_runs)
        flow_runs = await list_flow_runs_with_states(states)
    print("Done!")


if __name__ == "__main__":
    anyio.run(bulk_cancel_flow_runs)
```

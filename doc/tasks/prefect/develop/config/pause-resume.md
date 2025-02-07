# 暂停和恢复流程运行

Prefect允许您使用两个功能相似但略有不同的函数来中断一个流程的运行。
当一个流程运行被暂停时，代码执行停止，但进程继续运行。
当一个流程运行被挂起时，代码执行停止，进程也停止运行。

## 暂停流程运行

Prefect使得在手动审批过程中可以暂停正在进行中的流程运行成为可能。
Prefect通过[`pause_flow_run`](https://prefect-python-sdk-docs.netlify.app/prefect/engine/#prefect.engine.pause_flow_run)和[`resume_flow_run`](https://prefect-python-sdk-docs.netlify.app/prefect/engine/#prefect.engine.resume_flow_run)函数提供了这一能力。

```{admonition} **超时**
:class: note
默认情况下，暂停的流程运行将在一小时后超时。
超时后，流程运行将以一条说明其被暂停且从未恢复的消息失败。
可以使用`timeout`参数以秒为单位指定不同的超时周期。
```

您可以在流程中调用`pause_flow_run`：

```python
from prefect import task, flow, pause_flow_run, resume_flow_run

@task
async def marvin_setup():
    return "a raft of ducks walk into a bar..."


@task
async def marvin_punchline():
    return "it's a wonder none of them ducked!"


@flow
async def inspiring_joke():
    await marvin_setup()
    await pause_flow_run(timeout=600)  # pauses for 10 minutes
    await marvin_punchline()
```

您也可以实施条件性暂停：

```python
from prefect import task, flow, pause_flow_run

@task
def task_one():
    for i in range(3):
        sleep(1)
        print(i)

@flow(log_prints=True)
def my_flow():
    terminal_state = task_one.submit(return_state=True)
    if terminal_state.type == StateType.COMPLETED:
        print("Task one succeeded! Pausing flow run..")
        pause_flow_run(timeout=2)
    else:
        print("Task one failed. Skipping pause flow run..")
```

这个流程在第一个任务后暂停代码执行，并等待恢复以传达关键信息。

```bash
await inspiring_joke()
> "a raft of ducks walk into a bar..."
```

要恢复暂停的流程运行，请在Prefect用户界面中点击 **Resume** 或通过客户端代码调用 `resume_flow_run` 实用程序。

```python
from prefect import resume_flow_run

resume_flow_run(FLOW_RUN_ID)
```

暂停的流程流动随后完成。

```bash
> "it's a wonder none of them ducked!"
```

### 挂起流程运行

与暂停流程运行类似，Prefect允许挂起正在进行的流程运行。

```{admonition} **暂停和挂起流程运行的区别**
:class: note

暂停和挂起流程运行之间存在重要区别。
当你暂停流程运行时，流程代码仍在运行但被阻塞，直到有人恢复流程。
然而，挂起流程运行时情况并非如此。
当你挂起流程运行时，流程完全退出，运行它的基础设施（例如，Kubernetes Job）也会被拆除。
```

这意味着你可以通过挂起流程运行来节省成本，而不是为长时间运行的基础设施付费。
但是，当流程运行恢复时，流程代码将从头开始重新执行。
我们建议使用[任务](https://docs.prefect.io/v3/develop/write-tasks)和[任务缓存](https://docs.prefect.io/v3/develop/task-caching)来避免重复计算昂贵的操作。

Prefect通过[`suspend_flow_run`](https://prefect-python-sdk-docs.netlify.app/prefect/engine/#prefect.engine.suspend_flow_run)和[`resume_flow_run`](https://prefect-python-sdk-docs.netlify.app/prefect/engine/#prefect.engine.resume_flow_run)函数以及Prefect UI提供这一能力。

当在流程中调用`suspend_flow_run`时，会立即挂起流程运行的执行。
流程运行被标记为“挂起”，并且不会恢复，直到调用`resume_flow_run`。

```{admonition} **超时**
:class: note

默认情况下，挂起的流程运行在一小时后超时。
超时后，流程运行失败，并显示消息表示其已挂起且未恢复。
你可以使用`timeout`参数指定不同的超时时间（以秒为单位），或传递`timeout=None`来禁用超时。
```

以下是一个示例流程，它在暂停时不会阻塞流程执行。
这个流程在一个任务后退出，并在恢复时重新调度。
第一个任务的结果被存储起来，而不是重新运行。

```python
from prefect import flow, pause_flow_run, task

@task(persist_result=True)
def foo():
    return 42

@flow(persist_result=True)
def noblock_pausing():
    x = foo.submit()
    pause_flow_run(timeout=30, reschedule=True)
    y = foo.submit()
    z = foo(wait_for=[x])
    alpha = foo(wait_for=[y])
    omega = foo(wait_for=[x, y])
```

您可以通过调用 `suspend_flow_run(flow_run_id=<ID>)` 或者在 Prefect UI 或 Prefect Cloud 中选择 **暂停** 按钮来中断流程运行。

要恢复已暂停的流程运行，可以在 Prefect UI 中点击 **恢复** 或者通过客户端代码调用 `resume_flow_run` 工具。

```python
from prefect import resume_flow_run

resume_flow_run(FLOW_RUN_ID)
```

```{admonition} **您无法独立于其父运行暂停子流程**
:class: note

如果您使用一个流程通过 `run_deployment` 来安排另一个流程的运行，默认情况下，被安排的流程运行会作为嵌套流程运行与调用流程链接。这意味着您无法独立于调用流程暂停被安排的流程运行。

如果您需要独立于调用流程暂停被安排的流程运行，请在调用 `run_deployment` 时设置 `as_subflow=False` 以禁用此链接。
```

## 在暂停或挂起流程运行时等待输入

```{warning}
`pause_flow_run` 或 `suspend_flow_run` 函数中使用的 `wait_for_input` 参数是一个实验性功能。
此功能的接口或行为可能会在未来的版本中未经警告地改变。

如果您遇到任何问题，请在Slack上或通过GitHub issue告诉我们。
```

当您暂停或挂起流程运行时，可能需要等待用户输入。
Prefect提供了一种方式来实现这一点，即使用 `pause_flow_run` 和 `suspend_flow_run` 函数。
这些函数接受一个 `wait_for_input` 参数，它应该是 `prefect.input.RunInput`（一个Pydantic模型）的子类。
恢复流程运行时，用户需要为该模型提供数据。成功验证后，
流程运行恢复，并且 `pause_flow_run` 或 `suspend_flow_run`
的返回值是包含所提供数据的模型实例。

以下是示例流程，它暂停并等待用户的输入：

```python
from prefect import flow, pause_flow_run
from prefect.input import RunInput


class UserNameInput(RunInput):
    name: str


@flow(log_prints=True)
async def greet_user():
    user_input = await pause_flow_run(
        wait_for_input=UserNameInput
    )

    print(f"Hello, {user_input.name}!")
```

运行此流程将创建一个流程实例。该流程实例会持续运行，直到代码执行到达`pause_flow_run`处，此时它将进入“暂停”状态。执行将被阻塞并等待恢复。

在恢复流程运行时，系统会提示用户为`UserNameInput`模型的`name`字段提供一个值。验证成功后，流程将继续运行，并且`pause_flow_run`的返回值是包含提供数据的`UserNameInput`模型实例。

有关在暂停和挂起流程运行时从用户那里接收输入的更多信息，请参阅[发送和接收流程运行输入](https://docs.prefect.io/v3/develop/inputs)。

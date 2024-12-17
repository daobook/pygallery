# 访问运行时上下文

Prefect通过运行上下文追踪当前流程或任务运行的信息。

运行上下文就像是一个全局变量，它允许Prefect引擎确定你的运行之间的关系，例如你的任务是从哪个流程调用的。

运行上下文本身包含许多内部对象，这些对象被Prefect用于管理你的运行执行，并且只在特定情况下可用。出于这个原因，我们提供了一个简单接口，它只包括你关心的项目，并在必要时动态检索额外信息。我们将这称为“运行时上下文”，因为它包含的信息只能在运行期间访问。

````{admonition} 通过环境变量模拟值
class: tip

你可能希望为了测试目的模拟某些值。例如，通过手动设置ID或计划开始时间来确保你的代码正常运行。

通过使用以下模式的环境变量在运行时模拟值：
`PREFECT__RUNTIME__{SUBMODULE}__{KEY_NAME}=value`:

```bash
export PREFECT__RUNTIME__TASK_RUN__FAKE_KEY='foo'
python -c 'from prefect.runtime import task_run; print(task_run.fake_key)' # "foo"
```

如果环境变量模拟了现有的运行时属性，该值将被转换为相同的类型。这对于基本类型的运行时属性（`bool`, `int`, `float` 和 `str`）以及 `pendulum.DateTime` 都是有效的。对于复杂类型如 `list` 或 `dict`，我们建议使用 [monkeypatch](https://docs.pytest.org/en/latest/how-to/monkeypatch.html) 或类似工具进行模拟。

````

## 访问运行时信息

`prefect.runtime`模块是所有运行时上下文访问的核心。每个主要的运行时概念都有自己的子模块：

- `deployment`: 获取当前运行部署的相关信息
- `flow_run`: 获取当前流程运行的相关信息
- `task_run`: 获取当前任务运行的相关信息

例如：

```python my_runtime_info.py
from prefect import flow, task
from prefect import runtime

@flow(log_prints=True)
def my_flow(x):
    print("My name is", runtime.flow_run.name)
    print("I belong to deployment", runtime.deployment.name)
    my_task(2)

@task
def my_task(y):
    print("My name is", runtime.task_run.name)
    print("Flow run parameters:", runtime.flow_run.parameters)

if __name__ == "__main__":
    my_flow(1)
```

运行此文件将产生如下类似的输出：

```bash
10:08:02.948 | INFO    | prefect.engine - Created flow run 'solid-gibbon' for flow 'my-flow'
10:08:03.555 | INFO    | Flow run 'solid-gibbon' - My name is solid-gibbon
10:08:03.558 | INFO    | Flow run 'solid-gibbon' - I belong to deployment None
10:08:03.703 | INFO    | Flow run 'solid-gibbon' - Created task run 'my_task-0' for task 'my_task'
10:08:03.704 | INFO    | Flow run 'solid-gibbon' - Executing 'my_task-0' immediately...
10:08:04.006 | INFO    | Task run 'my_task-0' - My name is my_task-0
10:08:04.007 | INFO    | Task run 'my_task-0' - Flow run parameters: {'x': 1}
10:08:04.105 | INFO    | Task run 'my_task-0' - Finished in state Completed()
10:08:04.968 | INFO    | Flow run 'solid-gibbon' - Finished in state Completed('All states completed.')
```

上述示例展示了如何访问关于当前流程运行、任务运行和部署的信息。
当没有部署的情况下运行时（通过`python my_runtime_info.py`），你应该会看到日志中记录“属于部署None”。
当信息不可用时，运行时总是返回一个空值。
因为这个流程是在部署外部运行的，所以没有部署数据。
如果这个流程是作为部署的一部分运行的，我们将看到部署的名称而不是None。

查看[运行时API参考](https://prefect-python-sdk-docs.netlify.app/prefect/runtime/flow_run/)以获取可用属性的完整列表。

## 直接访问运行上下文

使用`prefect.context.get_run_context()`函数可以访问当前的运行上下文。
如果当前没有可用的运行上下文，即您不在流程或任务运行中，此函数将抛出异常。
如果有任务运行上下文可用，即使有流程运行上下文可用，也将返回任务运行上下文。

或者，您可以明确地访问流程运行或任务运行上下文。
例如，这允许您从任务运行中访问流程运行上下文。

由于序列化和反序列化的开销较大，Prefect不会将流程运行上下文发送给分布式任务工作器。

```python
from prefect.context import FlowRunContext, TaskRunContext

flow_run_ctx = FlowRunContext.get()
task_run_ctx = TaskRunContext.get()
```

与 `get_run_context` 不同，如果上下文不可用，这些方法调用不会引发错误。相反，它们将返回 `None`。

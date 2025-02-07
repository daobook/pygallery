# 配置日志记录

当您运行流程或任务时，Prefect 会自动发出一系列标准的日志记录，您可以在用户界面、命令行界面或通过 API 进行检查。
此外，您还可以在流程和任务运行期间发出自定义的日志消息，以捕获对您的工作流程重要的特定事件或信息。

每当您执行流程或任务时，Prefect 的日志记录都会自动配置。

标准日志集包括：
- 关于运行创建或重命名的信息
- 关于运行状态变化的信息
- 执行过程中出现的任何错误的回溯信息

## Prefect日志记录器

Prefect 提供了一组日志记录器，您可以使用它们来发出自己的自定义日志。
要使用 Prefect 日志记录器，请从 `prefect.logging` 模块导入 `get_run_logger` 函数。
这个函数返回日志记录器实例，该实例了解当前的流程或任务运行上下文，允许进行更详细和有上下文的日志记录。
这使得您可以根据相关的运行信息（如运行 ID 和运行名称）在 UI 或 API 中探索日志。

```{warning}
`get_run_logger()` 只能在流程或任务的上下文中使用。

要在其他地方使用具有相同配置的普通Python日志记录器，请使用 `prefect.logging` 中的 `get_logger()`。

通过 `get_logger()` 检索的日志记录器 **不会** 将日志记录发送到 Prefect API。
```

### 记录流程和任务

要记录流程或任务，首先使用 `get_run_logger()` 获取日志记录器实例，然后调用标准的 Python [日志方法](https://docs.python.org/3/library/logging.html)：

```python
from prefect import flow, task
from prefect.logging import get_run_logger


@task(name="log-example-task")
def logger_task():
    # this logger instance will emit logs 
    # associated with both the flow run *and* the individual task run
    logger = get_run_logger()
    logger.info("INFO level log message from a task.")
    logger.debug("DEBUG level log message from a task.")


@flow(name="log-example-flow")
def logger_flow():
    # this logger instance will emit logs
    # associated with the flow run only
    logger = get_run_logger()
    logger.info("INFO level log message.")
    logger.debug("DEBUG level log message.")
    logger.error("ERROR level log message.")
    logger.critical("CRITICAL level log message.")

    logger_task()
```

### 记录打印语句

Prefect 为流程和任务提供了 `log_prints` 选项，以启用对 `print` 语句的自动日志记录功能。当特定任务或流程的 `log_prints=True` 时，Python 内置的 `print` 函数会被修改为将输出重定向到该任务或流程范围内的 Prefect 日志记录器。这些日志将以 `INFO` 级别发出。默认情况下，任务运行和嵌套流程运行会继承其父流程运行的 `log_prints` 设置，除非它们通过自己的明确 `log_prints` 设置选择退出。

```python
from prefect import task, flow

@task
def my_task():
    print("we're logging print statements from a task")

@flow(log_prints=True)
def my_flow():
    print("we're logging print statements from a flow")
    my_task()
```

输出：


```bash
15:52:11.244 | INFO    | prefect.engine - Created flow run 'emerald-gharial' for flow 'my-flow'
15:52:11.812 | INFO    | Flow run 'emerald-gharial' - we're logging print statements from a flow
15:52:11.926 | INFO    | Flow run 'emerald-gharial' - Created task run 'my_task-20c6ece6-0' for task 'my_task'
15:52:11.927 | INFO    | Flow run 'emerald-gharial' - Executing 'my_task-20c6ece6-0' immediately...
15:52:12.217 | INFO    | Task run 'my_task-20c6ece6-0' - we're logging print statements from a task
```

```python
from prefect import task, flow

@task(log_prints=False)
def my_task():
    print("not logging print statements in this task")

@flow(log_prints=True)
def my_flow():
    print("we're logging print statements from a flow")
    my_task()
```

在任务级别设置 `log_prints=False` 将输出：

```bash
15:52:11.244 | INFO    | prefect.engine - Created flow run 'emerald-gharial' for flow 'my-flow'
15:52:11.812 | INFO    | Flow run 'emerald-gharial' - we're logging print statements from a flow
15:52:11.926 | INFO    | Flow run 'emerald-gharial' - Created task run 'my_task-20c6ece6-0' for task 'my_task'
15:52:11.927 | INFO    | Flow run 'emerald-gharial' - Executing 'my_task-20c6ece6-0' immediately...
not logging print statements in this task
```

你可以通过配置 `PREFECT_LOGGING_LOG_PRINTS` 设置，将此行为设定为所有 Prefect 流程和任务运行的默认值。

```bash
prefect config set PREFECT_LOGGING_LOG_PRINTS=True
```

## 日志配置

Prefect依赖于[Python标准实现的日志配置](https://docs.python.org/3/library/logging.config.html)。
任何版本的Prefect的默认日志配置完整规范始终可以在[这里](https://github.com/PrefectHQ/prefect/blob/main/src/prefect/logging/logging.yml)查看。
默认的日志级别是`INFO`。

### 自定义日志配置

Prefect提供多个设置项来配置日志级别和各个日志记录器。

通过使用形式为`PREFECT_LOGGING_[PATH]_[TO]_[KEY]=value`的Prefect设置，可以覆盖[Prefect的日志配置文件](https://github.com/PrefectHQ/prefect/blob/main/src/prefect/logging/logging.yml)中的任何值，该设置对应于您正在配置的字段的嵌套地址。

例如，要更改流程运行的默认日志级别但不更改任务运行的级别，请更新您的配置文件：
```bash
prefect config set PREFECT_LOGGING_LOGGERS_PREFECT_FLOW_RUNS_LEVEL="ERROR"
```
或者设置相应的环境变量：
```bash
export PREFECT_LOGGING_LOGGERS_PREFECT_FLOW_RUNS_LEVEL="ERROR"
```

您还可以配置"根"Python日志记录器。根日志记录器接收所有日志记录器的日志，除非它们通过禁用传播明确选择退出。默认情况下，根日志记录器配置为将`WARNING`级别的日志输出到控制台。与其他日志设置一样，您可以从环境或在日志配置文件中覆盖此设置。例如，您可以使用`PREFECT_LOGGING_ROOT_LEVEL`环境变量更改级别。

在某些情况下，您可能希望完全重写Prefect的日志配置，通过提供自己的`logging.yml`文件。
您可以通过以下两种方式之一创建自己的`logging.yml`版本：

1. 在您的`PREFECT_HOME`目录（默认为`~/.prefect`）中创建一个`logging.yml`文件。
2. 使用`PREFECT_LOGGING_SETTINGS_PATH`设置指定到您的`logging.yml`文件的自定义路径。

如果Prefect无法在指定位置找到`logging.yml`文件，它将回退到使用默认的日志配置。

有关`logging.yml`使用的更多关于配置选项和语法的信息，请参阅Python [Logging configuration](https://docs.python.org/3/library/logging.config.html#logging.config.dictConfig)文档。

```{note}
正如所有Prefect配置一样，日志设置也是在运行时加载的。
这意味着要在远程环境中自定义Prefect的日志记录，需要在该环境中设置适当的环境变量和/或配置文件。
```

### 格式化器

Perfect日志格式化器指定了日志消息的格式。任务和流程运行记录的默认格式为：
对于任务，格式为 `"%(asctime)s.%(msecs)03d | %(levelname)-7s | Task run %(task_run_name)r - %(message)s"`；
类似地，对于流程，格式为 `"%(asctime)s.%(msecs)03d | %(levelname)-7s | Flow run %(flow_run_name)r - %(message)s"`。

可用于插值在日志消息中的变量因记录器而异。除了运行上下文、消息字符串和任何关键字参数外，流程和任务运行记录器还可以访问其他变量。

流程运行记录器有以下变量可用于格式化：

- `flow_run_name`
- `flow_run_id`
- `flow_name`

任务运行记录器有以下变量可用于格式化：

- `task_run_id`
- `flow_run_id`
- `task_run_name`
- `task_name`
- `flow_run_name`
- `flow_name`

你可以通过设置相关的环境变量或修改自定义的 `logging.yml` 文件中的格式化器来指定自定义格式，如前所述。例如，以下更改了流程运行格式化器的格式：


```bash
PREFECT_LOGGING_FORMATTERS_STANDARD_FLOW_RUN_FMT="%(asctime)s.%(msecs)03d | %(levelname)-7s | %(flow_run_id)s - %(message)s"
```

生成的消息使用流程运行ID代替名称，如下所示：


```bash
10:40:01.211 | INFO    | e43a5a80-417a-41c4-a39e-2ef7421ee1fc - Created task run
'othertask-1c085beb-3' for task 'othertask'
```
### 样式

默认情况下，Prefect会在控制台日志中用多种颜色高亮显示特定的关键字。你可以通过设置`PREFECT_LOGGING_COLORS`来开启或关闭高亮显示：

```bash
PREFECT_LOGGING_COLORS=False
```

你也可以通过更新样式来改变高亮的内容，甚至调整颜色。有关可用键的详细信息，请参阅[Prefect日志配置文件](https://github.com/PrefectHQ/prefect/blob/main/src/prefect/logging/logging.yml)中的`styles`部分。

```{note}
请注意，这些样式设置仅影响终端内的显示，不会影响Prefect UI。
```

你甚至可以构建自己的处理程序，并使用[自定义高亮器](https://rich.readthedocs.io/en/stable/highlighting.html#custom-highlighters)来实现这一点。例如，要额外高亮显示电子邮件地址：

1. 将以下代码复制并粘贴到`my_package_or_module.py`（根据需要重命名）中，该文件与流程运行脚本位于同一目录；或者最好将其作为Python包的一部分，这样它就可以在`site-packages`中访问，并在你的工作环境中的任何地方使用。

```python
import logging
from typing import Dict, Union

from rich.highlighter import Highlighter

from prefect.logging.handlers import PrefectConsoleHandler
from prefect.logging.highlighters import PrefectConsoleHighlighter

class CustomConsoleHighlighter(PrefectConsoleHighlighter):
    base_style = "log."
    highlights = PrefectConsoleHighlighter.highlights + [
        # ?P<email> 将此表达式命名为 `email`
        r"(?P<email>[\w-]+@([\w-]+\.)+[\w-]+)",
    ]

class CustomConsoleHandler(PrefectConsoleHandler):
    def __init__(
        self,
        highlighter: Highlighter = CustomConsoleHighlighter,
        styles: Dict[str, str] = None,
        level: Union[int, str] = logging.NOTSET,
   ):
        super().__init__(highlighter=highlighter, styles=styles, level=level)
```

2. 更新`~/.prefect/logging.yml`以使用`my_package_or_module.CustomConsoleHandler`，并额外引用基础样式和命名表达式：`log.email`。

```yaml
    console_flow_runs:
        level: 0
        class: my_package_or_module.CustomConsoleHandler
        formatter: flow_runs
        styles:
            log.email: magenta
            # 其他样式可以在这里追加，例如
            # log.completed_state: green
```

3. 在下一次流程运行时，类似于电子邮件的文本将被高亮显示。例如，`my@email.com`将以洋红色显示：

```python
from prefect import flow
from prefect.logging import get_run_logger

@flow
def log_email_flow():
    logger = get_run_logger()
    logger.info("my@email.com")

log_email_flow()
```

### 高亮日志

要在Prefect日志中使用[Rich的标记](https://rich.readthedocs.io/en/stable/markup.html#console-markup)，首先配置`PREFECT_LOGGING_MARKUP`：

```bash
PREFECT_LOGGING_MARKUP=True
```

以下示例将“fancy”以红色加粗显示：

```python
from prefect import flow
from prefect.logging import get_run_logger

@flow
def my_flow():
    logger = get_run_logger()
    logger.info("This is [bold red]fancy[/]")

my_flow()
```

```{admonition} **不准确的日志可能导致问题**
:class: warning

如果启用了此功能，包含方括号的字符串可能会被不准确地解释，导致输出不完整。例如，`DROP TABLE [dbo].[SomeTable];"`会输出为`DROP TABLE .[SomeTable];`。
```

默认情况下，Prefect不会捕获您的流程和任务使用的库的日志语句。您可以通过`PREFECT_LOGGING_EXTRA_LOGGERS`设置来指示Prefect包含这些库的日志。

要使用此设置，请指定一个或多个要包括的Python库名称，并用逗号分隔。例如，如果您希望Prefect在流程和任务运行日志中捕获Dask和SciPy的日志语句，请使用：

```
PREFECT_LOGGING_EXTRA_LOGGERS=dask,scipy
```

将此设置配置为环境变量或在配置文件中。有关如何使用设置的更多详细信息，请参见[设置](/v3/develop/settings-and-profiles/)。

## 从命令行访问日志

您可以使用Prefect的CLI检索特定流程运行ID的日志：

```bash
prefect flow-run logs MY-FLOW-RUN-ID
```

如果您希望以本地文件的形式访问日志，这将特别有用：

```bash
prefect flow-run logs MY-FLOW-RUN-ID > flow.log
```

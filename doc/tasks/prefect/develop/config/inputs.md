# 发送和接收流程运行输入

在Prefect的用户界面中，流程可以暂停或挂起执行，并在接收到类型检查过的输入后自动恢复。
流程还可以在运行时随时发送和接收经过类型检查的输入——无需暂停或挂起。

本指南解释了如何使用这些功能来构建交互式工作流。

```{admonition} **异步Python语法** 
:class: note

本部分的大多数示例代码使用了异步 Python 函数和 `await` 关键字。然而，与其他Prefect功能一样，你可以使用或不使用`await`调用这些函数。
```

## 暂停或中断流程，直到它接收到输入

您可以在Prefect的用户界面中暂停或挂起流程，直到它接收到用户输入。当您需要请求额外的信息或反馈以继续流程时，这将非常有用。这些工作流程通常被称为[人类参与的循环](https://hai.stanford.edu/news/humans-loop-design-interactive-ai-systems)（Human-in-the-loop，简称 HITL）系统。

```{admonition} **人类参与的循环互动**
:class: note

在商业世界中，暂停以询问人类确认工作流是否应继续的审批工作流程非常常见。某些类型的[机器学习训练](https://link.springer.com/article/10.1007/s10462-022-10246-w)和人工智能工作流程从融合 HITL 设计中受益。
```

### 等待输入

在暂停或挂起流程时，若要接收输入，请使用 `pause_flow_run` 或 `suspend_flow_run` 函数中的 `wait_for_input` 参数。
此参数接受以下类型之一：

- 内置类型如 `int` 或 `str`，或者内置集合如 `List[int]`
- `pydantic.BaseModel` 的子类
- `prefect.input.RunInput` 的子类

```{admonition} 何时使用 RunModel 或 BaseModel 代替内置类型？
:class: tip

有几个理由推荐使用 `RunModel` 或 `BaseModel`。首先，当你让 Prefect 自动为你输入的类型创建这些类时，用户在点击流程运行的“恢复”按钮时，在Prefect的用户界面中看到的字段名为 `value`，并且没有任何帮助文本来说明该字段的含义。如果你创建 `RunInput` 或 `BaseModel`，你可以更改细节如字段名、帮助文本和默认值，用户将在“恢复”表单中看到这些更改。
```

暂停或挂起并等待输入的最简单方法是传递内置类型：

```python
from prefect import flow
from prefect.flow_runs import pause_flow_run
from prefect.logging import get_run_logger

@flow
def greet_user():
    logger = get_run_logger()

    user = pause_flow_run(wait_for_input=str)

    logger.info(f"Hello, {user}!")
```

在这个例子中，流程运行暂停，直到用户在 Prefect UI 中点击“继续”按钮，输入名称，并提交表单。

```{admonition} 你可以为 wait_for_input 传递的类型

当你为 `pause_flow_run`或`suspend_flow_run`的`wait_for_input`参数传递内建类型（如`int`）时，
Prefect会自动创建一个包含一个字段的Pydantic模型，该字段使用你指定的类型进行注解。这意味着你可以使用
[Pydantic接受的任何类型注解](https://docs.pydantic.dev/1.10/usage/types/)来与这些函数一起使用。
```

而不是内建类型，你可以传递 `pydantic.BaseModel` 类。如果你已经有想要使用的 `BaseModel`，这将非常有用：

```python
from prefect import flow
from prefect.flow_runs import pause_flow_run
from prefect.logging import get_run_logger
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


@flow
async def greet_user():
    logger = get_run_logger()

    user = await pause_flow_run(wait_for_input=User)

    logger.info(f"Hello, {user.name}!")
```

````{admonition} BaseModel 类会自动升级为 RunInput 类
:class: note

当您将 `pydantic.BaseModel` 类作为 `wait_for_input` 参数传递给 `pause_flow_run` 或 `suspend_flow_run` 时，Prefect 会自动创建行为与您的 `BaseModel` 相同的 `RunInput` 类并使用它代替。

`RunInput` 类包含额外的逻辑，允许在运行时发送和接收流。您不应该注意到任何差异。
````

对于高级用例，例如覆盖Prefect存储流程运行输入的方式，请创建 `RunInput` 类：

```python
from prefect import flow
from prefect.logging import get_run_logger
from prefect.input import RunInput

class UserInput(RunInput):
    name: str
    age: int

    # Imagine overridden methods here.
    def override_something(self, *args, **kwargs):
        super().override_something(*args, **kwargs)

@flow
async def greet_user():
    logger = get_run_logger()

    user = await pause_flow_run(wait_for_input=UserInput)

    logger.info(f"Hello, {user.name}!")
```

### 提供初始数据

使用 `with_initial_data` 方法为模型中的字段设置默认值。这对于为您自己的 `RunInput` 类中的字段提供默认值非常有用。

继续上面的例子，您可以将 `name` 字段的默认值设置为 `"anonymous"`。

```python
from prefect import flow
from prefect.logging import get_run_logger
from prefect.input import RunInput

class UserInput(RunInput):
    name: str
    age: int

@flow
async def greet_user():
    logger = get_run_logger()

    user_input = await pause_flow_run(
        wait_for_input=UserInput.with_initial_data(name="anonymous")
    )

    if user_input.name == "anonymous":
        logger.info("Hello, stranger!")
    else:
        logger.info(f"Hello, {user_input.name}!")
```

当用户看到这个输入的表单时，姓名字段默认包含 `"anonymous"` 作为默认值。

### 提供带有运行时数据的描述

你可以在流程运行暂停时，在 Prefect UI 中显示动态的 Markdown 描述。
这一功能使得上下文特定的提示成为可能，增强了清晰度和用户交互性。以上例为基础：

```python
from datetime import datetime
from prefect import flow
from prefect.flow_runs import pause_flow_run
from prefect.logging import get_run_logger
from prefect.input import RunInput


class UserInput(RunInput):
    name: str
    age: int


@flow
async def greet_user():
    logger = get_run_logger()
    current_date = datetime.now().strftime("%B %d, %Y")

    description_md = f"""
**Welcome to the User Greeting Flow!**
Today's Date: {current_date}

Please enter your details below:
- **Name**: What should we call you?
- **Age**: Just a number, nothing more.
"""

    user_input = await pause_flow_run(
        wait_for_input=UserInput.with_initial_data(
            description=description_md, name="anonymous"
        )
    )

    if user_input.name == "anonymous":
        logger.info("Hello, stranger!")
    else:
        logger.info(f"Hello, {user_input.name}!")
```

当用户看到这个输入表单时，给定的Markdown会出现在输入字段上方。

### 处理自定义验证

Prefect使用你`RunInput`或`BaseModel`类中的字段和类型提示来验证流程接收到的输入的一般结构。
如果你需要更复杂的验证，可以使用Pydantic的[model_validators](https://docs.pydantic.dev/latest/concepts/validators/#model-validators)。

```{admonition} 调用自定义验证将在流程恢复后进行
:class: warning

Prefect将你的`RunInput`或`BaseModel`类中的类型注解转换为JSON模式，并在UI中使用该模式进行客户端验证。然而，自定义验证需要运行在你的`RunInput`类中定义的Python逻辑。因此，验证将在流程恢复后进行，所以你应该在你的流程中明确处理它。继续阅读以了解一个最佳实践的例子。
```

下面是使用自定义`model_validator`的`RunInput`类的示例：

```python
from typing import Literal

import pydantic

from prefect.input import RunInput


class ShirtOrder(RunInput):
    size: Literal["small", "medium", "large", "xlarge"]
    color: Literal["red", "green", "black"]

    @pydantic.model_validator(mode="after")
    def validate_age(self):
        if self.color == "green" and self.size == "small":
            raise ValueError(
                "Green is only in-stock for medium, large, and XL sizes."
            )

        return self
```

在这个例子中，使用 Pydantic 的 `model_validator` 装饰器来为 `ShirtOrder` 类定义自定义验证。
您可以按照以下流程使用它：

```python
from typing import Literal

import pydantic

from prefect import flow, pause_flow_run
from prefect.input import RunInput


class ShirtOrder(RunInput):
    size: Literal["small", "medium", "large", "xlarge"]
    color: Literal["red", "green", "black"]

    @pydantic.model_validator(mode="after")
    def validate_age(self):
        if self.color == "green" and self.size == "small":
            raise ValueError(
                "Green is only in-stock for medium, large, and XL sizes."
            )

        return self


@flow
def get_shirt_order():
    shirt_order = pause_flow_run(wait_for_input=ShirtOrder)
```

如果用户选择的尺寸和颜色组合不是 `small` 和 `green`，流程运行将成功恢复。
然而，如果用户选择了尺寸  `small` 和颜色 `green`，流程运行会恢复，并且 `pause_flow_run` 会抛出 `ValidationError` 异常。这将导致流程运行失败并记录错误。

为了避免流程运行失败，使用 `while` 循环并在抛出 `ValidationError` 异常时再次暂停：

```python
from typing import Literal

import pydantic
from prefect import flow
from prefect.flow_runs import pause_flow_run
from prefect.logging import get_run_logger
from prefect.input import RunInput


class ShirtOrder(RunInput):
    size: Literal["small", "medium", "large", "xlarge"]
    color: Literal["red", "green", "black"]

    @pydantic.model_validator(mode="after")
    def validate_age(self):
        if self.color == "green" and self.size == "small":
            raise ValueError(
                "Green is only in-stock for medium, large, and XL sizes."
            )

        return self


@flow
def get_shirt_order():
    logger = get_run_logger()
    shirt_order = None

    while shirt_order is None:
        try:
            shirt_order = pause_flow_run(wait_for_input=ShirtOrder)
        except pydantic.ValidationError as exc:
            logger.error(f"Invalid size and color combination: {exc}")

    logger.info(
        f"Shirt order: {shirt_order.size}, {shirt_order.color}"
    )
```

这段代码会导致流程运行持续暂停，直到用户输入一个有效的年龄。

作为额外的步骤，你可以使用[自动化事件](https://docs.prefect.io/v3/automate/events/automations-triggers)触发器来向用户提示错误。

## 运行时发送和接收输入

使用 `send_input` 和 `receive_input` 函数在运行时向流程发送输入或从流程接收输入。
你不需要暂停或挂起流程就可以发送或接收输入。

```{admonition} 不暂停或挂起时发送或接收输入的原因
:class: note

你可能希望在设计为处理实时数据的流程运行时不暂停或挂起的情况下发送或接收输入。例如，在一个实时监控系统中，你可能需要根据传入的数据更新某些参数，而不中断流程。另一个例子是有一个长时间运行的流程，它以低延迟连续响应运行时输入。例如，如果你正在构建一个聊天机器人，你可以有一个启动GPT助手并管理对话线程的流程。
```

对 `send_input` 和 `receive_input` 函数来说，最重要的参数是 `run_type`，它应该是以下之一：

- 内置类型，如 `int` 或 `str`
- `pydantic.BaseModel` 类
- `prefect.input.RunInput` 类

```{admonition} 何时使用 BaseModel 或 RunInput 而不是内置类型
:class: tip

大多数内置类型和内置类型的集合应该可以与 `send_input` 和 `receive_input` 一起工作，但嵌套集合类型（例如列表中的元组）存在警告。例如，`List[Tuple[str, float]])`。在这种情况下，验证可能发生在你的流程接收数据之后，因此调用 `receive_input` 可能会引发 `ValidationError`。你可以计划捕获这个异常，并考虑将字段放在显式的 `BaseModel` 或 `RunInput` 中，这样你的流程只接收到完全匹配的类型。

见下面的 `receive_input`、`send_input` 以及这两个函数协同工作的示例。
```

### 接收输入

以下流程使用 `receive_input` 函数持续接收姓名，并为每个接收到的姓名打印个性化问候语：

```python
from prefect import flow
from prefect.input.run_input import receive_input


@flow
async def greeter_flow():
    async for name_input in receive_input(str, timeout=None):
        # Prints "Hello, andrew!" if another flow sent "andrew"
        print(f"Hello, {name_input}!")
```

当你将诸如 `str` 这样的类型传入 `receive_input` 时，Prefect会创建 `RunInput` 类来自动管理你的输入。当流程发送这种类型的输入时，Prefect使用 `RunInput` 类来验证输入。
如果验证成功，你的流程将以你指定的类型接收输入。在这个例子中，如果流程接收到有效的字符串作为输入，变量 `name_input` 将包含该字符串值。

相反，如果你传入 `BaseModel`，Prefect 会将你的 `BaseModel` 升级为 `RunInput` 类，而你的流程看到的变量（在本例中为 `name_input`）是行为类似 `BaseModel` 的 `RunInput` 实例。如果你传入的是 `RunInput` 类，则无需升级，你将获得 `RunInput` 实例。

更简单的方法是将如 `str` 这样的类型传入 `receive_input`。如果你需要访问包含接收值的生成的 `RunInput`，请将 `with_metadata=True` 传递给 `receive_input`：

```python
from prefect import flow
from prefect.input.run_input import receive_input


@flow
async def greeter_flow():
    async for name_input in receive_input(
        str,
        timeout=None,
        with_metadata=True
    ):
        # Input will always be in the field "value" on this object.
        print(f"Hello, {name_input.value}!")

```

```{admonition} 何时使用 `with_metadata=True`
:class: tip

访问接收输入的 `RunInput` 对象的主要用途是通过 `RunInput.respond()` 函数对发送者进行响应，或访问输入的唯一键。
```

请注意打印 `name_input.value` 的过程。当 Prefect 为您从内置类型生成 `RunInput` 时，`RunInput` 类有名为 `value` 的字段，该字段使用了与您指定的类型相匹配的类型注解。因此，如果您这样调用 `receive_input`：`receive_input(str, with_metadata=True)`，这相当于手动创建以下 `RunInput` 类和 `receive_input` 调用：


```python
from prefect import flow
from prefect.input.run_input import RunInput

class GreeterInput(RunInput):
    value: str

@flow
async def greeter_flow():
    async for name_input in receive_input(GreeterInput, timeout=None):
        print(f"Hello, {name_input.value}!")
```

````{admonition} 在 receive_input 和 send_input 中使用的类型必须匹配
:class: warning

为了使流程能够接收输入，发送方必须使用接收方正在接收的相同类型。这意味着如果接收方正在接收`GreeterInput`，则发送方必须发送`GreeterInput`。如果接收方正在接收`GreeterInput`而发送方发送了`str`类型的输入，Prefect会自动将其升级为`RunInput`类，这样类型就不匹配；这就意味着接收流程不会收到输入。然而，如果流程最终调用了`receive_input(str)`，输入将会等待。
````

### 跟踪您已经看到的输入

默认情况下，每次调用 `receive_input` 时，都会得到一个迭代器，该迭代器遍历特定流程运行的所有已知输入，从第一个接收的开始。迭代时，迭代器会跟踪您的当前位置，或者您可以调用 `next()` 明确获取下一个输入。如果您在循环中使用迭代器，应该将其分配给变量：

```python
from prefect import flow, get_client
from prefect.deployments import run_deployment
from prefect.input.run_input import receive_input, send_input

EXIT_SIGNAL = "__EXIT__"


@flow
async def sender():
    greeter_flow_run = await run_deployment(
        "greeter/send-receive", timeout=0, as_subflow=False
    )
    client = get_client()

    # Assigning the `receive_input` iterator to a variable
    # outside of the the `while True` loop allows us to continue
    # iterating over inputs in subsequent passes through the
    # while loop without losing our position.
    receiver = receive_input(
        str,
        with_metadata=True,
        timeout=None,
        poll_interval=0.1
    )

    while True:
        name = input("What is your name? ")
        if not name:
            continue

        if name == "q" or name == "quit":
            await send_input(
                EXIT_SIGNAL,
                flow_run_id=greeter_flow_run.id
            )
            print("Goodbye!")
            break

        await send_input(name, flow_run_id=greeter_flow_run.id)

        # Saving the iterator outside of the while loop and
        # calling next() on each iteration of the loop ensures
        # that we're always getting the newest greeting. If we
        # had instead called `receive_input` here, we would
        # always get the _first_ greeting this flow received,
        # print it, and then ask for a new name.
        greeting = await receiver.next()
        print(greeting)
```

迭代器有助于跟踪您的流程已经接收到的输入。如果您希望您的流程暂停，然后在稍后恢复，
请保存您已经看到的输入的键，以便流程在恢复时可以重新读取它们。
考虑使用一个[块](https://docs.prefect.io/v3/develop/blocks)，例如`JSONBlock`。

以下流程接收输入30秒，然后自行暂停，这会退出流程并拆除基础设施：

```python
from prefect import flow
from prefect.logging import get_run_logger
from prefect.flow_runs import suspend_flow_run
from prefect.blocks.system import JSON
from prefect.context import get_run_context
from prefect.input.run_input import receive_input


EXIT_SIGNAL = "__EXIT__"


@flow
async def greeter():
    logger = get_run_logger()
    run_context = get_run_context()
    assert run_context.flow_run, "Could not see my flow run ID"

    block_name = f"{run_context.flow_run.id}-seen-ids"

    try:
        seen_keys_block = await JSON.load(block_name)
    except ValueError:
        seen_keys_block = JSON(
            value=[],
        )

    try:
        async for name_input in receive_input(
            str,
            with_metadata=True,
            poll_interval=0.1,
            timeout=30,
            exclude_keys=seen_keys_block.value
        ):
            if name_input.value == EXIT_SIGNAL:
                print("Goodbye!")
                return
            await name_input.respond(f"Hello, {name_input.value}!")

            seen_keys_block.value.append(name_input.metadata.key)
            await seen_keys_block.save(
                name=block_name,
                overwrite=True
            )
    except TimeoutError:
        logger.info("Suspending greeter after 30 seconds of idle time")
        await suspend_flow_run(timeout=10000)
```

当这个流程处理名称输入时，它会将流程运行输入的 _key_ 添加到`seen_keys_block`中。

当流程稍后暂停并恢复时，它会从JSON块中读取已经看过的键，
并将它们作为`exclude_keys`参数传递给`receive_input`。

### 回应输入的发送者
当你的流程从另一个流程接收到输入时，Prefect知道发送流程的运行ID，因此接收流程可以通过调用它所接收的`RunInput`实例上的`respond`方法来回应。这里有一些要求：
- 传入一个`BaseModel`或`RunInput`，或使用`with_metadata=True`。
- 你正在回应的流程必须接收与你发送给它的相同类型的输入。
`respond`方法等同于调用`send_input(..., flow_run_id=sending_flow_run.id)`。但是使用`respond`，
你的流程不需要知道发送流程运行的ID。
接下来，让`greeter_flow`对名称输入做出回应，而不是打印它们：

```python
from prefect import flow
from prefect.input.run_input import receive_input


@flow
async def greeter():
    async for name_input in receive_input(
        str,
        with_metadata=True,
        timeout=None
    ):
        await name_input.respond(f"Hello, {name_input.value}!")
```

However, this flow runs forever unless there's a signal that it should exit.
Here's how to make it to look for a special string:

```python
from prefect import flow
from prefect.input.run_input import receive_input



EXIT_SIGNAL = "__EXIT__"


@flow
async def greeter():
    async for name_input in receive_input(
        str,
        with_metadata=True,
        poll_interval=0.1,
        timeout=None
    ):
        if name_input.value == EXIT_SIGNAL:
            print("Goodbye!")
            return
        await name_input.respond(f"Hello, {name_input.value}!")
```

### 发送输入

使用`send_input`函数向流程发送输入。这与`receive_input`函数类似，同样接受`run_input`参数。这个参数可以是内置类型如`str`，或者是`BaseModel`或`RunInput`的子类。

```{admonition} 何时向流程运行发送输入
:class: note

一旦你有了流程运行的ID，就应该立即向该流程运行发送输入。即使流程还没有开始接收输入，你也可以发送输入。如果你在流程开始接收之前发送了输入，当它调用`receive_input`时，只要`send_input`和`receive_input`调用中的类型匹配，它就会看到你的输入。
```

接下来，创建 `sender` 流程，该流程启动 `greeter` 流程运行，然后进入循环——持续从终端获取输入并发送至`greeter`流程：

```python
from prefect import flow
from prefect.deployments import run_deployment

@flow
async def sender():
    greeter_flow_run = await run_deployment(
        "greeter/send-receive", timeout=0, as_subflow=False
    )
    receiver = receive_input(str, timeout=None, poll_interval=0.1)
    client = get_client()

    while True:
        flow_run = await client.read_flow_run(greeter_flow_run.id)

        if not flow_run.state or not flow_run.state.is_running():
            continue

        name = input("What is your name? ")
        if not name:
            continue

        if name == "q" or name == "quit":
            await send_input(
                EXIT_SIGNAL,
                flow_run_id=greeter_flow_run.id
            )
            print("Goodbye!")
            break

        await send_input(name, flow_run_id=greeter_flow_run.id)
        greeting = await receiver.next()
        print(greeting)
```

首先，`run_deployment`启动一个名为`greeter`的流运行。这需要一个已经部署好的流程在一个进程中运行。
该进程开始执行`greeter`，而`sender`则继续执行。调用`run_deployment(..., timeout=0)`确保`sender`不会等待`greeter`流运行完成，因为它正在循环中运行，并且只有当发送`EXIT_SIGNAL`时才会退出。

接下来，通过`receive_input`返回的迭代器作为`receiver`被捕获。这个流程通过进入一个循环来工作。在每次循环中，流程请求终端输入，将其发送到`greeter`流，然后运行`receiver.next()`以等待接收来自`greeter`的响应。

接着，运行此流程的终端用户可以输入字符串`q`或`quit`来退出。
当这种情况发生时，向`greeter`流发送一个退出信号以关闭它。

最后，将新的名字发送给`greeter`。`greeter`会返回一个问候语作为字符串。
当你收到问候语时，打印它并继续获取终端输入的循环。

### 完整示例

要使用`send_input`和`receive_input`的完整示例，这里是`greeter`和`sender`流程一起的样子：

```python
import asyncio
import sys
from prefect import flow, get_client
from prefect.blocks.system import JSON
from prefect.context import get_run_context
from prefect.deployments import run_deployment
from prefect.input.run_input import receive_input, send_input


EXIT_SIGNAL = "__EXIT__"


@flow
async def greeter():
    run_context = get_run_context()
    assert run_context.flow_run, "Could not see my flow run ID"

    block_name = f"{run_context.flow_run.id}-seen-ids"

    try:
        seen_keys_block = await JSON.load(block_name)
    except ValueError:
        seen_keys_block = JSON(
            value=[],
        )

    async for name_input in receive_input(
        str,
        with_metadata=True,
        poll_interval=0.1,
        timeout=None
    ):
        if name_input.value == EXIT_SIGNAL:
            print("Goodbye!")
            return
        await name_input.respond(f"Hello, {name_input.value}!")

        seen_keys_block.value.append(name_input.metadata.key)
        await seen_keys_block.save(
            name=block_name,
            overwrite=True
        )


@flow
async def sender():
    greeter_flow_run = await run_deployment(
        "greeter/send-receive", timeout=0, as_subflow=False
    )
    receiver = receive_input(str, timeout=None, poll_interval=0.1)
    client = get_client()

    while True:
        flow_run = await client.read_flow_run(greeter_flow_run.id)

        if not flow_run.state or not flow_run.state.is_running():
            continue

        name = input("What is your name? ")
        if not name:
            continue

        if name == "q" or name == "quit":
            await send_input(
                EXIT_SIGNAL,
                flow_run_id=greeter_flow_run.id
            )
            print("Goodbye!")
            break

        await send_input(name, flow_run_id=greeter_flow_run.id)
        greeting = await receiver.next()
        print(greeting)


if __name__ == "__main__":
    if sys.argv[1] == "greeter":
        asyncio.run(greeter.serve(name="send-receive"))
    elif sys.argv[1] == "sender":
        asyncio.run(sender())
```

为了运行这个示例，你需要配置一个安装了Prefect的Python环境，该环境应指向一个Prefect云账户或自托管的Prefect服务器实例。

在设置好环境后，在一个终端中启动流程运行器，使用以下命令：

```bash
python my_file_name greeter
```

For example, with Prefect Cloud, you should see output like this:

```bash
______________________________________________________________________
| Your flow 'greeter' is being served and polling for scheduled runs |
|                                                                    |
| To trigger a run for this flow, use the following command:         |
|                                                                    |
|         $ prefect deployment run 'greeter/send-receive'            |
|                                                                    |
| You can also run your flow via the Prefect UI:                     |
| https://app.prefect.cloud/account/...(a URL for your account)      |
|                                                                    |
______________________________________________________________________
```

然后在另一个终端中启动问候程序：

```bash
python my_file_name sender
```

You should see output like this:

```bash
11:38:41.800 | INFO    | prefect.engine - Created flow run 'gregarious-owl' for flow 'sender'
11:38:41.802 | INFO    | Flow run 'gregarious-owl' - View at https://app.prefect.cloud/account/...
What is your name?
```

输入名字并按下回车键，即可看到发送和接收的实际操作演示。

```bash
What is your name? andrew
Hello, andrew!
```

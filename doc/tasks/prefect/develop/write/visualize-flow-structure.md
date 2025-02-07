# 可视化流程结构
学习如何查看您的流程的整体结构。

使用其 `visualize()` 方法可以快速查看流程的结构。调用此方法会尝试生成流程和任务的示意图，而无需实际运行您的流程代码。


```{warning}
在调用`visualize()`函数时，位于流程或任务之外的函数和代码仍然会被执行。这可能会导致一些意外的结果。为了避免这种情况，请将您的代码放入任务中。
```

要使用`visualize()`方法，您必须在系统路径中安装 Graphviz。请从[graphviz download/](http://www.graphviz.org/download/)下载并安装Graphviz。

```{note}
仅仅安装`graphviz` Python包是不够的。
```

```python
from prefect import flow, task

@task(name="Print Hello")
def print_hello(name):
    msg = f"Hello {name}!"
    print(msg)
    return msg

@task(name="Print Hello Again")
def print_hello_again(name):
    msg = f"Hello {name}!"
    print(msg)
    return msg

@flow(name="Hello Flow")
def hello_world(name="world"):
    message = print_hello(name)
    message2 = print_hello_again(message)

if __name__ == "__main__":
    hello_world.visualize()
```

Prefect 无法自动为包含循环或 if/else 控制流的动态工作流生成图表。在这种情况下，您可以为任务提供模拟返回值以用于 `visualize()` 调用。

```python
from prefect import flow, task
@task(viz_return_value=[4])
def get_list():
    return [1, 2, 3]

@task
def append_one(n):
    return n.append(6)

@flow
def viz_return_value_tracked():
    l = get_list()
    for num in range(3):
        l.append(5)
        append_one(l)

if __name__ == "__main__":
    viz_return_value_tracked.visualize()
```

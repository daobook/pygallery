# 配置任务缓存

缓存指的是任务运行能够进入“已完成”状态，并在不实际执行定义该任务的代码的情况下返回预定值的能力。缓存让你能够高效地重用那些可能计算成本高昂的任务结果，并确保在因意外失败而重新尝试时，你的工作流保持幂等性。

默认情况下，Prefect的缓存逻辑基于以下任务调用的属性：
- 提供给任务的输入
- 任务的代码定义
- 当前的流程运行ID，或如果独立执行，则是当前任务运行 ID

这些值被哈希以计算任务的 [缓存键](cache-keys)。这意味着，默认情况下，在同一个流程中多次调用同一个任务且使用相同输入时，第一次之后的调用将产生缓存行为。这种行为可以配置 - 参见下文的[自定义缓存](https://docs.prefect.io/v3/develop/write-tasks#customizing-the-cache)。

````{admonition} **缓存需要结果持久化**
:class: warning
缓存需要结果持久化，这在默认情况下是关闭的。要为所有任务开启结果持久化，请使用`PREFECT_RESULTS_PERSIST_BY_DEFAULT`设置：

```
prefect config set PREFECT_RESULTS_PERSIST_BY_DEFAULT=true
```

有关管理结果配置的更多细节，请参阅[管理结果](https://docs.prefect.io/v3/develop/results)，以及有关管理Prefect设置的更多信息，请参阅[设置和配置文件](https://docs.prefect.io/v3/develop/settings-and-profiles)。
````

(cache-keys)=
## 缓存键

为了确定任务运行是否应该检索缓存状态，Prefect使用了称为“缓存键”的概念。
缓存键是一个计算得出的字符串值，它决定任务的返回值将被持久化存储在配置的结果存储中的哪个位置。
当一个任务开始运行时，Prefect首先计算它的缓存键，并使用这个键来查找任务结果存储中的记录。
如果找到了未过期的记录，这个结果会被返回，任务不会运行，而是进入一个带有相应结果值的`Cached`状态。

同一个任务在不同的流程中，甚至是不同的任务之间，只要它们共享一个公共的结果存储位置，就可以共享缓存键。

默认情况下，Prefect会将结果本地存储在`~/.prefect/storage/`目录中。
此目录中的文件名将与从您的任务运行中计算出的缓存键完全对应。

```{admonition} **与结果持久性的关系**
:class: warning

任务缓存和结果持久性密切相关。因为任务缓存依赖于加载已知的结果，所以只有当您的任务能够将其输出持久化到固定且已知的位置时，任务缓存才会起作用。

因此，任何明确避免结果持久性的配置都会导致您的任务永远不使用缓存，例如设置`persist_result=False`。
```

## 缓存策略

可以通过使用 _缓存策略_ 来配置缓存键的计算。
缓存策略是一种用于计算给定任务的缓存键的配方。

Prefect预先打包了一些常见的缓存策略：
- `DEFAULT`: 此缓存策略使用任务的输入、其代码定义以及当前的流程运行ID来计算任务的缓存键。
- `INPUTS`: 此缓存策略仅使用任务的输入来计算缓存键。
- `TASK_SOURCE`: 此缓存策略仅使用任务的代码定义来计算缓存键。
- `FLOW_PARAMETERS`: 此缓存策略仅使用提供给父流程运行的参数值来计算缓存键。
- `NONE`: 此缓存策略总是返回`None`，因此完全避免缓存和结果持久化。

这些策略可以通过在[任务装饰器](https://prefect-python-sdk-docs.netlify.app/prefect/tasks/#prefect.tasks.task)上使用`cache_policy`关键字来设置。

```python
from prefect import task
from prefect.cache_policies import TASK_SOURCE

import time


@task(cache_policy=TASK_SOURCE)
def my_stateful_task():
    print('sleeping')
    time.sleep(10)
    return 42

my_stateful_task() # sleeps
my_stateful_task() # does not sleep
```

No matter how many flows call it, this task will run once and only once until its underlying code is altered:

```python
@task(cache_policy=TASK_SOURCE)
def my_stateful_task():
    print('sleeping')
    time.sleep(10)

    # change the return value, for example
    return 43 

my_stateful_task() # sleeps again
```

## 自定义缓存

Prefect允许您以多种方式配置任务的缓存行为。

### 缓存过期

所有缓存键都可以通过[任务装饰器](https://prefect-python-sdk-docs.netlify.app/prefect/tasks/#prefect.tasks.task)上的`cache_expiration`关键字来选择性地指定一个_过期时间_。该关键字接受一个`datetime.timedelta`，用于指定缓存值应被视为有效的持续时间。
提供过期值会导致Prefect在任务结果记录旁边持久化一个过期时间戳。然后，这个过期时间将应用于_所有_可能共享此缓存键的其他任务。

### 缓存策略

可以使用基本的Python语法组合和修改缓存策略，以形成更复杂的策略。例如，除了`NONE`之外的所有任务策略都可以_合并_在一起，形成新的策略，这些策略结合了各个策略的逻辑，形成更大的缓存键计算。通过这种方式组合策略，使得缓存更容易失效。

例如：

```python
from prefect import task
from prefect.cache_policies import TASK_SOURCE, INPUTS
@task(cache_policy=TASK_SOURCE + INPUTS)
def my_cached_task(x: int):
    return x + 42
```

此任务将在您为 `x` 提供新值或更改底层代码时重新运行。

`INPUTS` 策略是一种特殊策略，它允许您通过减去字符串值来忽略特定的任务输入。

```python
from prefect import task
from prefect.cache_policies import INPUTS


my_custom_policy = INPUTS - 'debug'

@task(cache_policy=my_custom_policy)
def my_cached_task(x: int, debug: bool = False):
    print('running...')
    return x + 42


my_cached_task(1)
my_cached_task(1, debug=True) # still uses the cache
```

### 缓存键函数

您可以通过使用缓存键函数来配置自定义的缓存策略逻辑。
一个缓存键函数是一个接受两个位置参数的函数：
- 第一个参数对应于`TaskRunContext`，它存储任务运行元数据。例如，这个对象具有属性`task_run_id`、`flow_run_id`和`task`，所有这些都可以用于您的自定义逻辑中。
- 第二个参数对应于任务输入值的字典。例如，如果您的任务具有签名`fn(x, y, z)`，那么该字典将具有键“x”、“y”和“z”，相应的值可用于计算您的缓存键。

然后，可以使用[任务装饰器](https://prefect-python-sdk-docs.netlify.app/prefect/tasks/#prefect.tasks.task)上的`cache_key_fn`参数指定此函数。

例如：

```python
def static_cache_key(context, parameters):
    # return a constant
    return "static cache key"


@task(cache_key_fn=static_cache_key)
def my_cached_task(x: int):
    return x + 1
```

### 缓存存储

默认情况下，缓存记录与任务结果共处一地，含有任务结果的文件将包括用于缓存的元数据。
通过配置带有`key_storage`参数的缓存策略，可以使得缓存记录与任务结果分开存储。

当配置了缓存键存储时，持久化的任务结果只会包含你的任务返回值，而缓存记录可以被删除或修改，而不会影响你的任务结果。

你可以通过在一个缓存策略上使用带有`key_storage`参数的`.configure`方法来配置缓存记录的存储位置。
`key_storage`参数接受一个本地目录的路径或一个存储块。

例如：

```python
from prefect import task
from prefect.cache_policies import TASK_SOURCE, INPUTS

cache_policy = (TASK_SOURCE + INPUTS).configure(key_storage="/path/to/cache/storage")

@task(cache_policy=cache_policy)
def my_cached_task(x: int):
    return x + 42
```

此任务将在指定的目录中存储缓存记录。

若要将缓存记录存储在远程对象存储（例如S3）中，请传递存储块：

```python
from prefect import task
from prefect.cache_policies import TASK_SOURCE, INPUTS

from prefect_aws import S3Bucket

cache_policy = (TASK_SOURCE + INPUTS).configure(key_storage=S3Bucket.load("my-bucket"))

@task(cache_policy=cache_policy)
def my_cached_task(x: int):
    return x + 42
```

### 缓存隔离

缓存隔离控制并发任务运行与缓存记录的交互方式。Prefect支持两种隔离级别：`READ_COMMITTED` 和 `SERIALIZABLE`。

默认情况下，缓存记录以 `READ_COMMITTED` 的隔离级别操作。这保证了读取一个缓存记录时能够看到最新的已提交缓存值，但允许同一任务的多个执行同时发生。

考虑以下示例：

```python
from prefect import task
from prefect.cache_policies import INPUTS
import threading


cache_policy = INPUTS

@task(cache_policy=cache_policy)
def my_task_version_1(x: int):
    print("my_task_version_1 running")
    return x + 42

@task(cache_policy=cache_policy)
def my_task_version_2(x: int):
    print("my_task_version_2 running")
    return x + 43

if __name__ == "__main__":
    thread_1 = threading.Thread(target=my_task_version_1, args=(1,))
    thread_2 = threading.Thread(target=my_task_version_2, args=(1,))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()
```

在运行此脚本时，尽管两个任务使用相同的缓存键，但它们将并行执行并进行工作。

这一点可以通过在输出中同时看到“my_task_version_1 running”和“my_task_version_2 running”得到证实。

```bash
11:27:21.031 | INFO    | Task run 'my_task_version_2' - Created task run 'my_task_version_2' for task 'my_task_version_2'
11:27:21.032 | INFO    | Task run 'my_task_version_1' - Created task run 'my_task_version_1' for task 'my_task_version_1'
my_task_version_2 running
my_task_version_1 running
11:27:21.050 | INFO    | Task run 'my_task_version_2' - Finished in state Completed()
11:27:21.051 | INFO    | Task run 'my_task_version_1' - Finished in state Completed()
```

为了实现更严格的隔离，您可以使用`SERIALIZABLE`隔离级别。这确保了在给定的缓存记录上，通过锁定机制，一次只执行一个任务。

要配置隔离级别，请在缓存策略上使用带有`isolation_level`参数的`.configure`方法。当使用`SERIALIZABLE`时，您还必须提供一个实现了系统锁定逻辑的`lock_manager`。

以下是使用`SERIALIZABLE`隔离的更新示例：

```python
import threading

from prefect import task
from prefect.cache_policies import INPUTS
from prefect.locking.memory import MemoryLockManager
from prefect.transactions import IsolationLevel

cache_policy = INPUTS.configure(
    isolation_level=IsolationLevel.SERIALIZABLE,
    lock_manager=MemoryLockManager(),
)


@task(cache_policy=cache_policy)
def my_task_version_1(x: int):
    print("my_task_version_1 running")
    return x + 42


@task(cache_policy=cache_policy)
def my_task_version_2(x: int):
    print("my_task_version_2 running")
    return x + 43


if __name__ == "__main__":
    thread_1 = threading.Thread(target=my_task_version_1, args=(2,))
    thread_2 = threading.Thread(target=my_task_version_2, args=(2,))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()
```

在更新后的脚本中，只有一个任务会运行，另一个则会使用缓存的值。

这一点从输出中仅看到“my_task_version_1正在运行”或“my_task_version_2正在运行”中的一个即可证明。

```bash
11:34:00.383 | INFO    | Task run 'my_task_version_1' - Created task run 'my_task_version_1' for task 'my_task_version_1'
11:34:00.383 | INFO    | Task run 'my_task_version_2' - Created task run 'my_task_version_2' for task 'my_task_version_2'
my_task_version_1 running
11:34:00.402 | INFO    | Task run 'my_task_version_1' - Finished in state Completed()
11:34:00.405 | INFO    | Task run 'my_task_version_2' - Finished in state Cached(type=COMPLETED)
```

````{admonition} 在分布式环境中管理锁
:class: note
为了在分布式环境中管理锁，你需要使用所有执行基础架构都能访问的锁存储系统。

推荐使用 `prefect-redis` 提供的 `RedisLockManager`，结合共享的 Redis 实例：

```python
from prefect import task
from prefect.cache_policies import TASK_SOURCE, INPUTS
from prefect.transactions import IsolationLevel

from prefect_redis import RedisLockManager

cache_policy = (INPUTS + TASK_SOURCE).configure(
    isolation_level=IsolationLevel.SERIALIZABLE,
    lock_manager=RedisLockManager(host="my-redis-host"),
)

@task(cache_policy=cache_policy)
def my_cached_task(x: int):
    return x + 42
```
````

### 处理不可序列化对象

您可能会遇到无法（或不应）作为缓存键进行序列化的任务输入。处理这种情况有两种直接方法，这两种方法都基于同一理念。

您可以 **调整序列化逻辑**，仅对输入的某些属性进行序列化：

1. 使用自定义缓存键函数：
```python
from prefect import flow, task
from prefect.cache_policies import CacheKeyFnPolicy, RUN_ID
from prefect.context import TaskRunContext
from pydantic import BaseModel, ConfigDict

class NotSerializable:
    def __getstate__(self):
        raise TypeError("NooOoOOo! I will not be serialized!")

class ContainsNonSerializableObject(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    bad_object: NotSerializable

def custom_cache_key_fn(context: TaskRunContext, parameters: dict) -> str:
    return parameters["some_object"].name

@task(cache_policy=CacheKeyFnPolicy(cache_key_fn=custom_cache_key_fn) + RUN_ID)
def use_object(some_object: ContainsNonSerializableObject) -> str:
    return f"Used {some_object.name}"


@flow
def demo_flow():
    obj = ContainsNonSerializableObject(name="test", bad_object=NotSerializable())
    state = use_object(obj, return_state=True) # Not cached!
    assert state.name == "Completed"
    other_state = use_object(obj, return_state=True) # Cached!
    assert other_state.name == "Cached"
    assert state.result() == other_state.result()
```

2. 在你的输入类型上使用Pydantic的[自定义序列化](https://docs.pydantic.dev/latest/concepts/serialization/#custom-serializers)功能。
```python
from pydantic import BaseModel, ConfigDict, model_serializer
from prefect import flow, task
from prefect.cache_policies import INPUTS, RUN_ID

class NotSerializable:
    def __getstate__(self):
        raise TypeError("NooOoOOo! I will not be serialized!")

class ContainsNonSerializableObject(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    bad_object: NotSerializable

    @model_serializer
    def ser_model(self) -> dict:
        """Only serialize the name, not the problematic object"""
        return {"name": self.name}

@task(cache_policy=INPUTS + RUN_ID)
def use_object(some_object: ContainsNonSerializableObject) -> str:
    return f"Used {some_object.name}"

@flow
def demo_flow():
    some_object = ContainsNonSerializableObject(
        name="test",
        bad_object=NotSerializable()
    )
    state = use_object(some_object, return_state=True) # Not cached!
    assert state.name == "Completed"
    other_state = use_object(some_object, return_state=True) # Cached!
    assert other_state.name == "Cached"
    assert state.result() == other_state.result()
```
选择最适合您需求的方法：
- 当您希望在应用程序中保持一致的序列化时，使用Pydantic模型
- 当您需要为不同任务设置不同的缓存逻辑时，使用自定义缓存键函数

## 多任务缓存

在许多情况下，多个任务需要始终一起运行或根本不运行。
这可以通过在Prefect中配置这些任务总是在单一的[_事务_](https://docs.prefect.io/v3/develop/transactions)内写入它们的缓存来实现。

```python
from prefect import task, flow
from prefect.transactions import transaction


@task(cache_key_fn=lambda *args, **kwargs: "static-key-1")
def load_data():
    return "some-data"


@task(cache_key_fn=lambda *args, **kwargs: "static-key-2")
def process_data(data, fail):
    if fail:
        raise RuntimeError("Error! Abort!")

    return len(data)


@flow
def multi_task_cache(fail: bool = True):
    with transaction():
        data = load_data()
        process_data(data=data, fail=fail)
```

当使用默认参数值运行此流程时，它将在`process_data`任务上失败。
`load_data`任务将会成功。然而，由于只有在事务被提交时才会写入缓存，因此在`process_data`任务也成功之前，`load_data`任务不会将其结果写入到其缓存键位置。

这确保了每当需要重新运行此流程时，`load_data`和`process_data`都会被一起执行。
在成功执行后，两个任务的结果都会被缓存，直到缓存键被更新。
欲了解更多关于[事务]的信息，请参阅([/v3/develop/transactions](https://docs.prefect.io/v3/develop/transactions))。

## 缓存示例

在这个示例中，只要未达到`cache_expiration`的时间点，如果调用`hello_task()`时的输入保持不变，则会返回缓存的返回值。任务不会重新运行。然而，如果输入参数的值发生变化，`hello_task()`会使用新的输入执行。

```python 
from datetime import timedelta
from prefect import flow, task
from prefect.cache_policies import INPUTS
@task(cache_policy=INPUTS, cache_expiration=timedelta(days=1))
def hello_task(name_input):
    # Doing some work
    print("Saying hello")
    return "hello " + name_input

@flow(log_prints=True)
def hello_flow(name_input):
    hello_task(name_input)
    hello_task(name_input) # does not rerun
```

一个更实际的例子可能包括在缓存键中包含流程运行ID，这样只有在同一流程运行中的重复调用才会被缓存。

```python
from prefect.cache_policies import INPUTS, RUN_ID


@task(cache_policy=INPUTS + RUN_ID, cache_expiration=timedelta(days=1))
def hello_task(name_input):
    # Doing some work
    print("Saying hello")
    return "hello " + name_input


@flow(log_prints=True)
def hello_flow(name_input):
    # reruns each time the flow is run
    hello_task(name_input) 

    # but the same call within the same flow run is Cached
    hello_task(name_input) 
```

## 强制忽略缓存

"刷新"缓存指示Prefect忽略与任务的缓存密钥相关联的数据，并无论如何都重新运行。

`refresh_cache`选项为特定任务启用此行为。

```python
import random


def static_cache_key(context, parameters):
    # return a constant
    return "static cache key"


@task(cache_key_fn=static_cache_key, refresh_cache=True)
def caching_task():
    return random.random()
```

当此任务运行时，它总是更新缓存键而不是使用缓存值。当你有一个负责更新缓存的流程时，这特别有用。

要刷新所有任务的缓存，请使用`PREFECT_TASKS_REFRESH_CACHE`设置。将`PREFECT_TASKS_REFRESH_CACHE`设置为`true`会将所有任务的默认行为更改为刷新。这对于在不使用缓存结果的情况下重新运行流程非常有用。更多关于管理Prefect设置的细节，请参阅[设置](https://docs.prefect.io/v3/develop/settings-and-profiles)。

如果你有任务在启用此设置时不应该刷新，你可以明确地将`refresh_cache`设置为`False`。这些任务永远不会刷新缓存。如果存在缓存键，它将被读取，而不是更新。如果缓存键还不存在，这些任务仍然可以写入缓存。

```python
@task(cache_key_fn=static_cache_key, refresh_cache=False)
def caching_task():
    return random.random()
```

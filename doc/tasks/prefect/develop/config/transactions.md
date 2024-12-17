# 写事务

Prefect支持工作流中的 _事务性语义_，允许你在任务失败时回滚并配置作为原子单元运行的任务组。

在Prefect中，_事务_ 对应于需要完成的工作。一个事务最多运行一次，并在完成时根据动态计算的缓存键生成结果记录，该记录存储在唯一地址上。这些记录可以在任务和流程之间共享。

在幕后，每个 Prefect 任务运行都由事务控制。在默认的任务执行模式下，你需要了解有关事务的所有内容是[决定任务缓存键计算的策略](/v3/develop/task-caching)。

```{admonition} **事务和状态**
:class: tip

事务和状态相似但有重要区别。
事务确定任务是否应该执行，而状态则使代码执行状态可见。
```

## 编写你的第一个事务

任务可以通过使用 `transaction` 上下文管理器被组合成一个共同的事务：

```python
import os
from time import sleep

from prefect import task, flow
from prefect.transactions import transaction


@task
def write_file(contents: str):
    "Writes to a file."
    with open("side-effect.txt", "w") as f:
        f.write(contents)


@write_file.on_rollback
def del_file(transaction):
    "Deletes file."
    os.unlink("side-effect.txt")


@task
def quality_test():
    "Checks contents of file."
    with open("side-effect.txt", "r") as f:
        data = f.readlines()

    if len(data) < 2:
        raise ValueError("Not enough data!")


@flow
def pipeline(contents: str):
    with transaction():
        write_file(contents)
        sleep(2) # sleeping to give you a chance to see the file
        quality_test()


if __name__ == "__main__":
    pipeline(contents="hello world")
```

如果您运行这个流程 `pipeline(contents="hello world!")`，它会失败。重要的是，在流程退出后，您的工作目录中不会有 `"side-effect.txt"`文件。这是因为事务失败导致执行了 `write_file` 任务的 `on_rollback` 钩子。

```{admonition} on_rollback 钩子与 on_failure 钩子不同
:class: tip

请注意，当`quality_test`任务失败时（而不是它所关联的、已经成功的 `write_file` 任务），会执行 `on_rollback` 钩子。这是因为只要任务参与的事务失败，就会发生回滚，即使失败发生在任务的本地范围之外。这种行为使得事务成为管理管道失败的有价值的模式。
```

## 事务周期

每笔事务最多经历四个生命周期阶段：

- **开始**：在此阶段，计算并查找事务的键。如果键位置已存在记录，则事务认为自身已提交。
- **准备**：在此阶段，事务将数据片段准备到其结果位置。数据的提交或回滚取决于事务的提交模式。
- **回滚**：如果事务在准备之后遇到任何错误，它将自行回滚，不会进行任何提交。
- **提交**：在此最终阶段，事务将其记录写入配置的位置。此时，事务完成。

值得注意的是，回滚仅发生在事务准备之后。回顾上面的例子，实际上有三个事务在进行：
- 当执行`with transaction()`时开始的较大事务；此事务在整个子事务期间保持活跃。
- 与`write_file`任务关联的事务。完成`write_file`任务后，此事务现在处于**准备**状态。
- 与`quality_test`任务关联的事务。该事务在能够准备之前失败，导致其父事务回滚任何已准备的子事务。特别是，已准备的`write_file`事务被回滚。

````{admonition} 任务也有 on_commit 生命周期钩子
:class: tip
除了`on_rollback`钩子外，任务还可以注册`on_commit`钩子，这些钩子在其事务提交时执行。
任务运行仅在事务提交时持久化其结果，如果它在一个长时间运行的事务中，这可能显著晚于任务完成时间。

`on_commit`钩子的签名与`on_rollback`钩子相同：

```python
@write_file.on_commit
def confirmation(transaction):
    print("现在使用任务的缓存键提交记录！")
```
````

## 幂等性

通过将代码段包装在事务中，您可以确保这些代码段的功能是幂等的。通过指定事务的`key`，您可以确保您的代码只执行一次。

例如，以下是从 API 下载数据并将其写入文件的流程：

```python
from prefect import task, flow
from prefect.transactions import transaction


@task
def download_data():
    """Imagine this downloads some data from an API"""
    return "some data"


@task
def write_data(data: str):
    """This writes the data to a file"""
    with open("data.txt", "w") as f:
        f.write(data)


@flow(log_prints=True)
def pipeline():
    with transaction(key="download-and-write-data") as txn:
        if txn.is_committed():
            print("Data file has already been written. Exiting early.")
            return
        data = download_data()
        write_data(data)


if __name__ == "__main__":
    pipeline()
```

如果您运行此流程，它将在第一次运行时将数据写入文件，但因为交易已经提交，所以在后续的运行中它会提前退出。

给交易一个“键”将导致交易在提交时写入一条记录，表示交易已经完成。
调用`txn.is_committed()`只有在持久化记录存在的情况下才会返回`True`。

### 处理竞态条件

持续事务记录能够很好地确保顺序执行的操作是幂等的，但如果多个具有相同键的事务同时运行怎么办？

默认情况下，事务的隔离级别设置为`READ_COMMITED`，这意味着它们可以看到任何先前已提交的记录，但它们无法阻止覆盖在它们开始和提交之间由另一个事务创建的记录。

以下脚本展示了这一行为：

```python
import threading

from prefect import flow, task
from prefect.transactions import transaction


@task
def download_data():
    return f"{threading.current_thread().name} is the winner!"


@task
def write_file(contents: str):
    "Writes to a file."
    with open("race-condition.txt", "w") as f:
        f.write(contents)


@flow
def pipeline(transaction_key: str):
    with transaction(key=transaction_key) as txn:
        if txn.is_committed():
            print("Data file has already been written. Exiting early.")
            return
        data = download_data()
        write_file(data)


if __name__ == "__main__":
    # Run the pipeline twice to see the race condition
    transaction_key = f"race-condition-{uuid.uuid4()}"
    thread_1 = threading.Thread(target=pipeline, name="Thread 1", args=(transaction_key,))
    thread_2 = threading.Thread(target=pipeline, name="Thread 2", args=(transaction_key,))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()
```
    
如果你运行这个脚本，你会发现有时候文件会写入“线程 1 获胜！”，有时候会写入“线程 2 获胜！”
**即使事务具有相同的键**。你可以通过在每次运行时更改 `key` 参数来确保后续运行不会提前退出。

为了防止竞态条件，你可以将事务的 `isolation_level` 设置为 `SERIALIZABLE`。这将使每个事务对提供的键进行锁定。这将阻止其他事务在第一个事务完成之前开始。

以下是使用 `SERIALIZABLE` 隔离级别的更新示例：

```python
import threading
import uuid
from prefect import flow, task
from prefect.locking.filesystem import FileSystemLockManager
from prefect.results import ResultStore
from prefect.settings import PREFECT_HOME
from prefect.transactions import IsolationLevel, transaction


@task
def download_data():
    return f"{threading.current_thread().name} is the winner!"


@task
def write_file(contents: str):
    "Writes to a file."
    with open("race-condition.txt", "w") as f:
        f.write(contents)


@flow
def pipeline(transaction_key: str):
    with transaction(
        key=transaction_key,
        isolation_level=IsolationLevel.SERIALIZABLE,
        store=ResultStore(
            lock_manager=FileSystemLockManager(
                lock_files_directory=PREFECT_HOME.value() / "locks"
            )
        ),
    ) as txn:
        if txn.is_committed():
            print("Data file has already been written. Exiting early.")
            return
        data = download_data()
        write_file(data)


if __name__ == "__main__":
    transaction_key = f"race-condition-{uuid.uuid4()}"
    thread_1 = threading.Thread(target=pipeline, name="Thread 1", args=(transaction_key,))
    thread_2 = threading.Thread(target=pipeline, name="Thread 2", args=(transaction_key,))

    thread_1.start()
    thread_2.start()

    thread_1.join()
    thread_2.join()
```

要使用具有`SERIALIZABLE`隔离级别的事务，您还必须向`transaction`上下文管理器提供一个`lock_manager`。锁管理器负责获取和释放事务键上的锁。在上面的示例中，我们使用了一个`FileSystemLockManager`，它将在当前实例的文件系统上以文件形式管理锁。

Prefect为不同的并发用例提供了几种锁管理器：

| 锁管理器         | 存储方式     | 支持场景                       | 模块/包                |
|------------------|-------------|--------------------------------|-----------------------|
| `MemoryLockManager` | 内存        | 单进程工作流，使用线程          | `prefect.locking.memory` |
| `FileLockManager`   | 文件系统    | 单一机器上的多进程工作流        | `prefect.locking.filesystem` |
| `RedisLockManager`  | Redis数据库 | 分布式工作流                   | `prefect-redis`         |

## 在事务中访问数据

可以在事务中设置键值对，并在事务的其他部分访问它们，包括在`on_rollback`钩子中。

下面的代码展示了如何在事务中设置一个键值对，并在`on_rollback`钩子中访问它：

```python
import os
from time import sleep

from prefect import task, flow
from prefect.transactions import transaction


@task
def write_file(filename: str, contents: str):
    "Writes to a file."
    with open(filename, "w") as f:
        f.write(contents)


@write_file.on_rollback
def del_file(txn):
    "Deletes file."
    os.unlink(txn.get("filename"))


@task
def quality_test(filename):
    "Checks contents of file."
    with open(filename, "r") as f:
        data = f.readlines()

    if len(data) < 2:
        raise ValueError(f"Not enough data!")


@flow
def pipeline(filename: str, contents: str):
    with transaction() as txn:
        txn.set("filename", filename)
        write_file(filename, contents)
        sleep(2)  # sleeping to give you a chance to see the file
        quality_test(filename)


if __name__ == "__main__":
    pipeline(
        filename="side-effect.txt",
        contents="hello world",
    )
```

在`on_rollback`钩子中可以访问`contents`的值。

使用`get_transaction()`来获取事务对象，并通过`txn.get("key")`来获取键的值。
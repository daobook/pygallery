# 处理大数据

本页面探讨了使用Prefect处理大数据时，如何减少工作流的处理时间或内存使用量的方法，而无需编辑Python代码。有多种优化Python代码以提升速度、内存、计算和存储效率的选项，包括：

1. 使用`quote`移除任务内省以节省运行代码的时间。
2. 将任务结果写入云存储（如S3）以节省内存。
3. 在流程中保存数据到磁盘，而不是使用结果。
4. 缓存任务结果以节省时间和计算资源。
5. 压缩写入磁盘的结果以节省空间。
6. 使用[任务运行器](https://docs.prefect.io/v3/develop/task-runners)进行可并行操作以节省时间。

### 移除任务内省

当一个任务从流程中调用时，Prefect默认会检查每个参数。为了加快流程运行速度，可以通过包装参数并使用[`quote`](https://docs.prefect.io/latest/api-ref/prefect/utilities/annotations/#prefect.utilities.annotations.quote)来禁用此行为。

下面是一个基本示例，提取并转换了一些纽约出租车数据：

```python et_quote.py
from prefect import task, flow
from prefect.utilities.annotations import quote
import pandas as pd

@task
def extract(url: str):
    """提取数据"""
    df_raw = pd.read_parquet(url)
    print(df_raw.info())
    return df_raw

@task
def transform(df: pd.DataFrame):
    """基本转换"""
    df["tip_fraction"] = df["tip_amount"] / df["total_amount"]
    print(df.info())
    return df

@flow(log_prints=True)
def et(url: str):
    """ET管道"""
    df_raw = extract(url)
    df = transform(quote(df_raw))

if __name__ == "__main__":
    url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-09.parquet"
    et(url)
```

当传递的对象是大型集合（如字典或DataFrame）时，内省可能会花费大量时间，因为需要访问每个元素。使用`quote`可以减少执行时间，但会禁用对包装对象的依赖跟踪。

### 将任务结果写入云存储

默认情况下，任务运行的结果会存储在执行环境的内存中。这种方法对于小数据来说非常快，但对于大数据可能会带来问题。通过将结果写入磁盘来节省内存。

在生产环境中，建议将结果写入云提供商的存储，如AWS S3。Prefect允许你使用Prefect Cloud集成库（如[prefect-aws](https://docs.prefect.io/integrations/prefect-aws)）中的存储块来保存你的配置信息。了解更多关于[块](https://docs.prefect.io/v3/develop/blocks)的信息。

安装相关库，向服务器注册块类型并创建你的块，然后在流程中引用它：

```python
...
from prefect_aws.s3 import S3Bucket

my_s3_block = S3Bucket.load("MY_BLOCK_NAME")

...
@task(result_storage=my_s3_block)
```

任务的结果将写入S3，而不是存储在内存中。

### 在流程中保存数据到磁盘

为了在大数据处理中节省内存和时间，你不需要在任务之间传递结果。相反，可以直接在流程代码中读写数据到磁盘。Prefect为每个主要云提供商提供了集成库。

每个库都包含方便读取和写入云对象存储的块。

### 缓存任务结果

缓存可以节省时间和计算资源，因为它允许你避免不必要地重新运行任务。需要注意的是，缓存需要任务结果持久化。了解更多关于[缓存](https://docs.prefect.io/v3/develop/task-caching)的信息。

### 压缩写入磁盘的结果

如果你在使用Prefect的任务结果持久化，可以通过压缩结果来节省磁盘空间。指定结果类型时使用`compressed/`前缀：

```python
@task(result_serializer="compressed/json")
```

需要注意的是，压缩和解压缩数据都需要时间。

### 使用任务运行器进行可并行操作

Prefect的任务运行器允许你使用Dask和Ray Python库来并行运行任务，分布在多台机器上。这可以在处理大型数据结构时节省时间和计算资源。详见[Dask和Ray任务运行器的指南](https://docs.prefect.io/v3/develop/task-runners)。
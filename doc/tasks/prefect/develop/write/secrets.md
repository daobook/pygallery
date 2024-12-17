### 访问第三方密钥

凭证块和秘密块是存储和检索敏感信息的流行方式，这些信息用于连接第三方服务。
在Prefect Cloud中，这些块的值以加密格式存储，允许您使用Prefect安全地连接到第三方服务。

本示例与Snowflake数据库交互，并将连接所需的凭证存储在AWS Secrets Manager中。
本示例使用Prefect Cloud，并且通常适用于需要凭证的其他第三方服务。

## 前提条件

1. CLI已通过认证连接到您的[Prefect Cloud](https://app.prefect.cloud)账户
2. [Snowflake账户](https://www.snowflake.com/)
3. [AWS账户](https://aws.amazon.com/)

## 步骤

### 步骤1：安装`prefect-aws`和`prefect-snowflake`库

以下代码安装并升级必要的库及其依赖项：

```bash
pip install -U prefect-aws prefect-snowflake
```

### 第二步：在AWS Secrets Manager中存储Snowflake密码

访问[AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)控制台并创建一个新的密钥。
或者，可以使用AWS CLI或脚本来创建一个密钥。

1. 在用户界面中，选择**存储一个新密钥**。
2. 选择**其他类型的密钥**。
3. 输入Snowflake密码的键值对，其中键可以是任何字符串，而值是你的Snowflake密码。
4. 复制该键以备后用，然后点击**下一步**。
5. 输入你的密钥名称，复制该名称，然后点击**下一步**。
6. 对于本次演示，你不需要轮换密钥，所以点击**下一步**。
7. 点击**存储**。

### 第三步：创建`AwsSecret`块以访问你的Snowflake密码

使用Python代码或通过Prefect UI创建块。通过UI创建块可以帮助你可视化各个部分是如何组合在一起的。

在块页面上，点击**+**添加一个新块，并从块类型列表中选择**AWS Secret**。
为你的新块输入一个名称，并输入来自AWS Secrets Manager的密钥名称。

```{note}
如果使用自托管的Prefect服务器，你必须在安装新模块之前注册块类型，才能创建块。
```

```bash
prefect block register -m prefect_aws && prefect block register -m prefect_snowflake
```

### 步骤4：创建`AwsCredentials`区块

在**AwsCredentials**部分，点击**添加+**来创建一个AWS凭证区块。

**访问密钥ID**和**秘密访问密钥**的值是从计算环境中读取的。
具有读取AWS秘密权限的你的AWS**访问密钥ID**和**秘密访问密钥**值存储在你本地的`~/.aws/credentials`文件中，因此这些字段留空即可。
通过将这些属性留空，Prefect知道要查找计算环境。

在你的`AWSCredentials`区块中指定一个区域，而不是你本地的AWS配置文件。`AwsCredentials`区块具有优先级且更加便携。

在后台，Prefect使用AWS的`boto3`客户端来创建一个会话。

在表单的**AwsCredentials**部分，点击**添加+**并通过输入必要的值来创建一个AWS凭证区块。

如果计算环境包含必要的凭证，Prefect将按照[Boto3文档](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#configuring-credentials)所示的顺序使用它们进行身份验证。

以相同的顺序解析AWS区域。
在你的`AWSCredentials`区块中指定区域，以便无论本地AWS配置文件的内容如何——或者你是否在一个与秘密不同的区域运行代码——你的连接都能正常工作。

点击**创建**保存区块。

### 步骤5：确保计算环境能够访问AWS凭证

确保计算环境包含有授权访问AWS Secrets Manager的AWS凭证。
当你连接到Snowflake时，Prefect会自动使用这些凭证进行身份验证并访问包含Snowflake密码的AWS秘密。


### 步骤6：在Python代码中创建并使用`SnowflakeCredentials`和`SnowflakeConnector`块

利用Prefect提供的块来方便地访问Snowflake。
不要保存这些块，以确保凭据不会存储在Prefect Cloud中。

创建一个流程，该流程连接到Snowflake并调用两个任务。
第一个任务创建一个表并插入一些数据。
第二个任务读取数据。

```python
import json
from prefect import flow, task
from prefect_aws import AwsSecret
from prefect_snowflake import SnowflakeConnector, SnowflakeCredentials


@task
def setup_table(snow_connector: SnowflakeConnector) -> None:
    with snow_connector as connector:
        connector.execute(
            "CREATE TABLE IF NOT EXISTS customers (name varchar, address varchar);"
        )
        connector.execute_many(
            "INSERT INTO customers (name, address) VALUES (%(name)s, %(address)s);",
            seq_of_parameters=[
                {"name": "Ford", "address": "Highway 42"},
                {"name": "Unknown", "address": "Space"},
                {"name": "Me", "address": "Myway 88"},
            ],
        )


@task
def fetch_data(snow_connector: SnowflakeConnector) -> list:
    all_rows = []
    with snow_connector as connector:
        while True:
            new_rows = connector.fetch_many("SELECT * FROM customers", size=2)
            if len(new_rows) == 0:
                break
            all_rows.append(new_rows)
    return all_rows


@flow(log_prints=True)
def snowflake_flow():
    aws_secret_block = AwsSecret.load("my-snowflake-pw")

    snow_connector = SnowflakeConnector(
        schema="MY_SCHEMA",
        database="MY_DATABASE",
        warehouse="COMPUTE_WH",
        fetch_size=1,
        credentials=SnowflakeCredentials(
            role="MYROLE",
            user="MYUSERNAME",
            account="ab12345.us-east-2.aws",
            password=json.loads(aws_secret_block.read_secret()).get("my-snowflake-pw"),
        ),
        poll_frequency_s=1,
    )

    setup_table(snow_connector)
    all_rows = fetch_data(snow_connector)
    print(all_rows)


if __name__ == "__main__":
    snowflake_flow()
```

请填写您的Snowflake账户相关信息，并运行脚本。

```{note}
该流程从AWS Secret Manager中读取Snowflake密码，并在
`SnowflakeCredentials`模块中使用它。
```

`SnowflakeConnector`模块使用嵌套的`SnowflakeCredentials`模块来连接到Snowflake。
同样，Snowflake的模块都不会被保存，因此凭证不会存储在Prefect Cloud中。

有关与Snowflake合作更多示例，请参见[`prefect-snowflake`](https://docs.prefect.io/integrations/prefect-snowflake)。

## 下一步

现在，您可以将您的流程转化为[部署](https://docs.prefect.io/v3/deploy/infrastructure-examples/docker)，以便您和您的团队可以按计划远程运行它，响应事件或手动操作。

请确保在工作池或部署中指定`prefect-aws`和`prefect-snowflake`依赖项，以便在运行时可用。

同时，确保您的计算资源具有适当的AWS凭证，以访问AWS Secrets Manager中的秘密。

您已经看到了如何使用Prefect块来存储非敏感配置，并从环境中获取敏感配置值。您可以使用这种模式连接到需要凭证的其他第三方服务，例如数据库和API。您可以使用任何秘密管理器的类似模式，或者将其扩展到与环境变量一起工作。
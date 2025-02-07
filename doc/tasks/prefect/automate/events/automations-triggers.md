# 在事件上触发操作

自动化使您能够配置在满足 [触发器](#triggers) 条件时自动执行的 [操作](#actions)。

潜在的触发器包括流运行状态变化的事件——或此类事件的缺失。您可以定义自己的自定义触发器，以基于在 Python 代码中定义的 [事件](https://docs.prefect.io/v3/automate/events/custom-triggers/) 触发。使用 Prefect Cloud，您甚至可以创建 [Webhook](https://docs.prefect.io/v3/automate/events/webhook-triggers/)，用于接收数据以在操作中使用。

操作包括启动流运行、暂停计划和发送自定义通知。

## 创建自动化

在 **自动化** 页面上，选择 **+** 图标以创建新的自动化。系统将提示您配置：

- 导致自动化执行的 [触发器](#triggers) 条件。
- 自动化执行的一个或多个 [操作](#actions)。
- 自动化的 [详细信息](#details)，例如名称和描述。

## 管理自动化

**自动化** 页面提供了工作区中所有配置的自动化的概览。

![在 Prefect Cloud 中查看工作区的自动化。](https://docs.prefect.io/v3/img/ui/automations.png)

选择自动化旁边的切换按钮以暂停自动化的执行。

切换按钮旁边的按钮提供复制自动化 ID、编辑自动化或删除自动化的命令。

选择自动化的名称以查看其 **详细信息** 和相关 **事件**。

### 触发器

触发器指定应执行操作的条件。Prefect UI 包含许多常见条件的模板，例如：

- 流运行状态变化（流运行标签仅使用 `OR` 标准进行评估）
- 工作池状态
- 工作队列状态
- 部署状态
- 指标阈值，例如平均持续时间、延迟或完成百分比
- 自定义事件触发器

<Note>
**自动化 API**

[自动化 API](https://app.prefect.cloud/api/docs#tag/Automations) 使您能够基于任意 [事件](https://app.prefect.cloud/api/docs#tag/Events) 进一步定制触发器和操作策略。
</Note>

重要的是，您不仅可以配置对事件的反应触发器，还可以主动配置：在没有预期事件的情况下。

![在 Prefect Cloud 中配置自动化的触发器。](https://docs.prefect.io/v3/img/ui/automations-trigger.png)

例如，在流运行状态变化触发器的情况下，您可能期望生产流在不超过三十分钟内完成。但瞬态基础设施或网络问题可能会导致您的流在运行状态下“卡住”。如果流在运行状态下停留超过 30 分钟，触发器可以启动一个操作。

此操作可以针对流本身，例如取消或重新启动它。或者操作可以是通知某人采取手动补救步骤的形式。或者您可以设置在触发器发生时同时执行这两个操作。

### 操作

操作指定当触发器条件满足时自动化执行的操作。当前的操作类型包括：

- 取消流运行
- 暂停或恢复计划
- 运行部署
- 暂停或恢复部署计划
- 暂停或恢复工作池
- 暂停或恢复工作队列
- 暂停或恢复自动化
- 发送 [通知](#automation-notifications)
- 调用 Webhook
- 暂停流运行
- 更改流运行状态

![在 Prefect Cloud 中配置自动化的操作。](https://docs.prefect.io/v3/img/ui/automations-action.png)

### 在 Python 代码中创建自动化

您可以使用 Python SDK 的 `Automation` 类及其方法创建和访问任何自动化。

```python
from prefect.automations import Automation
from prefect.events.schemas.automations import EventTrigger
from prefect.events.actions import CancelFlowRun

# 创建自动化
automation = Automation(
    name="woodchonk",
    trigger=EventTrigger(
        expect={"animal.walked"},
        match={
            "genus": "Marmota",
            "species": "monax",
        },
        posture="Reactive",
        threshold=3,
    ),
    actions=[CancelFlowRun()],
).create()
print(automation)
# name='woodchonk' description='' enabled=True trigger=EventTrigger(type='event', match=ResourceSpecification(__root__={'genus': 'Marmota', 'species': 'monax'}), match_related=ResourceSpecification(__root__={}), after=set(), expect={'animal.walked'}, for_each=set(), posture=Posture.Reactive, threshold=3, within=datetime.timedelta(seconds=10)) actions=[CancelFlowRun(type='cancel-flow-run')] actions_on_trigger=[] actions_on_resolve=[] owner_resource=None id=UUID('d641c552-775c-4dc6-a31e-541cb11137a6')

# 读取自动化

automation = Automation.read(id=automation.id)
# 或者
automation = Automation.read(name="woodchonk")

print(automation)
# name='woodchonk' description='' enabled=True trigger=EventTrigger(type='event', match=ResourceSpecification(__root__={'genus': 'Marmota', 'species': 'monax'}), match_related=ResourceSpecification(__root__={}), after=set(), expect={'animal.walked'}, for_each=set(), posture=Posture.Reactive, threshold=3, within=datetime.timedelta(seconds=10)) actions=[CancelFlowRun(type='cancel-flow-run')] actions_on_trigger=[] actions_on_resolve=[] owner_resource=None id=UUID('d641c552-775c-4dc6-a31e-541cb11137a6')
```

### 选定和推断的操作目标

某些操作要求您选择操作的目标，或指定应推断操作的目标。选定的目标是简单且有用的，当您确切知道操作应作用于哪个对象时。例如，您想要运行的清理流或您想要发送的特定通知。

推断的目标是从触发器本身推断出来的。

例如，如果触发器在流运行卡在运行状态下触发，并且操作是取消推断的流运行——导致触发器触发的流运行。

类似地，如果触发器在工作队列事件上触发，并且相应的操作是暂停推断的工作队列，则推断的工作队列是发出事件的工作队列。

Prefect 尽可能推断相关事件，但有时不存在相关事件。

为自动化指定名称，并可选地指定描述。

## 使用部署触发器创建自动化

为了简化事件驱动部署的配置，Prefect 提供了部署触发器——一种简写方式，用于创建与特定部署链接的自动化，以基于事件的存在或缺失运行它们。

部署的触发器定义在 `prefect.yaml`、`.serve` 和 `.deploy` 中受支持。在部署时，指定的触发器定义创建由与您选择的 [语法](https://docs.prefect.io/v3/automate/events/events/#event-grammar) 匹配的事件触发的链接自动化。每个触发器定义可以包括一个 [Jinja 模板](https://en.wikipedia.org/wiki/Jinja_(template_engine)) 来将触发的 `event` 渲染为部署的流运行的 `parameters`。

### 在 `prefect.yaml` 中定义触发器

您可以在 `prefect.yaml` 文件中的任何部署中包含一个触发器列表：

```yaml
deployments:
  - name: my-deployment
    entrypoint: path/to/flow.py:decorated_fn
    work_pool:
      name: my-work-pool
    triggers:
      - type: event
        enabled: true
        match:
          prefect.resource.id: my.external.resource
        expect:
          - external.resource.pinged
        parameters:
          param_1: "{{ event }}"
```

此部署在从 `my.external.resource` 看到 `external.resource.pinged` 事件 _和_ `external.resource.replied` 事件时创建流运行：

```yaml
deployments:
  - name: my-deployment
    entrypoint: path/to/flow.py:decorated_fn
    work_pool:
      name: my-work-pool
    triggers:
      - type: compound
        require: all
        parameters:
          param_1: "{{ event }}"
        triggers:
          - type: event
            match:
              prefect.resource.id: my.external.resource
            expect:
              - external.resource.pinged
          - type: event
            match:
              prefect.resource.id: my.external.resource
            expect:
              - external.resource.replied
```

### 在 `.serve` 和 `.deploy` 中定义触发器

要在 Python 中创建带有触发器的部署，可以从 `prefect.events` 导入触发器类型 `DeploymentEventTrigger`、`DeploymentMetricTrigger`、`DeploymentCompoundTrigger` 和 `DeploymentSequenceTrigger`：

```python
from prefect import flow
from prefect.events import DeploymentEventTrigger


@flow(log_prints=True)
def decorated_fn(param_1: str):
    print(param_1)


if __name__=="__main__":
    decorated_fn.serve(
        name="my-deployment",
        triggers=[
            DeploymentEventTrigger(
                enabled=True,
                match={"prefect.resource.id": "my.external.resource"},
                expect=["external.resource.pinged"],
                parameters={
                    "param_1": "{{ event }}",
                },
            )
        ],
    )
```

与之前的示例一样，您必须使用一个底层触发器列表提供复合触发器：

```python
from prefect import flow
from prefect.events import DeploymentCompoundTrigger


@flow(log_prints=True)
def decorated_fn(param_1: str):
    print(param_1)


if __name__=="__main__":
    decorated_fn.deploy(
        name="my-deployment",
        image="my-image-registry/my-image:my-tag",
        triggers=[
            DeploymentCompoundTrigger(
                enabled=True,
                name="my-compound-trigger",
                require="all",
                triggers=[
                    {
                      "type": "event",
                      "match": {"prefect.resource.id": "my.external.resource"},
                      "expect": ["external.resource.pinged"],
                    },
                    {
                      "type": "event",
                      "match": {"prefect.resource.id": "my.external.resource"},
                      "expect": ["external.resource.replied"],
                    },
                ],
                parameters={
                    "param_1": "{{ event }}",
                },
            )
        ],
        work_pool_name="my-work-pool",
    )
```

### 将触发器传递给 `prefect deploy`

您可以将一个或多个 `--trigger` 参数作为 JSON 字符串或 `.yaml` 或 `.json` 文件的路径传递给 `prefect deploy`。

```bash
# 将触发器作为 JSON 字符串传递
prefect deploy -n test-deployment \
  --trigger '{
    "enabled": true,
    "match": {
      "prefect.resource.id": "prefect.flow-run.*"
    },
    "expect": ["prefect.flow-run.Completed"]
  }'

# 使用 JSON/YAML 文件传递触发器
prefect deploy -n test-deployment --trigger triggers.yaml
prefect deploy -n test-deployment --trigger my_stuff/triggers.json
```

例如，`triggers.yaml` 文件可以定义多个触发器：

```yaml
triggers:
  - enabled: true
    match:
      prefect.resource.id: my.external.resource
    expect:
      - external.resource.pinged
    parameters:
      param_1: "{{ event }}"
  - enabled: true
    match:
      prefect.resource.id: my.other.external.resource
    expect:
      - some.other.event
    parameters:
      param_1: "{{ event }}"
```

运行 `prefect deploy` 后，上述两个触发器都将附加到 `test-deployment`。

<Warning>
**传递给 `prefect deploy` 的触发器将覆盖 `prefect.yaml` 中定义的触发器**

虽然您可以为给定部署在 `prefect.yaml` 中定义触发器，但传递给 `prefect deploy` 的触发器优先于 `prefect.yaml` 中定义的触发器。
</Warning>

请注意，部署触发器计入工作区中自动化的总数。

## 使用自动化发送通知

自动化支持通过任何能够且配置为发送消息的预定义块发送通知，包括：

- 向 Slack 频道发送消息
- 向 Microsoft Teams 频道发送消息
- 向电子邮件地址发送电子邮件

![在 Prefect Cloud 中配置自动化的通知。](https://docs.prefect.io/v3/img/ui/automations-notifications.png)

## 使用 Jinja 模板

您可以通过 [Jinja](https://palletsprojects.com/p/jinja/) 语法访问自动化操作中的模板变量。模板变量使您能够动态包含自动化触发器的详细信息，例如流或池名称。

Jinja 模板变量语法将变量名称包裹在双大括号中，如下所示：`{{ variable }}`。

您可以访问底层流运行对象的属性，包括：

- [flow_run](https://prefect-python-sdk-docs.netlify.app/prefect/server/schemas/core/#prefect.server.schemas.core.FlowRun)
- [flow](https://prefect-python-sdk-docs.netlify.app/prefect/server/schemas/core/#prefect.server.schemas.core.Flow)
- [deployment](https://prefect-python-sdk-docs.netlify.app/prefect/server/schemas/core/#prefect.server.schemas.core.Deployment)
- [work_queue](https://prefect-python-sdk-docs.netlify.app/prefect/server/schemas/core/#prefect.server.schemas.core.WorkQueue)
- [work_pool](https://prefect-python-sdk-docs.netlify.app/prefect/server/schemas/core/#prefect.server.schemas.core.WorkPool)

除了其原生属性外，每个对象还包括一个 `id` 以及 `created` 和 `updated` 时间戳。

`flow_run|ui_url` 令牌返回在 UI 中查看流运行的 URL。

以下是与流运行状态相关的通知示例：

```
流运行 {{ flow_run.name }} 进入状态 {{ flow_run.state.name }}。

    时间戳：{{ flow_run.state.timestamp }}
    流 ID：{{ flow_run.flow_id }}
    流运行 ID：{{ flow_run.id }}
    状态消息：{{ flow_run.state.message }}
```

生成的 Slack Webhook 通知如下所示：

![在 Prefect Cloud 中配置自动化的通知。](https://docs.prefect.io/v3/img/ui/templated-notification.png)

您可以包含 `flow` 和 `deployment` 属性：

```
流运行 {{ flow_run.name }} 对于流 {{ flow.name }}
进入状态 {{ flow_run.state.name }}
带有消息 {{ flow_run.state.message }}

流标签：{{ flow_run.tags }}
部署名称：{{ deployment.name }}
部署版本：{{ deployment.version }}
部署参数：{{ deployment.parameters }}
```

一个报告工作池状态的自动化可能包括使用 `work_pool` 属性的通知：

```
工作池状态警报！

名称：{{ work_pool.name }}
最后轮询：{{ work_pool.last_polled }}
```

除了这些用于流、部署和工作池的快捷方式外，您还可以访问自动化和触发自动化的事件。有关更多详细信息，请参阅 [自动化 API](https://app.prefect.cloud/api/docs#tag/Automations)。

```
自动化：{{ automation.name }}
描述：{{ automation.description }}

事件：{{ event.id }}
资源：
{% for label, value in event.resource %}
{{ label }}：{{ value }}
{% endfor %}
相关资源：
{% for related in event.related %}
    角色：{{ related.role }}
    {% for label, value in related %}
    {{ label }}：{{ value }}
    {% endfor %}
{% endfor %}
```

请注意，此示例还展示了在模板通知时使用 Jinja 功能（如迭代器和 for 循环 [控制结构](https://jinja.palletsprojects.com/en/3.1.x/templates/#list-of-control-structures)）的能力。

## API 示例

此示例从 API 获取数据，并根据最终状态发送通知。

### 创建示例脚本

首先从端点提取假设的用户数据，然后执行数据清理和转换。

首先创建一个简单的提取方法，从随机用户数据生成器端点拉取数据：

```python
from prefect import flow, task, get_run_logger
import requests
import json

@task
def fetch(url: str):
    logger = get_run_logger()
    response = requests.get(url)
    raw_data = response.json()
    logger.info(f"原始响应：{raw_data}")
    return raw_data

@task
def clean(raw_data: dict):
    print(raw_data.get('results')[0])
    results = raw_data.get('results')[0]
    logger = get_run_logger()
    logger.info(f"清理结果：{results}")
    return results['name']

@flow
def build_names(num: int = 10):
    df = []
    url = "https://randomuser.me/api/"
    logger = get_run_logger()
    copy = num
    while num != 0:
        raw_data = fetch(url)
        df.append(clean(raw_data))
        num -= 1
    logger.info(f"构建了 {copy} 个名字：{df}")
    return df

if __name__ == "__main__":
    list_of_names = build_names()
```

数据清理工作流可以查看每个步骤，并将名字列表发送到管道的下一步。

### 在 UI 中创建通知块

接下来，根据完成状态结果发送通知。配置一个通知，显示何时查看工作流逻辑。

1. 在创建自动化之前，确认通知位置。创建一个通知块以帮助定义通知的发送位置。
![可用块列表](https://docs.prefect.io/v3/img/guides/block-list.png)

2. 导航到 UI 中的块页面，并点击创建电子邮件通知块。
![在 Cloud UI 中创建通知块](https://docs.prefect.io/v3/img/guides/notification-block.png)

3. 转到自动化页面以创建您的第一个自动化。
![自动化页面](https://docs.prefect.io/v3/img/guides/automation-list.png)

4. 接下来，找到触发器类型。在这种情况下，使用流完成触发器。
![触发器类型](https://docs.prefect.io/v3/img/guides/automation-triggers.png)

5. 创建触发器命中的操作。在这种情况下，创建一个通知以展示完成情况。
![自动化中的通知块](https://docs.prefect.io/v3/img/guides/notify-auto-block.png)

6. 现在自动化已准备好从流运行完成触发。在本地运行文件，并查看完成后通知发送到您的收件箱。通知可能需要几分钟才能到达。
![最终通知](https://docs.prefect.io/v3/img/guides/final-automation.png)

<Tip>
**无需创建部署**

您无需创建部署来触发自动化。在上面的例子中，流运行状态触发器在本地执行的流运行完成后触发。
</Tip>

现在您已经了解了如何从流运行完成创建电子邮件通知，请了解如何根据事件启动部署运行。

### 基于事件的部署自动化

创建一个自动化以启动部署而不是通知。探索如何使用 Prefect 的 REST API 以编程方式创建此自动化。

请参阅 [REST API 文档](https://docs.prefect.io/latest/api-ref/rest-api/#interacting-with-the-rest-api) 作为与自动化端点交互的参考。

创建一个部署，以基于流运行的时间启动一些工作。例如，如果 `build_names` 流执行时间过长，您可以启动一个带有相同 `build_names` 流的部署，但将 `count` 值替换为较低的数字以加快完成速度。

使用 `prefect.yaml` 文件或使用 `flow.deploy` 的 Python 文件创建部署。
<Tabs>
<Tab title="prefect.yaml">

    为我们的流 `build_names` 创建一个 `prefect.yaml` 文件，如下所示：

    ```yaml
      # 欢迎使用您的 prefect.yaml 文件！您可以使用此文件来存储和管理部署流代码的配置。我们建议将此文件与您的流代码一起提交到源代码控制中。

      # 有关此项目的通用元数据
      name: automations-guide
      prefect-version: 3.0.0

      # 构建部分允许您管理和构建 Docker 镜像
      build: null

      # 推送部分允许您管理是否以及如何将此项目上传到远程位置
      push: null

      # 拉取部分允许您提供在远程位置克隆此项目的说明
      pull:
      - prefect.deployments.steps.set_working_directory:
          directory: /Users/src/prefect/Playground/automations-guide

      # 部署部分允许您提供部署流的配置
      deployments:
      - name: deploy-build-names
        version: null
        tags: []
        description: null
        entrypoint: test-automations.py:build_names
        parameters: {}
        work_pool:
          name: tutorial-process-pool
          work_queue_name: null
          job_variables: {}
        schedule: null
    ```
  </Tab>

  <Tab title=".deploy">

    要遵循更基于 Python 的方法来创建部署，请使用 `flow.deploy`，如下例所示：

    ```python
    # .deploy 只需要一个名称、有效的工作池
    # 以及对流代码存在的引用

    if __name__ == "__main__":
    build_names.deploy(
        name="deploy-build-names",
        work_pool_name="tutorial-process-pool"
        image="my_registry/my_image:my_image_tag",
    )
    ```
  </Tab>
</Tabs>

从 CLI 获取此部署的 `deployment_id` 并将其嵌入到您的自动化中。

<Tip>
**从 CLI 查找 deployment_id**

在经过身份验证的命令提示符中运行 `prefect deployment ls`。
</Tip>

```bash
prefect deployment ls
                                          Deployments
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name                                                  ┃ ID                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Extract islands/island-schedule                       │ d9d7289c-7a41-436d-8313-80a044e61532 │
│ build-names/deploy-build-names                        │ 8b10a65e-89ef-4c19-9065-eec5c50242f4 │
│ ride-duration-prediction-backfill/backfill-deployment │ 76dc6581-1773-45c5-a291-7f864d064c57 │
└───────────────────────────────────────────────────────┴──────────────────────────────────────┘
```
创建一个自动化，使用 POST 调用以编程方式创建自动化。确保您有 `api_key`、`account_id` 和 `workspace_id`。

```python
def create_event_driven_automation():
    api_url = f"https://api.prefect.cloud/api/accounts/{account_id}/workspaces/{workspace_id}/automations/"
    data = {
        "name": "Event Driven Redeploy",
        "description": "Programmatically created an automation to redeploy a flow based on an event",
        "enabled": "true",
        "trigger": {
            "after": [
                "string"
            ],
            "expect": [
                "prefect.flow-run.Running"
            ],
            "for_each": [
                "prefect.resource.id"
            ],
            "posture": "Proactive",
            "threshold": 30,
            "within": 0
        },
        "actions": [
            {
                "type": "run-deployment",
                "source": "selected",
                "deployment_id": "YOUR-DEPLOYMENT-ID",
                "parameters": "10"
            }
        ],
        "owner_resource": "string"
    }

    headers = {"Authorization": f"Bearer {PREFECT_API_KEY}"}
    response = requests.post(api_url, headers=headers, json=data)

    print(response.json())
    return response.json()
```

运行此函数后，您将在 UI 中看到来自 POST 请求的更改。请记住，上下文在 UI 中是“自定义”的。

运行底层流并查看部署在 30 秒后启动。这将导致 `build_names` 的新流运行。您可以看到此新部署使用上述自定义参数启动。

通过几个快速更改，您可以以编程方式创建一个自动化，该自动化使用自定义参数部署工作流。

## 使用底层的 .yaml 文件

您可以通过使用自己的 .yaml 版本的自动化并将其注册到 UI 来进一步简化此操作。这通过在 .yaml 文件中声明自动化要求，然后使用 API 注册该 .yaml 文件来简化自动化的要求。

首先创建一个 .yaml 文件来存放自动化要求：

```yaml automation.yaml
name: Cancel long running flows
description: Cancel any flow run after an hour of execution
trigger:
  match:
    "prefect.resource.id": "prefect.flow-run.*"
  match_related: {}
  after:
    - "prefect.flow-run.Failed"
  expect:
    - "prefect.flow-run.*"
  for_each:
    - "prefect.resource.id"
  posture: "Proactive"
  threshold: 1
  within: 30
actions:
  - type: "cancel-flow-run"
```

创建一个辅助函数，使用 REST API 函数应用此 YAML 文件。

```python
import yaml

from myproject.utils import post, put

def create_or_update_automation(path: str = "automation.yaml"):
    """Create or update an automation from a local YAML file"""
    # Load the definition
    with open(path, "r") as fh:
        payload = yaml.safe_load(fh)

    # Find existing automations by name
    automations = post("/automations/filter")
    existing_automation = [a["id"] for a in automations if a["name"] == payload["name"]]
    automation_exists = len(existing_automation) > 0

    # Create or update the automation
    if automation_exists:
        print(f"Automation '{payload['name']}' already exists and will be updated")
        put(f"/automations/{existing_automation[0]}", payload=payload)
    else:
        print(f"Creating automation '{payload['name']}'")
        post("/automations/", payload=payload)

if __name__ == "__main__":
    create_or_update_automation()
```

在此示例中，您通过注册 .yaml 文件创建了自动化。

## 使用自定义 Webhook 启动自动化

{/*
<!-- vale off -->
*/}

使用 Webhook 公开事件 API。这使您能够扩展部署的功能并响应工作流中的更改。

{/*
<!-- vale on -->
*/}

通过公开 Webhook 端点，您可以从 HTTP 请求创建的事件启动触发部署的工作流。

在 UI 中创建此 Webhook 以创建这些动态事件。

```JSON
{
    "event": "model-update",
    "resource": {
        "prefect.resource.id": "product.models.{{ body.model_id}}",
        "prefect.resource.name": "{{ body.friendly_name }}",
        "run_count": "{{body.run_count}}"
    }
}
```

从该输入中，您可以创建一个公开的 Webhook 端点。

![webhook-simple](https://docs.prefect.io/v3/img/guides/webhook-simple.png)

每个 Webhook 对应一个创建的自定义事件，您可以使用单独的部署或自动化对其做出反应。

例如，您可以创建一个 curl 请求，发送端点信息，例如部署的运行计数：
```console
curl -X POST https://api.prefect.cloud/hooks/34iV2SFke3mVa6y5Y-YUoA -d "model_id=adhoc" -d "run_count=10" -d "friendly_name=test-user-input"
```

从这里，您可以创建一个连接到 curl 命令中拉取参数的 Webhook。它启动一个使用这些拉取参数的部署：
![Webhook created](https://docs.prefect.io/v3/img/guides/webhook-created.png)

进入事件源以直接从此事件自动化：
![Webhook automate](https://docs.prefect.io/v3/img/guides/webhook-automate.png)

这使您能够创建响应这些 Webhook 事件的自动化。通过 UI 中的几次点击，您可以将外部过程与 Prefect 事件 API 关联，该 API 可以触发下游部署。
![Automation custom](https://docs.prefect.io/v3/img/guides/automation-custom.png)

## 示例

### 使用事件触发下游部署

此示例展示了如何使用触发器在上游部署完成时调度下游部署。

```python event_driven_deployments.py
from prefect import flow, serve
from prefect.events import DeploymentEventTrigger


@flow(log_prints=True)
def upstream_flow():
    print("upstream flow")


@flow(log_prints=True)
def downstream_flow():
    print("downstream flow")


if __name__ == "__main__":
    upstream_deployment = upstream_flow.to_deployment(name="upstream_deployment")
    downstream_deployment = downstream_flow.to_deployment(
        name="downstream_deployment",
        triggers=[
            DeploymentEventTrigger(
                expect={"prefect.flow-run.Completed"},
                match_related={"prefect.resource.name": "upstream_deployment"},
            )
        ],
    )

    serve(upstream_deployment, downstream_deployment)
```

首先，启动 `serve` 进程以侦听计划的部署运行：

```bash
python event_driven_deployments.py
```

现在，运行上游部署并查看下游部署在其完成后启动：

```bash
prefect deployment run upstream-flow/upstream_deployment
```

<Tip>
**检查事件源**

您可以在 UI 中的事件源中检查原始事件，以查看可用于匹配的相关资源。

例如，以下 `prefect.flow-run.Completed` 事件的相关资源包括：
```json
{
   "related": [
    {
      "prefect.resource.id": "prefect.flow.10e099ec-8358-4146-b188-be68027ee58f",
      "prefect.resource.role": "flow",
      "prefect.resource.name": "upstream-flow"
    },
    {
      "prefect.resource.id": "prefect.deployment.be777bbd-4b15-49f3-bc1f-4d109374cee2",
      "prefect.resource.role": "deployment",
      "prefect.resource.name": "upstream_deployment"
    },
    {
      "prefect.resource.id": "prefect-cloud.user.80546602-9f31-4396-ab4b-e873a5377feb",
      "prefect.resource.role": "creator",
      "prefect.resource.name": "stoat"
    }
  ]
}
```
</Tip>

### 当客户完成订单时触发部署

想象一下，您正在运行一个电子商务平台，并且希望在客户完成订单时触发部署。

在您的平台上，订单期间可能会发生许多事件，例如：

- `order.created`
- `order.item.added`
- `order.payment-method.confirmed`
- `order.shipping-method.added`
- `order.complete`

<Tip>
**事件语法**

上述事件名称的选择是任意的。使用 Prefect 事件，您可以自由选择最能代表您用例的事件语法。
</Tip>

在这种情况下，我们希望在用户完成订单时触发部署，因此我们的触发器应：

- `expect` 一个 `order.complete` 事件
- `after` 一个 `order.created` 事件
- 为每个用户 ID 评估这些条件

最后，它应将 `user_id` 作为参数传递给部署。以下是代码中的样子：

```python post_order_deployment.py
from prefect import flow
from prefect.events.schemas.deployment_triggers import DeploymentEventTrigger

order_complete = DeploymentEventTrigger(
    expect={"order.complete"},
    after={"order.created"},
    for_each={"prefect.resource.id"},
    parameters={"user_id": "{{ event.resource.id }}"},
)


@flow(log_prints=True)
def post_order_complete(user_id: str):
    print(f"用户 {user_id} 已完成订单 -- 现在执行操作")


if __name__ == "__main__":
    post_order_complete.serve(triggers=[order_complete])
```

<Tip>
**指定多个事件或资源**

`expect` 和 `after` 字段接受事件名称的 `set`，因此您可以为每个条件指定多个事件。

同样，`for_each` 字段接受资源 ID 的 `set`。
</Tip>

要模拟用户导致订单状态事件，请在 Python shell 或脚本中运行以下内容：

```python simulate_events.py
import time
from prefect.events import emit_event

user_id_1, user_id_2 = "123", "456"
for event_name, user_id in [
    ("order.created", user_id_1),
    ("order.created", user_id_2), # 其他用户
    ("order.complete", user_id_1),
]:
    event = emit_event(
        event=event_name,
        resource={"prefect.resource.id": user_id},
    )
    time.sleep(1)
    print(f"{user_id} 发出 {event_name}")
```

在上面的示例中：

- `user_id_1` 创建并完成订单，触发我们的部署运行。
- `user_id_2` 创建订单，但没有发出完成事件，因此不会触发部署。

## 另请参阅

- 要了解有关 Prefect 事件的更多信息，这些事件可以触发自动化，请参阅 [事件文档](https://docs.prefect.io/v3/automate/events/events/)。
- 请参阅 [Webhook 指南](https://docs.prefect.io/v3/automate/events/webhook-triggers/) 以了解如何创建 Webhook 并接收外部事件。
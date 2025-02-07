# 通过事件跟踪活动

事件可以表示 API 调用、状态转换或执行环境或基础设施的变化。

事件支持多个功能，包括流运行日志和自动化。在 Prefect Cloud 中，事件支持 [审计日志](https://docs.prefect.io/v3/manage/cloud/manage-users/audit-logs)。

事件通过 [UI 中的事件源](#events-in-the-cloud-ui) 和通过 [自动化](https://docs.prefect.io/v3/automate/events/automations-triggers/) 配置 Prefect 的反应性，使您能够观察到数据堆栈。

## 事件规范

事件遵循结构化的 [规范](https://app.prefect.cloud/api/docs#tag/Events)。


| 名称     | 类型   | 必填？    | 描述                                                                 |
| -------- | ------ | --------- | -------------------------------------------------------------------- |
| occurred | 字符串 | 是        | 事件发生的时间                                                       |
| event    | 字符串 | 是        | 发生的事件名称                                                       |
| resource | 对象   | 是        | 此事件涉及的主要资源                                                 |
| related  | 数组   | 否        | 与此事件相关的其他资源的列表                                         |
| payload  | 对象   | 否        | 描述事件发生情况的开放式数据集                                       |
| id       | 字符串 | 是        | 客户端提供的事件标识符                                               |
| follows  | 字符串 | 否        | 已知在此事件之前发生的事件的 ID                                      |

## 事件语法

事件具有一致且信息丰富的语法：事件描述了资源及其对该资源采取的行动——或对该资源采取的行动。例如，Prefect 对象发出的事件采用以下形式：

```
prefect.block.write-method.called
prefect-cloud.automation.action.executed
prefect-cloud.user.logged-in
```

## 事件源

Prefect 对象会自动发出事件，包括流、任务、部署、工作队列和日志。Prefect 发出的事件包含 `prefect` 或 `prefect-cloud` 资源前缀。您还可以通过经过身份验证的 HTTP 请求将事件发送到 Prefect 的 [事件 API](https://app.prefect.cloud/api/docs#tag/Events)。

### 从 Python 代码发出自定义事件

Prefect Python SDK 提供了一个 `emit_event` 函数，当调用时会发出一个 Prefect 事件。您可以在任务或流内部或外部调用 `emit_event`。例如，运行此代码会向 Prefect API 发出一个事件，该 API 会验证并摄取事件数据：

```python
from prefect.events import emit_event


def some_function(name: str="kiki") -> None:
    print(f"hi {name}!")
    emit_event(event=f"{name}.sent.event!", resource={"prefect.resource.id": f"coder.{name}"})


if __name__ == "__main__":
  some_function()
```

`emit_event` 需要两个参数：`event`，事件的名称，和 `resource={"prefect.resource.id": "my_string"}`，资源 ID。

要将数据放入事件中以用于自动化操作，请为 `payload` 参数指定一个值字典。

### 通过 Webhook 发出事件

Prefect Cloud 提供 [可编程 Webhook](https://docs.prefect.io/v3/automate/events/webhook-triggers/)，以接收来自其他系统的 HTTP 请求，并将其转换为工作区中的事件。Webhook 可以发出 [预定义的静态事件](https://docs.prefect.io/v3/automate/events/webhook-triggers/#static-webhook-events)、[使用传入 HTTP 请求部分的动态事件](https://docs.prefect.io/v3/automate/events/webhook-triggers/#dynamic-webhook-events)，或来自 [CloudEvents](https://docs.prefect.io/v3/automate/events/webhook-triggers/#accepting-cloudevents) 的事件。

## 资源

每个事件都有主要资源，描述发出事件的对象。资源用作事件源的准稳定标识符，并构造为点分隔的字符串。例如：

```
prefect-cloud.automation.5b9c5c3d-6ca0-48d0-8331-79f4b65385b3.action.0
acme.user.kiki.elt_script_1
prefect.flow-run.e3755d32-cec5-42ca-9bcd-af236e308ba6
```

资源可以选择性地具有其他任意标签，这些标签可用于事件聚合查询。例如：

```json
"resource": {
    "prefect.resource.id": "prefect-cloud.automation.5b9c5c3d-6ca0-48d0-8331-79f4b65385b3",
    "prefect-cloud.action.type": "call-webhook"
    }
```

事件可以选择性地包含相关资源，用于将事件与其他资源关联。例如，主要资源可以对另一个资源执行操作或与之交互。以下是相关资源的示例：

```json
"resource": {
    "prefect.resource.id": "prefect-cloud.automation.5b9c5c3d-6ca0-48d0-8331-79f4b65385b3.action.0",
    "prefect-cloud.action.type": "call-webhook"
  },
"related": [
  {
      "prefect.resource.id": "prefect-cloud.automation.5b9c5c3d-6ca0-48d0-8331-79f4b65385b3",
      "prefect.resource.role": "automation",
      "prefect-cloud.name": "webhook_body_demo",
      "prefect-cloud.posture": "Reactive"
  }
]
```

## UI 中的事件

Prefect UI 提供了交互式仪表板，用于分析和处理在工作区中发生的事件源页面上的事件。

![事件源](https://docs.prefect.io/v3/img/ui/event-feed.png)

事件源是查看、搜索和过滤事件以了解整个堆栈活动的主要位置。每个条目显示资源、相关资源和发生的事件的数据。

通过点击事件查看更多信息。您将看到事件的资源、相关资源及其有效负载的完整详细信息。

## 响应事件

从事件页面，您可以配置一个 [自动化](https://docs.prefect.io/v3/automate/events/automations-triggers/)，以在观察到匹配事件时触发——或匹配事件的缺失——通过点击溢出菜单中的自动化按钮：

![从事件自动化](https://docs.prefect.io/v3/img/ui/automation-from-event.png)

默认触发器配置每次看到具有匹配资源标识符的事件时都会触发。可以通过 [自定义触发器](https://docs.prefect.io/v3/automate/events/custom-triggers/) 进行高级配置。

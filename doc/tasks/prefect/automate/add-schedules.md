# 调度流程运行

Prefect允许你指定流程的运行调度。
你可以为任何[已服务或已部署的流程](https://docs.prefect.io/v3/deploy/run-flows-in-local-processes)添加一个或多个调度。
调度告诉 Prefect 何时以及如何创建新的流程运行。
你可以在 Prefect UI 中、通过 CLI 使用 `prefect deployment schedule` 命令，或者在 `prefect.yaml` 配置文件中给已部署的流程添加调度。

## 创建时间表

有几种方式可以为部署创建时间表：

- 通过 Prefect UI
- 如果使用 [`serve` 方法](https://docs.prefect.io/v3/develop/write-flows#serving-a-flow)构建部署，则可以通过 `cron`、`interval` 或 `rrule` 参数来创建 `Flow` 对象或[`serve`工具](https://docs.prefect.io/v3/develop/write-flows#serving-multiple-flows-at-once)以同时管理多个流程
- 如果使用基于[工作者的部署](https://docs.prefect.io/v3/deploy/infrastructure-concepts/workers)
  - 当你用 `flow.serve` 或 `flow.deploy` 定义部署时
  - 通过交互式 `prefect deploy`命令
  - 在 `prefect.yaml` 文件的 `deployments` -> `schedules`部分

### 在 UI 中创建调度

你可以在UI中的**部署**页面的**调度**部分添加调度。
要添加时间表，请选择 **+ Schedule** 按钮。
选择 **间隔** 或 **Cron** 来创建调度。

```{admonition} 关于RRule？
:class: tip
UI不支持创建RRule时间表。
然而，UI将显示你通过命令行创建的RRule时间表。
```

新创建的时间表将出现在你创建它的**部署**页面上。
新的计划流程运行可以在**部署**页面的**即将到来**选项卡中看到。

要编辑现有时间表，请从**部署**页面上的时间表旁边的三点菜单中选择**编辑**。

### 使用 Python 创建调度

在 Python 文件中，通过 `flow.serve()`、`serve`、`flow.deploy()` 或 `deploy` 创建部署时，可以指定调度。只需添加关键字参数 `cron`、`interval` 或 `rrule` 即可。

| 参数       | 描述                                                                                                                                                                                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `interval` | 执行部署的时间间隔。接受一个数字或timedelta对象来创建一个单一计划。如果给定一个数字，则解释为秒。也接受一个数字或timedelta的可迭代对象来创建多个计划。                                                                                               |
| `cron`     | 一个cron计划字符串，用于指定何时运行此部署的运行。还接受一个cron计划字符串的可迭代对象来创建多个计划。                                                                                                                                                  |
| `rrule`    | 一个rrule计划字符串，用于指定何时运行此部署的运行。还接受一个rrule计划字符串的可迭代对象来创建多个计划。                                                                                                                                           |
| `schedules`| 定义何时运行此部署的计划对象列表。用于定义多个计划或额外的调度选项，如`timezone`。                                                                                                                                                                  |
| `schedule` | 定义何时运行此部署的计划对象。用于定义额外的调度选项，如`timezone`。                                                                                                                                                                           |

下面 `serve` 方法将创建名为 `my_flow` 的部署，并使用 cron 计划每分钟创建一次运行：

```python
from prefect import flow

from myproject.flows import my_flow

my_flow.serve(name="flowing", cron="* * * * *")
```

如果采用基于工作池的部署方式，`deploy` 方法具有相同的基于调度的参数。

当 `my_flow` 按照此 interval 调度运行时，它将从 2026 年 1 月 1 日午夜开始，在 `America/Chicago` 时区每10分钟运行一次。

```python
from datetime import timedelta, datetime
from prefect.client.schemas.schedules import IntervalSchedule

from myproject.flows import my_flow

my_flow.serve(
  name="flowing",
  schedules=[
    IntervalSchedule(
      interval=timedelta(minutes=10),
      anchor_date=datetime(2026, 1, 1, 0, 0),
      timezone="America/Chicago"
    )
  ]
)
```

### 在终端中创建调度

您可以通过交互式的 `prefect deploy` 命令来创建调度。系统会提示您选择要创建的调度类型。

### 在 YAML 中创建调度

如果你保存了 `prefect deploy` 命令生成的 `prefect.yaml` 文件，你会发现它包含用于部署的 `schedules` 部分。
或者，你也可以根据配方或从头开始创建 `prefect.yaml` 文件，并向其中添加 `schedules` 部分。

```yaml
deployments:
  ...
  schedules:
    - cron: "0 0 * * *"
      timezone: "America/Chicago"
      active: false
    - cron: "0 12 * * *"
      timezone: "America/New_York"
      active: true
    - cron: "0 18 * * *"
      timezone: "Europe/London"
      active: true
```

## 调度类型

Prefect 支持三种类型的调度：

- 对于已经熟悉 `cron` 的用户来说，[`Cron`](#cron)是最为合适的。
- [`Interval`](#interval)最适合那些以某种一致的节奏运行的部署，这种节奏与绝对时间无关。
- [`RRule`](#rrule)最适合依赖日历逻辑的部署，它适用于简单的循环计划、不规则间隔、排除项或月中某日调整。

```{admonition} 调度可处于非激活状态
:class: tip

当您创建或编辑计划时，可以在 Python 中将 `active` 属性设置为 `False`（或者在 YAML 文件中设置为 `false`），以停用该调度。
这一功能有助于保留调度配置，同时临时阻止调度生成新的流程运行。
```

(cron)=
### Cron

你可以使用[`cron`](https://en.wikipedia.org/wiki/Cron)模式来指定调度。你还可以提供时区，以执行夏令时（DST）的行为。

Prefect 使用 [`croniter`](https://github.com/kiorky/croniter) 来指定具有类似 `cron` 格式的日期时间迭代。

```{admonition} 支持的 croniter 功能
:class: tip

虽然Prefect支持大多数 `croniter` 功能来创建类似 `cron` 的调度，但它不支持 "R" 随机或 "H" 哈希关键词表达式，或者那些表达式可能实现的时间表抖动。
```

`cron` 属性包括：

| 属性         | 描述                                                                                                                 |
| ------------ | ---------------------------------------------------------------------------------------------------------------- |
| cron         | 有效的 `cron` 字符串。（必需的）                                                                                    |
| day_or       | 布尔值，指示 `croniter` 如何处理 `day` 和 `day_of_week` 条目。默认值为 `True`。                                        |
| timezone     | 时区的字符串名称。（查看[IANA时区数据库](https://www.iana.org/time-zones)以获取有效时区。）                     |

#### `day_or` 属性的工作原理

`day_or` 属性默认为 `True`，与 `cron` 的行为一致。

在此模式下，如果您指定了一个月中的某一天（`day`）和一周中的某一天（`day_of_week`），则计划将在指定的月日和周日均执行一次流程。

`day_or` 中的 `"or"` 指的是这两个条目被视为逻辑 "OR" 语句。计划应包括两者，就像 SQL 语句中的那样：

```sql
SELECT * FROM employees WHERE first_name = 'Ford' OR last_name = 'Prefect';
```

例如，当 `day_or` 设置为 `True` 时，cron 计划表达式 `* * 3 1 2` 将在每月的第三天以及每年一月（即一年的第一个月）的星期二（一周中的第二天）每分钟执行一次流程。

当 `day_or` 设置为 `False` 时，“日”（指月份中的日期）和 “星期几” 的条目会通过更为严格的 `AND` 逻辑操作符连接起来，正如 SQL 语句中所示：

```sql
SELECT * from employees WHERE first_name = 'Zaphod' AND last_name = 'Beeblebrox';
```

例如，当`day_or`设置为`False`时，相同的计划表将在1月的**第三个星期二**每分钟运行一次。
这种行为与`fcron`相符，而非`cron`。

```{admonition} 夏令时考虑事项
:class: note

如果`timezone`遵守夏令时，那么计划表会相应地进行调整。

夏令时的`cron`规则基于计划时间而非间隔。这意味着每小时的`cron`计划会在每个新的计划小时触发一次，而不是每过一个小时触发一次。
例如，当时钟向后调一小时时，这将导致计划出现两小时的暂停，因为计划将在第一次到达凌晨1点和120分钟后的凌晨2点各触发一次。

更长的计划，例如每天早上9点触发的计划，会自动调整以适应夏令时。
```

(interval)=
### Interval

`Interval` 调度器会以秒为单位定期创建新的流程运行。这些间隔是根据可选的 `anchor_date` 来计算的。

```yaml
schedule:
  interval: 600
  timezone: America/Chicago
```

`Interval` 属性包括：

| 属性        | 描述                                                                                                                                                                               |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| interval    | 表示流运行之间时间的 `datetime.timedelta`。（必填）                                                                                                                                |
| anchor_date | 表示开始或“锚点”日期以开始计划的 `datetime.datetime`。如果没有提供 `anchor_date`，则使用当前的 UTC 时间。                                                                          |
| timezone    | 时区的字符串名称，用于强制执行本地化行为，如夏令时边界。（有关有效时区，请参阅 [IANA 时区数据库](https://www.iana.org/time-zones)。）                                              |

`anchor_date` 并不表示计划的“开始时间”，而是用于计算间隔的固定点。
如果锚点日期在未来，则计划日期通过从锚点日期减去 `interval` 来计算。
在这个示例中，您导入了 [Pendulum](https://pendulum.eustace.io/) Python 包，以便于日期时间操作。
Pendulum 不是必需的，但它是一个指定日期的有用工具。

```{admonition} 夏令时注意事项
:class: note 

如果计划的 `anchor_date` 或 `timezone` 提供了遵循夏令时的时区，则计划会自行适当调整。
大于 24 小时的间隔将遵循夏令时惯例，而小于 24 小时的间隔将遵循 UTC 间隔。

例如，每小时计划将在每个 UTC 小时触发，即使在夏令时边界也是如此。当时间被拨回时，这会导致两次运行 _看起来_ 被安排在本地时间的 1 点，尽管它们在 UTC 时间上相差一小时。

对于较长的间隔，如每日计划，间隔计划会调整夏令时边界，以便时钟小时保持不变。
这意味着一个总是在上午 9 点触发的每日计划将遵循夏令时，并在本地时区继续在上午 9 点触发。
```

(rrule)=
### RRule

`RRule` 调度支持 [iCal 重复规则](https://icalendar.org/iCalendar-RFC-5545/3-8-5-3-recurrence-rule.html)（RRules），它提供了方便的语法来创建重复的计划。计划可以按频率从每年到每分钟重复。

`RRule` 使用 [dateutil rrule](https://dateutil.readthedocs.io/en/stable/rrule.html) 模块来指定 iCal 重复规则。

RRules 适用于任何类型的日历日期操作，包括简单的重复、不规则的间隔、排除、工作日或每月的日期调整等。RRules 可以表示复杂的逻辑，例如：

- 每个月的最后一个工作日
- 11 月的第四个星期四
- 每周的每隔一天

`RRule` 属性包括：

| 属性     | 描述                                                                                                                                                          |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| rrule    | RRule 计划的字符串表示。有关语法，请参阅 [`rrulestr` 示例](https://dateutil.readthedocs.io/en/stable/rrule.html#rrulestr-examples)。                             |
| timezone | 时区的字符串名称。有关有效时区，请参阅 [IANA 时区数据库](https://www.iana.org/time-zones)。                                                                   |

您可能会发现使用 RRule 字符串生成器（如 [iCalendar.org RRule 工具](https://icalendar.org/rrule-tool.html)）来帮助创建有效的 RRules 很有用。

```yaml
schedule:
  rrule: 'FREQ=WEEKLY;BYDAY=MO,WE,FR;UNTIL=20240730T040000Z'
```

```{admonition} RRule 限制
:class: note

`rrulestr` 支持的最大字符长度为 6,500 个字符

`COUNT` 不受支持。请使用 `UNTIL` 或 `/deployments/{id}/runs` 端点来安排固定数量的流运行。
```

```{admonition} 夏令时注意事项
:class: note

作为面向日历的标准，`RRules` 对初始时区很敏感。
一个在夏令时感知开始日期下每天上午 9 点的计划，会在夏令时边界内保持本地时间上午 9 点。一个在 UTC 开始日期下每天上午 9 点的计划，会保持 UTC 时间上午 9 点。
```

## 调度的工作原理

Prefect 的 `Scheduler` 服务会评估每个部署的计划，并适当地创建新的运行。它在运行 `prefect server start` 时自动启动，并且是 Prefect Cloud 的内置服务。

`Scheduler` 会创建满足以下约束的最少运行次数，按顺序：

- 最多安排 100 次运行。
- 运行不会安排在超过 100 天后的未来。
- 至少安排三次运行。
- 运行将安排到至少一小时后的未来。

这些行为可以通过 `prefect config view --show-defaults` 命令的相关设置进行调整：

```bash
PREFECT_API_SERVICES_SCHEDULER_DEPLOYMENT_BATCH_SIZE='100'
PREFECT_API_SERVICES_SCHEDULER_ENABLED='True'
PREFECT_API_SERVICES_SCHEDULER_INSERT_BATCH_SIZE='500'
PREFECT_API_SERVICES_SCHEDULER_LOOP_SECONDS='60.0'
PREFECT_API_SERVICES_SCHEDULER_MIN_RUNS='3'
PREFECT_API_SERVICES_SCHEDULER_MAX_RUNS='100'
PREFECT_API_SERVICES_SCHEDULER_MIN_SCHEDULED_TIME='1:00:00'
PREFECT_API_SERVICES_SCHEDULER_MAX_SCHEDULED_TIME='100 days, 0:00:00'
```

请参阅 [设置文档](https://docs.prefect.io/v3/develop/settings-and-profiles) 以获取有关更改设置的更多信息。

这些设置意味着，如果部署有一个每小时的计划，默认设置将创建接下来四天（或 100 小时）的运行。如果它有一个每周的计划，默认设置将维持接下来的 14 次运行（最多 100 天后的未来）。

```{admonition} Scheduler 不影响执行
:class: tip

Prefect 的 `Scheduler` 服务仅创建新的流运行并将它们置于 `Scheduled` 状态。它不参与流或任务的执行。
```

如果您更改了计划，之前安排的尚未开始的流运行将被删除，并创建新的安排流运行以反映新的计划。

要删除流部署的所有安排运行，您可以删除该计划。

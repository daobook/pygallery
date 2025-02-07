# 执行以下 shell 命令

本页面解释了如何使用`watch`和`serve` Prefect CLI命令来执行和调度shell命令作为Prefect流程，包括如何：

- 使用`watch`按需运行shell命令作为Prefect流程
- 使用`serve`将shell命令调度为定期执行的Prefect流程

## `watch`命令
`watch`命令将任何shell命令包装在一个Prefect流程中以即时执行。这对于快速任务或将shell脚本集成到工作流中非常有用。

### 示例用法
要使用`curl`命令获取芝加哥当前的天气情况，请使用以下Prefect CLI命令：

```bash
prefect shell watch "curl http://wttr.in/Chicago?format=3"
```

该命令向`wttr.in`发出请求，这是一个面向控制台的天气服务，并打印芝加哥的天气状况。

### `watch`的好处
- **立即反馈**：在Prefect框架内执行shell命令以获得即时结果。
- **易于集成**：将外部脚本或数据获取集成到您的数据工作流中。
- **可见性和日志记录**：使用Prefect的日志记录来跟踪shell任务的执行和输出。

## 使用`serve`部署
为了按计划运行shell命令，`serve`命令创建了一个由Prefect提供的定期执行的部署[部署](https://docs.prefect.io/v3/deploy/infrastructure-examples/docker)。这是创建由Prefect提供服务的部署的一种快捷方式。

### 示例用法
要在上午9点设置一个每日的芝加哥天气预报，请使用以下`serve`命令：

```bash
prefect shell serve "curl http://wttr.in/Chicago?format=3" --flow-name "Daily Chicago Weather Report" --cron-schedule "0 9 * * *" --deployment-name "Chicago Weather"
```

该命令安排一个Prefect流程每天获取芝加哥的天气情况，提供一致的更新而无需手动干预。要手动获取芝加哥天气，请从UI或CLI创建新部署的运行。

要关闭服务器并暂停计划中的运行，请在CLI中按`ctrl` + `c`。

### `serve`的好处
- **自动调度**：安排shell命令自动运行，确保关键更新及时生成并提供。
- **集中式工作流管理**：在Prefect内部管理和监控计划中的shell命令，以获得统一的工作流概览。
- **可配置的执行**：自定义执行频率、[并发限制](https://docs.prefect.io/v3/develop/global-concurrency-limits)和其他参数，以满足项目的需求和资源。}}
# claude-proxy-rules

Claude（claude.ai 网页、Claude 桌面端、Claude Code）用到的域名分流规则，支持 mihomo / Clash、Clash Verge Rev、Surge、Loon、Shadowrocket。

很多订阅自带的 AI 规则只覆盖 `claude.ai`、`anthropic.com` 这几个主域名，漏掉的域名会落到兜底的 `MATCH` / `FINAL`。兜底策略组的出口跟 AI 分组往往不一样，结果是页面加载慢、Artifact 打不开、登录验证转圈，或者同一个会话从两个 IP 出去。这份规则把 Claude 自己用到的域名收齐，统一走你的 AI 策略组。

## 收录了什么

| 分类 | 域名 | 用途 |
|---|---|---|
| 官方 | `anthropic.com` `claude.ai` `claude.com` `claudeusercontent.com` | 主站、API、静态资源 |
| 官方 | `claude.site` | 已发布的 Artifact 页面 |
| 官方 | `claudemcpcontent.com` `claudemcpclient.com` | 连接器（MCP）应用沙盒 |
| 监控 | `browser-intake-datadoghq.com` `browser-intake-us5-datadoghq.com` `us5.datadoghq.com` `datadoghq-browser-agent.com` | Datadog 前端监控与日志上报 |
| 监控 | `growthbook.io` | 功能开关 |
| 监控 | `o1158394.ingest.us.sentry.io` | Anthropic 的 Sentry 错误上报 |
| 客服 | `intercom.io` `intercomcdn.com` | 在线客服 |
| 验证 | `challenges.cloudflare.com` `hcaptcha.com` | 登录、注册时的人机验证 |
| 付款 | `stripe.com` `stripe.network` `stripecdn.com` | 订阅付款 |

完整列表见 [`rules/claude.list`](rules/claude.list)。

> 监控类域名连不上也不影响使用。收进来是为了让同一会话的所有请求都从同一个出口出去。

## 用法

下面的 `PROXY` 换成你配置里实际的策略组名，比如 `🤖 AI`。

### mihomo / Clash（rule-provider）

```yaml
rule-providers:
  claude:
    type: http
    behavior: classical
    format: yaml
    url: https://raw.githubusercontent.com/windery/claude-proxy-rules/main/dist/clash/claude.yaml
    path: ./ruleset/claude.yaml
    interval: 86400

rules:
  - RULE-SET,claude,PROXY
  # ……放在 GEOIP / MATCH 之前
```

也有 text 格式：`dist/clash/claude.txt`（`format: text`）。

### Clash Verge Rev

两种方式选一种：

1. **引用远程规则集，自动更新**：把 [`dist/clash-verge/merge.yaml`](dist/clash-verge/merge.yaml) 的内容粘到「订阅 → 全局扩展覆写配置（Merge）」，或者某个订阅右键「编辑规则 / 扩展覆写配置」。
2. **直接内联，不依赖网络拉取**：订阅右键 →「编辑规则」，把 [`dist/clash-verge/prepend-rules.yaml`](dist/clash-verge/prepend-rules.yaml) 里的 `prepend` 列表粘进去。

改完点订阅页右上角的「重新激活订阅」，然后到「规则」页确认这些规则排在最前面。

### Surge / Loon / Shadowrocket

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/windery/claude-proxy-rules/main/dist/surge/claude.list,PROXY
```

### 不支持远程规则集的客户端

比如 Mesl 这类只有「自定义规则」界面的客户端：按 `rules/claude.list` 逐条添加，类型照抄，出口选 AI 策略组，选「前置添加」，让它们优先于订阅规则。

## 域名是怎么找出来的

- 从 Claude Desktop（2.19675.0）的 `app.asar` 和 Claude Code（2.1.285）二进制里提取引用的域名；
- 在浏览器里打开 claude.ai（登录前和登录后），记录实际发出的请求；
- 去掉文档链接、第三方连接器（Google、Slack、Linear 等，这些按各自服务走自己的规则）和公共 CDN（jsdelivr、cdnjs、unpkg，Artifact 会用到，但它们是很多网站共用的，不适合绑到 AI 策略组）。

如果发现有遗漏，欢迎提 Issue 或 PR。最好附上客户端「连接」页面里显示走了兜底规则的那条请求。

## 修改与生成

只改 `rules/claude.list`（格式是 `类型,值`，不带策略组），然后运行：

```bash
python3 scripts/build.py
```

`dist/` 下的所有文件都会重新生成，提交时一起提交。

## License

[MIT](LICENSE)

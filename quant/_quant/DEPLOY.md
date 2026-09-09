# 手动部署：GitHub Pages + 聚宽主动同步

这套方案不需要自有服务器或公网 endpoint。聚宽使用 GitHub API 上传日志批次，GitHub Actions 解析后发布静态看板，地址为 https://amazingmorning.github.io/quant/ 。原博客仍在网站首页。

当前仅准备好本地代码，尚未上传或部署。正式数据区为空；页面的“演示数据”开关展示虚构样例。旧的本地回测日志没有放进发布包。

## 1. 把网站包放到 GitHub 仓库

解压 `dist/github-pages-quant.zip`，或直接使用 `deployment/github-pages/` 中的文件。
打开 https://github.com/amazingmorning/amazingmorning.github.io ，选择现有的 `master` 分支。
按下表放到仓库根目录，**不要再套一层 github-pages 或 deployment 文件夹**：

| 本地包内路径 | GitHub 仓库内路径 | 用途 |
| --- | --- | --- |
| `quant/` 整个目录 | `quant/` | 已生成的网页、空数据索引和独立演示数据 |
| `_quant/` 整个目录 | `_quant/` | 日志解析器、网页源文件、测试和上传目录 |
| `.github/workflows/quant-pages.yml` | `.github/workflows/quant-pages.yml` | 上传后及每小时自动构建发布 |
| `_includes/nav.html` | `_includes/nav.html` | 替换同名文件，给博客导航添加“量化看板” |

不要把 ZIP 文件本身当成网页上传。可用 GitHub 网页的 **Add file → Upload files** 上传目录，提交到 `master`。
macOS Finder 中按 Command + Shift + . 可显示 `.github` 隐藏目录。
如果网页上传漏了隐藏目录，用 **Add file → Create new file**，文件名填写 `.github/workflows/quant-pages.yml`，填入包内对应文件的完整内容后提交。
GitHub 网页上传可能忽略隐藏的 `.gitkeep`；初次部署没有它也能构建，聚宽首次上传会自动建立子目录。
其余博客文件不用替换。提交前检查文件列表应包含 `quant/index.html`、`_quant/build_static.py` 和上述 workflow 文件。

## 2. 开启 Pages 自动发布

1. 仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
2. 打开 **Actions → Publish Blog and Quant Dashboard → Run workflow**，选择 `master` 后运行一次。
3. 等待 `build`、`deploy` 都成功，再访问 https://amazingmorning.github.io/quant/ 。
4. 初次显示“等待日志数据”是正常的；可切换演示数据检查页面布局。

工作流会用 Jekyll 构建整个原博客后发布，不会只发布看板而清空博客。不要添加 `.nojekyll`，不要把 Pages 发布目录单独改为 `quant/`。
如果 workflow 没出现在 Actions 中，先确认 `.github/workflows/quant-pages.yml` 路径和文件内容已完整提交。

## 3. 创建仅用于日志上传的 GitHub Token

在 GitHub 个人 **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token** 创建：

- Resource owner：`amazingmorning`。
- Repository access：**Only select repositories**，仅选 `amazingmorning.github.io`。
- Repository permissions：**Contents → Read and write**；保留默认的 Metadata 读取权限。
- 设置有效期，保存 token。到期需在聚宽配置文件中替换新 token。

该 token 仅需写入日志文件，不需要 Workflows 写权限。不要把它写进网页代码、公开仓库或 GitHub Issues。
如果 `master` 受分支保护限制直接写入，需让该上传凭证能向该分支写入日志，否则会上传失败。

## 4. 聚宽放置两个文件

解压 `dist/joinquant-github-sync.zip`，或使用 `deployment/joinquant/`。

| 文件 | 放到聚宽哪里 |
| --- | --- |
| `joinquant_four_strategies.py` | 策略编辑器中，整体替换现有四策略代码，保存并更新到对应模拟交易 |
| `dashboard_sync_config.json` | **投资研究的根目录**，与 `read_file('dashboard_sync_config.json')` 对应，替换之前上传的同名配置 |

这两个文件不放到公开网站仓库。策略文件包含完整四策略代码，不需要把上传函数再粘贴一遍。
保留已有企业微信平台配置。先用新代码回测检查策略，再更新模拟交易；回测不会向 GitHub 上传。

在研究目录的 JSON 文件中填入：

```json
{
  "enabled": true,
  "transport": "github",
  "owner": "amazingmorning",
  "repo": "amazingmorning.github.io",
  "branch": "master",
  "source_id": "four-strategies",
  "token": "这里替换成刚创建的真实 GitHub Token"
}
```

包内默认 `enabled: false`。填好 token 后再改为 `true`，保留合法 JSON 格式。
此模式不需要 `endpoint`，不要填写 `127.0.0.1` 或网站 `/quant/` 地址。
只给一个模拟盘使用此 `source_id`，不要让不同账户共用，以免混合持仓和资产。

## 5. 对照日志确认自动同步

仅聚宽 `sim_trade` 模拟交易上传：

- 09:00 盘前报告完成后上传盘前全文。
- 10:00 至 15:00 每个整点上传待发记录，含期间确认的成交。
- 15:01 收盘报告完成后上传，15:30 补发或重试。
- 没有新记录不发送；成交时只入队；失败保留批次，在下一次调度重试。

聚宽出现 `【看板同步】上传成功，本批 N 条记录` 后，GitHub 仓库应新增：

```text
_quant/inbox/four-strategies/交易日期/批次编号.json
```

每次新提交都会触发发布，此外每小时第 17 分钟会自动构建一次。GitHub 调度和构建可能排队延迟，不保证整点即时更新；公开仓库长期无活动时，GitHub 也可能暂停计划工作流，届时在 Actions 重新启用。
网页每小时刷新，打开期间每分钟检查一次已发布索引；也可点刷新按钮。
盘前、已确认买卖、收盘数据只有在策略实际生成后才会出现，不回补启用前的历史记录。
企业微信发送提示、平台全部调试日志及系统报错不属于本同步范围。

日志和生成的数据将随公开仓库公开，包括选股、交易和资产信息。认证 token 不会写进上传批次。

## 常见定位

- **聚宽提示上传失败**：核对 token 是否过期、Contents 写权限、仓库及 `master` 分支、平台能否连接 `api.github.com`。失败不会清空待发记录。
- **仓库已有 JSON，网页未更新**：查看 Actions 中最新运行的 build/deploy 是否成功；核对 Pages Source 是否为 GitHub Actions。
- **网页只有演示数据**：关掉演示开关；正式数据只来自启用上传后的真实模拟盘记录。
- **想暂停同步**：将研究目录 JSON 的 `enabled` 改为 `false`；如需暂停发布，可在 Actions 停用该 workflow。

本地已覆盖上传重试、批次去重、静态生成和浏览器交互验证；聚宽云端联网和 GitHub Actions 实际部署仍需按上面步骤验证。

官方参考：[GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)、[GitHub 文件上传 API](https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents)。

# Cloudflare 发布闭环与本机已验证的排障路径

适用：自有项目的 GitHub 发布，并且用户要求将网站上线到 Cloudflare；或维护已有 Pages 项目。单纯上传源码、软件或文档时，不自动创建网站。

## 正常发布顺序

1. 读取项目 AGENTS、部署配置、品牌标准和 brand.json。静态产物可用 Pages Direct Upload；需要后端的新项目先按真实运行时选型，不机械套用静态部署。
2. 用 scripts/sync_readme.py 复用二维码和企业服务区，保留项目正文。普通新项目继续链接华链企业服务，不能把品牌中心官网地址替换成新项目的应用地址。
3. 构建产物，明确项目名、分支和上传目录。只上传该项目公开交付内容，完整报价与凭据不进入发布目录。
4. 先将源码、必要公开资产、构建配置和部署说明提交到 GitHub。保留历史、可见范围以及用户未完成的其他修改。
5. 查询当前 Cloudflare 身份、账号与目标项目。不存在时创建一次，取得实际分配的域名；网络超时后先查询结果，不直接重复创建。
6. 按实际域名生成 canonical、分享地址、资源地址和 sitemap，再归档当前源码并发布。若有首次试发布，切换配置后最终从已提交源码再发布一次。
7. 检查正式域名和真实关键路径。有界面或托管变化时检查桌面/手机及相关交互；仅改 README 不重跑应用回归。
8. 更新本项目 README、体验入口和 GitHub 首页网址。只有企业官网迁移时，才更新品牌中心链接并同步受影响仓库；普通新项目不会改动其他项目的网址。

## 可复用脚本

中心在本机为 `D:/见舟品牌与发布中心`，其他机器先定位克隆的品牌中心。需要 Python 3 与 requests，依赖列在 scripts/requirements-publish.txt。

```powershell
python scripts/cloudflare_pages.py inspect --project-dir "项目目录" --project-name "项目名"
python scripts/cloudflare_pages.py ensure-project --project-dir "项目目录" --project-name "项目名"
python scripts/cloudflare_pages.py deploy --project-dir "项目目录" --project-name "项目名"
python scripts/cloudflare_pages.py verify --project-dir "项目目录" --project-name "项目名" --check-path "/实际关键路径/"
```

- inspect 只读；ensure-project 先查询，已有项目不重复创建。
- deploy 使用默认 dist 或 --directory 指定目录，不代替构建和 Git 提交；完成后检查正式入口。
- 多账号时传 --account-id。Wrangler 可通过 --wrangler、JIANZHOU_WRANGLER、项目依赖或 PATH 定位；本机的 E:/CodexTools/Cloudflare/wrangler.cmd 可直接复用。
- 脚本通过 Wrangler 的 auth token --json 在内存中取用现有授权，不显示或落盘令牌。不要直接向聊天或日志输出该命令的凭据。
- 普通项目没有宣传册或联系页面时，不套用华链官网的八条路径。

## 这次踩坑与处理顺序

| 现象 | 实际判断与处理 |
| --- | --- |
| 登录成功，创建返回 8000077 | 登录与邮箱校验分开判断。先核对工具邮箱与页面邮箱，并确认一次 verified 状态。用户已确认验证后，不再重复要求点击验证邮件。 |
| 页面已验证，CLI/MCP 仍拒绝 | 本次两条通道同样报错，读接口正常、写权限已具备。刷新一次发布授权，再用当前授权直接请求 API。若仍同一错误，记录账户状态矛盾，停止重复验证/登录循环，说明需要平台处理。 |
| 新授权下 API 创建成功 | 继续发布，不再卡在邮箱检查；不能断言根因一定是旧会话缓存或一定是后台延迟。 |
| CLI fetch failed、连接重置，Python API 同期正常 | 这是独立传输问题，不是邮箱或构建失败。使用下面实际验证的 relay 模式，不反复升级 CLI、更换 TLS 或随机切换网络参数。 |
| 临时新版 Wrangler 找不到 keyring | 本机依赖在 E 盘工具前缀。复用现有包装器，保留 XDG_CONFIG_HOME、XDG_CACHE_HOME、npm_config_prefix、NODE_PATH；无需为了绕过问题改成明文凭据。 |
| 本机 Node 复制静态目录崩溃 | 发生在原 Sites 打包链路，和页面内容无关。目标明确为 Pages 后直接上传现成静态目录，不再为旧平台反复打包。 |
| 从 PDF 抽图后黑底 | 原图带 SMask，单独抽颜色图丢失透明信息。合并原图与 SMask，保留原始品牌图。 |
| 重复复制 PDF 提示只读 | 副本继承了源属性。只处理自己的目标副本，不修改微信原文件。 |
| GitHub push TLS 握手失败 | 本地提交仍在。先确认远端状态，本次 HTTP/1.1、OpenSSL 或已知本机代理成功；按网络择一，不强推或删除历史。 |

## 本机上传中继：备用模式

当前环境已复现 Node 上传失败、Python 直接 API 正常时，直接复用：

```powershell
python scripts/cloudflare_pages.py deploy --project-dir "项目目录" --project-name "项目名" --transport relay
```

临时适配仅绑定本机回环地址，将 Wrangler 请求转发至 Cloudflare 官方 HTTPS API；账号、权限和邮箱校验仍由 Cloudflare 决定。只为子进程设置 API 地址和代理变量，完成或失败后自动关闭，不记录凭据。网站运行不依赖它。

正常网络环境使用 direct，不把这项本机故障变成所有项目的强制前置步骤。

## 授权与工具

已有 Wrangler 配置的项目沿用 Wrangler。复用有效登录，确实缺失时才发起官方交互登录。本次 Pages 授权使用 account:read、user:read、pages:write，保存在系统凭据保护中。

官方 Cloudflare 技能与 MCP 已安装，MCP 地址为 https://mcp.cloudflare.com/mcp 。工具暂不可见时可在下一次会话加载，不阻断已经可用的 Wrangler 流程。

用真实返回的域名作为上线证据，不提前把候选 pages.dev 地址写成可访问网址。参考当前官方文档与 CLI 帮助，尊重用户明确指定的部署方式。

## 完成与留档

报告正式网址、GitHub 留档、受影响仓库、验证结果和未完成项。保留旧仓库、旧版本、可见范围与部署说明，完整报价继续私有。

本次结果见品牌中心 docs/Cloudflare部署与迁移方案.md；本参考只存方法，不另存账号、微信号和公共网址副本。

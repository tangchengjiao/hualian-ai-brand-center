# 华链 AI 官网：Cloudflare Pages 部署与迁移说明

日期：2026-10-24　状态：已部署并完成生产页面检查。

## 正式入口

- 官网：https://hualian-ai.pages.dev
- 企业服务：https://hualian-ai.pages.dev/services/
- 服务参考价：https://hualian-ai.pages.dev/pricing/
- 企业宣传册：https://hualian-ai.pages.dev/brochure/
- 宣传册 PDF：https://hualian-ai.pages.dev/downloads/company-brochure.pdf
- 联系见舟：https://hualian-ai.pages.dev/contact/
- 品牌与项目资源：https://hualian-ai.pages.dev/brand/
- 微信二维码：https://hualian-ai.pages.dev/assets/contact/wechat-qr.png

## 实际部署方式

官网托管于 Cloudflare Pages，项目 `hualian-ai`，生产分支 `main`，发布目录 `dist/`，使用 Wrangler Direct Upload。无需部署到产品服务器，既有产品服务器未做修改。

GitHub 保留完整源码、已生成页面、公开资源和版本历史，当前推送 GitHub 本身不会自动部署。原 Sites 发布身份和历史作为归档保留，主要官网入口已经切换到 Cloudflare。

## 发布与验证结果

- 首次 Cloudflare 上传 22 个静态文件，返回部署成功。
- 正式主域名、微信二维码及公开宣传册 PDF 均返回 HTTP 200。
- 8 页、桌面和手机两种尺寸，共 16 个页面状态通过生产浏览器检查。
- 微信弹窗、关闭操作、复制咨询提纲、服务预选和手机菜单交互通过。
- 公开目录中的 PDF 只有企业宣传册，完整报价保留本地私有资料，未进入公开源码或部署。
- 各仓库联系方式从品牌中心配置生成，二维码与服务资料统一使用正式官网地址。

## 后续更新

1. 修改内容与品牌中心配置。
2. 使用 scripts/build_site.py 生成页面；需要切换域名时传入 --site-url。
3. 将当前源码和公开资源提交到 GitHub 留档。
4. 使用已授权的 Wrangler 将 dist/ 发布到 hualian-ai 的 main 分支。
5. 检查页面和资源；若地址变化，再同步品牌中心和各项目的统一联系区。

当前已具备自有域名接入基础；未来绑定自有域名后，可将域名作为长期公共入口，以后更换托管平台优先调整域名解析。

## 本次排障记录

最初 Cloudflare 创建项目接口拒绝邮箱验证状态。用户确认页面已验证后，重新取得 OAuth 授权并直接请求 API，创建成功；现有证据不能区分旧授权缓存与后端状态同步延迟。

本机 Node 上传客户端另外发生连接重置。本次临时使用仅绑定本机回环地址的传输适配，将 Wrangler 请求转发至 Cloudflare 官方 HTTPS API 后上传成功；适配过程不存储或记录凭据，完成后停止。该适配不属于网站运行依赖。

## 已沉淀的复用工具

本次方法已进入[发布技能参考](../skills/jianzhou-github-publish/references/cloudflare-release.md)和[统一标准](../统一发布标准.md)。[Pages 助手](../scripts/cloudflare_pages.py)可参数化查询身份与项目、按需创建、部署和检查链接；明确需要时用 --transport relay 复用本机备用传输，结束自动关闭。

本次工具验证包含三项离线行为检查：二进制上传透传且不记录凭据、子进程失败后关闭中继并保留调用者环境、已有项目不重复创建；另对现有 hualian-ai 项目做了只读检查，没有触发重建或重新部署。

## 官方参考

- Direct Upload：https://developers.cloudflare.com/pages/get-started/direct-upload/
- 自定义域名：https://developers.cloudflare.com/pages/configuration/custom-domains/

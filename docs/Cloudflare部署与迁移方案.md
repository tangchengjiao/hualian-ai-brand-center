# 华链 AI 官网：Cloudflare Pages 部署与迁移方案

日期：2026-10-24　状态：旧站方式已核对，迁移准备完成，尚未切换线上入口。

## 已核实的旧站部署方式

- GitHub 源码：https://github.com/tangchengjiao/jianzhou-ai-site 。
- 已有访问地址：https://jianzhou-ai-site.pages.dev 。本次匿名访问返回 HTTP 200，响应由 Cloudflare 提供。
- 仓库部署说明与本地交接一致：Cloudflare Pages 托管，使用 Wrangler CLI 上传构建目录；该项目未连接 Git Provider，因此 GitHub 推送不会自动部署。
- 这条路线不要求购买或运行自有服务器。

## 华链官网采用的路线

GitHub 保留完整源码、已生成静态文件、公开素材、宣传册、发布标准与部署说明；Cloudflare Pages 负责官网访问。以后更换服务器或平台，继续从 GitHub 重新部署，不删除仓库或历史。

第一阶段新建独立的华链官网 Pages 项目，不覆盖见舟个人站。项目名可先考虑 `hualian-ai`，最终名称和默认域名以 Cloudflare 实际返回值为准，不提前把候选网址写入各仓库。

网站目前是 8 页静态 HTML，无需额外数据库或常驻后端。发布目录为 `dist/`。本次不迁移或修改产品服务器上的应用。

Cloudflare Pages 提供托管与默认 `pages.dev` 地址，可以参考旧站使用；国内实际访问体验需要在新站上线后按真实网络确认，不将换域名等同于大陆节点加速。

## 切换时一起处理

1. 恢复 Cloudflare 账户的有效授权，查询现有项目，确定新项目的名称。
2. 通过本项目 `wrangler.jsonc` 所列静态目录部署，取得真实的 Cloudflare 地址。
3. 使用 `scripts/build_site.py --site-url 新地址` 生成规范链接、分享图片地址和 sitemap。保持二维码、图片、脚本、样式及公开宣传册由同一网站提供。
4. 检查 8 个页面、手机导航、微信弹窗、复制功能、二维码图片和宣传册下载。
5. 验证成功后更新品牌中心 `public/brand.json` 中的官网、企业服务、参考价、宣传册、咨询和二维码地址。
6. 将各自有仓库的统一联系区同步为新地址。二维码改用官网的 `/assets/contact/wechat-qr.png`，不再依赖 GitHub 原始图片地址作为主要展示来源。
7. GitHub 留存本次源码与发布说明。原有 Sites 身份和历史保留为旧发布记录，不作为新仓库的默认官网入口。

完整服务报价始终留在本地私有资料中，不进入 Cloudflare 上传目录、公开源码或宣传册下载列表。

## 自有域名与后续迁移

当前尚未确认企业域名，因此可以先用 Cloudflare 实际分配的默认地址上线。以后绑定自有域名后，将域名作为长期公共入口；未来更换托管平台时，优先调整域名解析，避免反复修改各项目的服务链接。

公开二维码和宣传册使用稳定路径；GitHub 继续保存这些公开资源的主副本与历史。

## 当前待完成事项

Wrangler 本次没有读取到可用的 Cloudflare 登录，查询项目时提示需要认证。此结果不能据此判断是账户失效还是本机登录上下文不可用；实际创建项目和部署前需完成一次有效授权。

目前没有创建新的 Pages 项目、切换现有域名或改动产品服务器。品牌中心和既有仓库仍保留当前可用链接，避免迁移尚未完成时出现空入口。

## 官方参考

- Cloudflare Pages 静态 HTML：https://developers.cloudflare.com/pages/framework-guides/deploy-anything/
- Cloudflare Pages 自定义域名：https://developers.cloudflare.com/pages/configuration/custom-domains/
- 已有个人站部署说明：https://github.com/tangchengjiao/jianzhou-ai-site#github--cloudflare-pages-部署

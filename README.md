# 华链 AI × 见舟 · 品牌与发布中心

统一维护品牌资料、联系二维码、企业宣传册与仓库发布标准，供当前及后续项目复用。

**[华链 AI 官网](https://hualian-ai.pages.dev)** · [企业服务](https://hualian-ai.pages.dev/services/) · [服务参考价](https://hualian-ai.pages.dev/pricing/) · [企业宣传册](public/downloads/company-brochure.pdf)

## 统一使用哪些资料

| 内容 | 位置 |
| --- | --- |
| 品牌、联系人及公共链接 | [品牌配置](public/brand.json) |
| Cloudflare 发布与踩坑 | [可复用手册](skills/jianzhou-github-publish/references/cloudflare-release.md) |
| Pages 发布助手 | [检查、创建、部署与验证](scripts/cloudflare_pages.py) |
| 备用传输与依赖 | [本机中继](scripts/cloudflare_transport.py) · [依赖](scripts/requirements-publish.txt) |
| 官网托管迁移 | [Cloudflare 部署方案](docs/Cloudflare部署与迁移方案.md) |
| 新项目接入和日常维护 | [统一发布标准](统一发布标准.md) |
| 可复用发布技能 | [技能定义](skills/jianzhou-github-publish/SKILL.md) |
| 本次发布记录 | [2026-10-24](docs/发布记录-2026-10-24.md) |
| 项目联系区 | [README 模板](templates/readme-footer.md) |
| 联系区同步 | [同步脚本](scripts/sync_readme.py) |
| 企业宣传册 | [公开 PDF](public/downloads/company-brochure.pdf) |

完整服务报价通过见舟微信获取，本公开仓库不提供原文下载。

## 联系二维码

| 微信 | 抖音 | 视频号 | 公众号 |
| :---: | :---: | :---: | :---: |
| ![微信](public/assets/contact/wechat-qr.png) | ![抖音](public/assets/contact/douyin-qr.png) | ![视频号](public/assets/contact/channels-qr.png) | ![公众号](public/assets/contact/official-account-qr.jpg) |
| DST10209 | 74683161410 | 见舟AI赋能 | 扫码关注 |

## 新仓库接入

**默认规则已固定：以后让 Codex 上传自有新项目到 GitHub，就会自动接入统一二维码和企业服务链接，无需再次提醒。**

1. 整理项目本身的介绍、使用方法与实际下载文件。
2. 读取本中心的品牌配置，复用统一联系区。
3. 检查二维码及官网、服务、参考价、宣传册链接，再按项目需要发布。

脚本支持 Python 3，仅使用标准库。默认预览，不修改项目：

```powershell
python scripts/sync_readme.py --repo "目标项目目录"
python scripts/sync_readme.py --repo "目标项目目录" --apply
```

微信号或链接文字更新后，重新同步目标仓库。图片使用固定公共地址，更新同名图片后各引用方随缓存刷新取得新图。

## 软件交付

源码和文档进项目仓库；Windows 安装包、Mac DMG 及交付 ZIP 放在对应项目 Releases，README 开头提供清晰入口。

品牌名称、二维码和企业资料用于华链 AI 与见舟的自有项目及合作展示，不意味着转让品牌或第三方素材权利。

<!-- JIANZHOU-PUBLIC-INFO:START -->
## 企业服务与联系

**华链 AI** · 企业 AI 业务落地与内生能力建设

培训与 FDE 培养 · 场景验证 · 智能体定制 · 企业实施 · 产品应用支持

[华链 AI 官网](https://hualian-ai.pages.dev) · [企业服务](https://hualian-ai.pages.dev/services/) · [服务参考价](https://hualian-ai.pages.dev/pricing/) · [企业宣传册](https://hualian-ai.pages.dev/downloads/company-brochure.pdf) · [合作咨询](https://hualian-ai.pages.dev/contact/)

咨询联系人：**见舟** · 微信：**`DST10209`**

<img src="https://hualian-ai.pages.dev/assets/contact/wechat-qr.png" alt="见舟微信二维码" width="200">

抖音：`74683161410` · 视频号：见舟AI赋能
<!-- JIANZHOU-PUBLIC-INFO:END -->

# 📊 Weibo MCN Data Radar (微博 MCN 商业数据雷达)

![Version](https://img.shields.io/badge/Version-v1.3.0--Ultimate_Pro-blue?style=flat-square)
![Update](https://img.shields.io/badge/Update-2026--03--03-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Supported-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-orange?style=flat-square)

## 💡 项目简介
本项目是一个基于 **Docker + Playwright** 架构构建的商业级数据采集与分析引擎。专为 MCN 机构和商业博主调研设计，旨在穿透微博重度单页应用 (SPA) 的动态渲染壁垒，实现微博基础运营数据与 **WEIQ 商业底库**（CPM、图文报价、转发报价）的跨平台自动化对齐。

## 🚀 核心特性
* **双轨数据交叉验证**: 独创双轨采集逻辑，同时调度微博主站与 WEIQ 黄金接口，利用 UID 降维打击，确保在主站限流时依然能获取 100% 精准的商业数据。
* **沉浸式多模态大盘**: 全站统一采用 Apple/Vercel 级高斯模糊 (Glassmorphism) 设计。内置 Echarts 雷达图与散点图，并首创 AI 自动化商业策略简报生成。
* **WAF 穿透防护**: 动态伪装 WebDriver 特征，自动挂载持久化 Cookie 环境，完美避开 403 屏蔽与无头浏览器白屏风控。
* **容器化一键部署**: 深度适配 Windows WSL2 环境，基于 Docker Compose 实现“代码+数据库+环境”的一键式秒级拉起。

## 🛠️ 技术栈
* **后端 (Backend)**: Python 3.10 / FastAPI / Playwright (Async)
* **前端 (Frontend)**: 原生 HTML5 / CSS3 / Echarts (Apple 风格空间便当盒面板)
* **存储 (Database)**: PostgreSQL 15
* **基础设施 (Infra)**: Docker / Docker Compose / Debian 12 (Bookworm)

## 📋 版本历史

### v1.3.0 Ultimate Pro (2026-03-03) - 空间沉浸与多模态全景重构版 🌌
* **[UI/UX 跃迁]**：全面重构交互引擎，全站统一采用 Vercel/Apple 级高斯模糊 (Glassmorphism) 与防滚穿透锁。新增数据请求“动态呼吸灯”与“打字机”数字滚动动效，呈现顶级 SaaS 质感。
* **[多模态大盘重塑]**：新增“矩阵多模态全景洞察”沉浸式工作台。内置 Echarts 价值散点图与直发/转发效能雷达图，首创 **AI 自动化商业策略简报** 生成。
* **[底层黑科技突破]**：针对 WEIQ 图表数据的重度加密防御，独创“浏览器内存级 JS 越权提取技术 (Echarts Instance Hook)”，强行从前端 Canvas 画布剥离近 20 篇阅读量波动数据，彻底根治图表白板 Bug。
* **[绝对纯净命名系统]**：实装工业级脏数据切除引擎。全网域物理抹杀“UID”、“undefined”及默认占位符。引入“智能溯源降级系统”，提取失败时精准展示原始链接，彻底告别“未知账号”盲盒。
* **[精度与死锁修复]**：重构核心数据计算引擎，粉丝与交互数据严格保留小数点后一位；修复了因平台脏数据导致的 JS 渲染线程崩溃及全局大盘卡死问题。

### v1.2.0 Stable (2026-03-03) - 双轨架构与极简稳定版 🚀
* **[重构] 双轨驱动架构 (Dual-Track Engine)**：彻底剥离微博与 WEIQ 采集逻辑。微博端降维采用纯 HTTP 协议穿透 WAF 防火墙（0 浏览器指纹），WEIQ 端保留原生内核维持强登录状态。
* **[修复] WEIQ 跨域授权与风控死锁**：全域统一使用无 `www.` 的根域名 (`weiq.com`) 注入 Cookie，彻底解决授权跨域丢失导致的“疯狂弹滑块验证码”和“404 页面不存在”的致命 Bug。
* **[修复] 纯净 UID 智能解析器**：根治底层正则雪崩缺陷。强力剥离 `100505`、`103505` 等业务线前缀，引入 OSINT 搜索引擎兜底个性化域名，彻底杜绝数据乱匹配与“错抓底部版权号当报价”的假数据灾难。
* **[交互] 优雅人工介入机制**：遇不可逾越的滑块验证码 (403) 或掉线 (401) 时安全挂起队列，前端弹出红色补票遮罩。支持一键唤醒带状态的本地浏览器，手动滑动验证后无缝恢复批量任务。
* **[安全] 终极物理防盲跑**：废除脆弱的前端递归调度，重构为严格的同步 `while` 状态机。遇连续网络断流或 500 系统崩溃瞬间物理锁死，绝不盲目消耗剩余探测队列。

### v0.1.0 Beta (2026-03-01) - 初始概念版
* **[新增]** 精美中文可视化交互雷达面板。
* **[优化]** 引入 `domcontentloaded` 极速加载策略，大幅缩短无头浏览器等待时间。
* **[修复]** 解决 Debian 12 (Trixie) 测试版包管理器崩溃与跨国拉取超时 (exit code 100) 的底层 Bug。
* **[安全]** 完善 `.gitignore` 策略，实现本地敏感通行证 (Cookie) 与代码的物理隔离。

## 📦 快速部署指南
> **提示**: 请确保本地已安装 [GitHub Desktop](https://desktop.github.com/) 并开启 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

1.  **准备通行证**: 在项目根目录下放置 `weibo_auth_state.json` 和 `weiq_auth_state.json` (可选，建议本地扫码生成)。
2.  **编译镜像**: 在项目文件夹内打开终端，执行：
    ```powershell
    docker-compose up -d --build
    ```
3.  **启动雷达**: 访问浏览器地址：`http://localhost:8000/`。

## 🛡️ 安全与隐私声明
本项目代码完全遵循 **MIT 开源协议**。
* **严禁上传**: 本项目已通过 `.gitignore` 锁定隐私文件。请勿手动将包含敏感登录凭证的 `*_auth_state.json` 上传至任何公共仓库。
* **责任限制**: 爬虫脚本仅供学习与商业调研参考，请遵守各平台 Robots 协议，严禁用于任何非法攻击行为。

---
**GitHub 主页**: [youfei0719](https://github.com/youfei0719)  
**更新日期**: 2026年3月3日

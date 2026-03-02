# 📊 Weibo MCN Data Radar (微博 MCN 商业数据雷达)

![Version](https://img.shields.io/badge/Version-v0.1.0--Beta-blue?style=flat-square)
![Update](https://img.shields.io/badge/Update-2026--03--01-green?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Supported-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-orange?style=flat-square)

## 💡 项目简介
本项目是一个基于 **Docker + Playwright** 架构构建的商业级数据采集与分析引擎。专为 MCN 机构和商业博主调研设计，旨在穿透微博重度单页应用 (SPA) 的动态渲染壁垒，实现微博基础运营数据与 **WEIQ 商业底库**（CPM、图文报价、转发报价）的跨平台自动化对齐。



## 🚀 核心特性
* **双轨数据交叉验证**: 独创双轨采集逻辑，同时调度微博主站与 WEIQ 黄金接口，利用 UID 降维打击，确保在主站限流时依然能获取 100% 精准的商业数据。
* **极简苹果风交互**: 采用响应式 Apple Design 风格前端，纯中文交互界面，支持主页链接、UID、昵称多种模糊匹配输入。
* **WAF 穿透防护**: 动态伪装 WebDriver 特征，自动挂载持久化 Cookie 环境，完美避开 403 屏蔽与无头浏览器白屏风控。
* **容器化一键部署**: 深度适配 Windows WSL2 环境，基于 Docker Compose 实现“代码+数据库+环境”的一键式秒级拉起。

## 🛠️ 技术栈
* **后端 (Backend)**: Python 3.10 / FastAPI / Playwright (Async)
* **前端 (Frontend)**: 原生 HTML5 / CSS3 / JavaScript (苹果风格极简面板)
* **存储 (Database)**: PostgreSQL 15
* **基础设施 (Infra)**: Docker / Docker Compose / Debian 12 (Bookworm)

## 📋 版本历史
### v0.1.0 Beta (2026-03-01)
* **[新增]** 精美中文可视化交互雷达面板。
* **[优化]** 引入 `domcontentloaded` 极速加载策略，大幅缩短无头浏览器等待时间。
* **[修复]** 解决 Debian 12 (Trixie) 测试版包管理器崩溃与跨国拉取超时 (exit code 100) 的底层 Bug。
* **[安全]** 完善 `.gitignore` 策略，实现本地敏感通行证 (Cookie) 与代码的物理隔离。

## 📦 快速部署指南
> **提示**: 请确保本地已安装 [GitHub Desktop](https://desktop.github.com/) 并开启 [Docker Desktop](https://www.docker.com/products/docker-desktop/)。

1.  **准备通行证**: 在项目根目录下放置 `weibo_auth_state.json` (可选，建议本地扫码生成)。
2.  **编译镜像**: 在项目文件夹内打开终端，执行：
    ```powershell
    docker-compose up -d --build
    ```
3.  **启动雷达**: 访问浏览器地址：`http://localhost:8000/`。

## 🛡️ 安全与隐私声明
本项目代码完全遵循 **MIT 开源协议**。
* **严禁上传**: 本项目已通过 `.gitignore` 锁定隐私文件。请勿手动将包含敏感登录凭证的 `*_auth_state.json` 上传至任何公共仓库。
* **责任限制**: 爬虫脚本仅供学习与商业调研参考，请遵守各平台 Robots 协议，严禁用于任何非法攻击行为。

---
**GitHub 主页**: [youfei0719](https://github.com/youfei0719)  
**更新日期**: 2026年3月1日

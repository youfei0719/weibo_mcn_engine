import os
import asyncio
from playwright.async_api import async_playwright

async def main():
    user_data_dir = os.path.join(os.getcwd(), "temp_browser_profile")

    async with async_playwright() as p:
        print("正在启动全功能无限制版浏览器 (已注入反封杀与中文字体补丁)...")
        
        # 【深度修复核心】：注入反爬防御与环境伪装参数
        browser_args = [
            "--disable-blink-features=AutomationControlled",  # 移出 WebDriver 标记，彻底解决微博白屏拦截
            "--lang=zh-CN",                                   # 强制中文渲染环境，彻底修复 □□□□ 乱码
            "--start-maximized",                              # 窗口最大化，防止扫码元素被挤压
            "--disable-popup-blocking"                        # 解除底层弹窗限制
        ]
        
        try:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                channel="msedge",
                args=browser_args,
                locale="zh-CN",        # 绑定中文区域
                viewport=None,         # 配合最大化使用
                ignore_https_errors=True
            )
        except Exception:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                channel="chrome",
                args=browser_args,
                locale="zh-CN",
                viewport=None,
                ignore_https_errors=True
            )
        
        page = context.pages[0]
        
        # 1. 获取 WEIQ 商业通行证
        print("正在尝试打开 WEIQ 主页...")
        await page.goto("https://www.weiq.com/", timeout=60000)
        print("\n👉 请在浏览器中扫码或短信登录 WEIQ...")
        input("✅ 【第一步】确认 WEIQ 登录成功后，回到这个黑窗口按下 Enter (回车) 键继续...")
        await context.storage_state(path="weiq_auth_state.json")
        print("🎉 WEIQ 通行证已保存！\n")

        # 2. 获取微博访客通行证
        print("正在尝试打开 微博 专属独立登录页...")
        # 【战术调整】：直接跳入独立登录接口，物理规避所有弹窗白屏问题
        login_url = "https://weibo.com/newlogin?tabtype=weibo&gid=102803&openLoginLayer=0&url=https%3A%2F%2Fweibo.com%2F"
        await page.goto(login_url, timeout=60000)
        
        print("\n👉 请在浏览器中手动扫码登录微博 (二维码白屏已修复)...")
        input("✅ 【第二步】确认 微博 登录成功后，回到这个黑窗口按下 Enter (回车) 键继续...")
        await context.storage_state(path="weibo_auth_state.json")
        print("🎉 微博通行证已保存！")

        await context.close()

asyncio.run(main())
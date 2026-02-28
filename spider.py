import os
import re
import asyncio
from playwright.async_api import async_playwright

class MasterSpiderEngine:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context_weibo = None
        self.context_weiq = None

    async def start(self):
        self.playwright = await async_playwright().start()
        # 注入真实 User-Agent，防止被识别为空壳爬虫
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-images",
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ]
        )
        
        weibo_state = "weibo_auth_state.json"
        if os.path.exists(weibo_state):
            self.context_weibo = await self.browser.new_context(storage_state=weibo_state)
        else:
            self.context_weibo = await self.browser.new_context()
            
        weiq_state = "weiq_auth_state.json"
        if os.path.exists(weiq_state):
            self.context_weiq = await self.browser.new_context(storage_state=weiq_state)
        else:
            self.context_weiq = await self.browser.new_context()

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def collect_and_store(self, target: str):
        page = await self.context_weibo.new_page()
        try:
            if target.startswith("http"):
                url = target
            elif target.isdigit():
                url = f"https://weibo.com/u/{target}"
            else:
                url = f"https://s.weibo.com/weibo?q={target}"
                
            await page.goto(url, timeout=60000)
            
            # 【深度修复1】：智能等待核心元素渲染，过滤无效的空页面
            try:
                await page.wait_for_selector('text="粉丝"', timeout=15000)
            except:
                await page.wait_for_timeout(3000)

            page_text = await page.evaluate("document.body.innerText")
            title = await page.title()
            
            current_url = page.url
            uid_match = re.search(r'(?:weibo\.com/u/|weibo\.com/)(\d+)', current_url)
            uid = uid_match.group(1) if uid_match else (target if target.isdigit() else "未知UID")

            nickname = title.replace("的微博_微博", "").replace(" - 微博搜索", "").replace("个人主页 - 微博", "").strip()
            if not nickname or nickname == "微博":
                nickname = target
                
            followers_count = 0
            statuses_count = 0
            
            # 【深度修复2】：严格正则，过滤类似 "88VIP" 的噪音数据
            fans_match = re.search(r'(?:粉丝)\s*([\d.]+万?)', page_text) or re.search(r'([\d.]+万?)\s*(?:粉丝)', page_text)
            if fans_match:
                fans_str = fans_match.group(1).replace('万', '0000')
                try:
                    followers_count = int(float(fans_str))
                except:
                    pass
                    
            posts_match = re.search(r'(?:微博)\s*([\d,]+)', page_text) or re.search(r'([\d,]+)\s*(?:微博)', page_text)
            if posts_match:
                try:
                    statuses_count = int(posts_match.group(1).replace(',', ''))
                except:
                    pass

            return {
                "uid": uid,
                "nickname": nickname,
                "followers_count": followers_count,
                "statuses_count": statuses_count
            }
        except Exception as e:
            raise Exception(f"微博数据初步解析阻塞: {str(e)}")
        finally:
            await page.close()

    async def collect_commercial_data(self, uid: str, nickname: str):
        page = await self.context_weiq.new_page()
        try:
            url = f"https://www.weiq.com/client/product/weibo/detail?account_uid={uid}"
            await page.goto(url, timeout=60000)
            
            # 【深度修复3】：强制等待 WEIQ 核心商业数据渲染完成
            try:
                await page.wait_for_selector('text="直发CPM"', timeout=15000)
            except:
                await page.wait_for_timeout(4000)
            
            page_text = await page.evaluate("document.body.innerText")
            
            cpm = 0.0
            original_price = 0
            repost_price = 0
            weiq_followers = 0
            weiq_posts = 0
            weiq_nickname = nickname

            # 【核心架构跃升】：直接从 WEIQ 页面反向提取粉丝数和发文量，双保险！
            name_match = re.search(r'([^\n]+)\s*UID[：:]', page_text)
            if name_match:
                weiq_nickname = name_match.group(1).strip()

            fans_match = re.search(r'粉丝数[^\d]*?([\d.]+万?)', page_text)
            if fans_match:
                fans_str = fans_match.group(1).replace('万', '0000')
                try:
                    weiq_followers = int(float(fans_str))
                except:
                    pass

            posts_match = re.search(r'博文总数[^\d]*?([\d,]+)', page_text)
            if posts_match:
                try:
                    weiq_posts = int(posts_match.group(1).replace(',', ''))
                except:
                    pass

            # 【深度修复4】：超级非贪婪正则，无视一切换行和排版直接锁定数字
            cpm_match = re.search(r'直发CPM[^\d]*?([\d.]+)', page_text)
            if cpm_match:
                cpm = float(cpm_match.group(1))
                
            orig_match = re.search(r'原创图文[^\d]*?([\d,]+)', page_text)
            if orig_match:
                original_price = int(orig_match.group(1).replace(',', ''))
                
            repost_match = re.search(r'供稿转发[^\d]*?([\d,]+)', page_text)
            if repost_match:
                repost_price = int(repost_match.group(1).replace(',', ''))
                
            return {
                "weiq_nickname": weiq_nickname,
                "weiq_followers": weiq_followers,
                "weiq_posts": weiq_posts,
                "cpm": cpm,
                "original_price": original_price,
                "repost_price": repost_price
            }
        except Exception as e:
            raise Exception(f"WEIQ 商业底库解析失败: {str(e)}")
        finally:
            await page.close()
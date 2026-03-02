import sys, os, re, asyncio, random, json
import urllib.parse
import httpx
from playwright.async_api import async_playwright

class MasterSpiderEngine:
    def __init__(self):
        self.playwright = self.browser = self.context_weiq = None
        self.lock = asyncio.Semaphore(1) 

    def _get_auth_path(self, filename):
        return os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath("."), filename)

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            channel="msedge", headless=True, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        s2 = self._get_auth_path("weiq_auth_state.json")
        pc_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.context_weiq = await self.browser.new_context(user_agent=pc_ua, storage_state=s2 if os.path.exists(s2) else None)

    async def close(self):
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()

    async def trigger_manual_login(self):
        await self.close()
        p = await async_playwright().start()
        b = await p.chromium.launch(channel="msedge", headless=False)
        
        s2 = self._get_auth_path("weiq_auth_state.json")
        ctx = await b.new_context(storage_state=s2 if os.path.exists(s2) else None)
        
        page = await ctx.new_page()
        await page.goto("https://weiq.com/")
        
        while len(ctx.pages) > 0:
            await asyncio.sleep(2)
            with open(self._get_auth_path("weiq_auth_state.json"), "w") as j: 
                json.dump(await ctx.storage_state(), j)
        await p.stop()
        await self.start()

    async def resolve_uid(self, target: str) -> str:
        clean_target = target.split('?')[0].split('#')[0].strip('/').strip()
        if clean_target.isdigit() and 8 <= len(clean_target) <= 14: return clean_target
        m_container = re.search(r'/p/10\d{4}(\d{8,14})', clean_target)
        if m_container: return m_container.group(1)
        m_standard = re.search(r'(?:weibo\.com|m\.weibo\.cn|weibo\.cn)/(?:u/|profile/|n/)?(\d{8,14})', clean_target)
        if m_standard: return m_standard.group(1)
        
        keyword = clean_target.split('/')[-1]
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"}
            async with httpx.AsyncClient(verify=False, timeout=8.0) as client:
                resp = await client.get(f"https://s.weibo.com/weibo?q={urllib.parse.quote(keyword)}", headers=headers)
                m_search = re.search(r'weibo\.com/(?:u/|n/|profile/)?(\d{8,14})', resp.text) or re.search(r'uid=(\d{8,14})', resp.text)
                if m_search: return m_search.group(1)
        except: pass
        return ""

    # 【专业格式化算法】将所有凌乱的数字统一换算为清爽的“万”
    def format_to_wan(self, val_str):
        if not val_str: return "0"
        val_str = str(val_str).replace(',', '').replace('w', '万').replace('W', '万').strip()
        if '万' in val_str: return val_str
        try:
            num = float(val_str)
            if num >= 10000:
                return f"{num/10000:.1f}万".replace('.0万', '万')
            return str(int(num))
        except:
            return val_str

    async def collect_all(self, target: str):
        async with self.lock:
            uid = await self.resolve_uid(target)
            if not uid: raise Exception("ID_NOT_FOUND")

            max_retries = 2
            for attempt in range(max_retries):
                page = await self.context_weiq.new_page()
                try:
                    await page.goto(f"https://weiq.com/client/product/weibo/detail?account_uid={uid}", timeout=45000)
                    await page.wait_for_timeout(2500)
                    
                    title = await page.title()
                    if "登录" in title: raise Exception("AUTH_EXPIRED")
                    
                    text = await page.evaluate("document.body.innerText")
                    
                    if "安全验证" in text or "滑块" in text or "验证码" in text or "向右滑动" in text:
                        raise Exception("WEIQ_VERIFY_BLOCKED")

                    if "原创图文" not in text and "直发CPM" not in text:
                        raise Exception("WEIQ_NO_DATA")

                    def get_val(reg, t): 
                        m = re.search(reg, t)
                        return m.group(1).replace(',', '') if m else None

                    # 核心报价
                    price_str = get_val(r'原创图文[^\d]*?([\d,]+)', text)
                    if not price_str: raise Exception("WEIQ_NO_DATA")
                    price = int(price_str)
                    cpm = float(get_val(r'直发CPM[^\d]*?([\d.]+)', text) or 0)

                    # 【多维度数据扩充】提取粉丝、平均阅读、平均互动
                    followers_raw = get_val(r'粉丝数[^\d]*?([\d.]+万?)', text)
                    avg_read_raw = get_val(r'(?:平均|预期)阅读[数量]?[^\d]*?([\d.]+万?)', text)
                    avg_interact_raw = get_val(r'(?:平均)?互动[数量]?[^\d]*?([\d.]+万?)', text)

                    # 【获取绝对真实的昵称，拒绝 UID】
                    nickname = ""
                    try:
                        nickname = await page.evaluate("() => { let el = document.querySelector('.account-name, .name, .user-name, h1'); return el ? el.innerText.trim() : ''; }")
                    except: pass
                    
                    if not nickname: nickname = title.split("的微博报价")[0].strip() if "的微博报价" in title else ""
                    
                    # 【双重兜底】如果依然是数字(说明WEIQ没抓到)，利用搜索引擎级爬虫强抓微博源站的真实名字
                    if not nickname or nickname.isdigit() or nickname == uid:
                        try:
                            headers = {"User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"}
                            async with httpx.AsyncClient(verify=False, timeout=5.0) as client:
                                resp = await client.get(f"https://m.weibo.cn/u/{uid}", headers=headers)
                                m_title = re.search(r'<title>(.*?)的微博.*?</title>', resp.text)
                                if m_title: nickname = m_title.group(1).strip()
                        except: pass
                    
                    # 最后极度兜底，实在查不到才给 未知
                    if nickname.isdigit() or not nickname: nickname = "未知昵称"

                    return {
                        "uid": uid,
                        "nickname": nickname,
                        "followers": self.format_to_wan(followers_raw),
                        "avg_read": self.format_to_wan(avg_read_raw),
                        "avg_interact": self.format_to_wan(avg_interact_raw),
                        "commercial": {
                            "cpm": cpm,
                            "original_price": price
                        }
                    }
                except Exception as e:
                    err_str = str(e)
                    if "AUTH_EXPIRED" in err_str or "WEIQ_VERIFY_BLOCKED" in err_str or "WEIQ_NO_DATA" in err_str:
                        raise e
                    if attempt == max_retries - 1:
                        if "Execution context was destroyed" in err_str or "Target closed" in err_str:
                            raise Exception("NETWORK_ERROR")
                        raise e
                    await asyncio.sleep(2)
                finally:
                    await page.close()
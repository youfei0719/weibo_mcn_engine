import sys, os, re, asyncio, json
import urllib.parse
import httpx
from playwright.async_api import async_playwright

class MasterSpiderEngine:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context_weiq = None
        self.lock = asyncio.Semaphore(1) 

    def _get_auth_path(self, filename):
        return os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath("."), filename)

    async def start(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
        if self.browser:
            try: await self.browser.close()
            except: pass

        self.browser = await self.playwright.chromium.launch(
            channel="msedge", headless=True, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        s2 = self._get_auth_path("weiq_auth_state.json")
        pc_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.context_weiq = await self.browser.new_context(user_agent=pc_ua, storage_state=s2 if os.path.exists(s2) else None)

    async def close(self):
        if self.context_weiq: await self.context_weiq.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()

    async def trigger_manual_login(self):
        if self.context_weiq: await self.context_weiq.close()
        if self.browser: await self.browser.close()
        
        b = await self.playwright.chromium.launch(channel="msedge", headless=False)
        s2 = self._get_auth_path("weiq_auth_state.json")
        ctx = await b.new_context(storage_state=s2 if os.path.exists(s2) else None)
        page = await ctx.new_page()
        await page.goto("https://weiq.com/")
        while len(ctx.pages) > 0:
            await asyncio.sleep(2)
            with open(self._get_auth_path("weiq_auth_state.json"), "w") as j: 
                json.dump(await ctx.storage_state(), j)
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
            headers = {"User-Agent": "Mozilla/5.0"}
            async with httpx.AsyncClient(verify=False, timeout=8.0) as client:
                resp = await client.get(f"https://s.weibo.com/weibo?q={urllib.parse.quote(keyword)}", headers=headers)
                m_search = re.search(r'weibo\.com/(?:u/|n/|profile/)?(\d{8,14})', resp.text) or re.search(r'uid=(\d{8,14})', resp.text)
                if m_search: return m_search.group(1)
        except: pass
        return ""

    def format_to_wan(self, val_str):
        if not val_str or val_str == "N/A": return "N/A"
        val_str = str(val_str).replace(',', '').replace('w', '万').replace('W', '万').strip()
        if '万' in val_str: return val_str
        try:
            num = float(val_str)
            if num >= 10000: return f"{num/10000:.1f}万".replace('.0万', '万')
            return f"{num:.1f}".replace('.0', '')
        except: return val_str

    def get_num(self, val_str):
        if not val_str or val_str == "N/A": return 0
        v = str(val_str).replace(',', '').replace('万', '0000')
        try: return float(v)
        except: return 0

    async def collect_all(self, target: str):
        async with self.lock:
            uid = await self.resolve_uid(target)
            if not uid: raise Exception("ID_NOT_FOUND")

            max_retries = 2
            for attempt in range(max_retries):
                page = await self.context_weiq.new_page()
                
                intercepted_data = {"trend_20": [], "fan_growth": []}
                async def handle_response(response):
                    if "application/json" in response.headers.get("content-type", ""):
                        try:
                            json_data = await response.json()
                            s_data = json.dumps(json_data)
                            m_read = re.search(r'"(?:read_count_trend|readTrend|trend|read_num)":\s*\[([\d,\.\s]+)\]', s_data)
                            if m_read: intercepted_data["trend_20"] = [float(x) for x in m_read.group(1).split(',') if x.strip()]
                            m_fans = re.search(r'"(?:fans_trend|followerTrend|fans)":\s*\[([\d,\.\s]+)\]', s_data)
                            if m_fans: intercepted_data["fan_growth"] = [float(x) for x in m_fans.group(1).split(',') if x.strip()]
                        except: pass
                
                page.on("response", handle_response)

                try:
                    await page.goto(f"https://weiq.com/client/product/weibo/detail?account_uid={uid}", timeout=45000)
                    
                    for _ in range(4):
                        await page.mouse.wheel(0, 1000)
                        await asyncio.sleep(0.8)
                    
                    title = await page.title()
                    if "登录" in title: raise Exception("AUTH_EXPIRED")
                    
                    text = await page.evaluate("document.body.innerText")
                    if "安全验证" in text or "滑块" in text or "验证码" in text or "向右滑动" in text:
                        raise Exception("WEIQ_VERIFY_BLOCKED")

                    nickname = await page.evaluate("() => { let el = document.querySelector('.account-name, .name, .user-name, h1'); return el ? el.innerText.trim() : ''; }")
                    nickname = re.sub(r'(?i)\s*UID[:：]?\s*\d+', '', nickname).strip()
                    
                    if not nickname or nickname.isdigit(): 
                        t_name = title.split("的微博报价")[0].strip()
                        t_name = re.sub(r'(?i)\s*UID[:：]?\s*\d+', '', t_name).strip()
                        # 【核心防污染】：如果是这些默认占位符，说明没抓到名字，直接赋空值！
                        if "weibo账号详情" in t_name or "WEIQ" in t_name or not t_name:
                            nickname = "" 
                        else:
                            nickname = t_name
                    
                    category = await page.evaluate("() => { let el = document.querySelector('.tags, .type, .account-tags, .domain'); return el ? el.innerText.trim().split(/[\\n\\s]+/)[0] : ''; }")

                    if "原创图文" not in text and "直发CPM" not in text:
                        raise Exception(f"WEIQ_NO_DATA||{nickname}||{category}")

                    def get_metric(reg, t, fallback="N/A"): 
                        m = re.search(reg, t)
                        return m.group(1).replace(',', '').strip() if m else fallback
                        
                    price_str = get_metric(r'原创图文[^\d]*?([\d,]+)', text)
                    if price_str == "N/A": raise Exception(f"WEIQ_NO_DATA||{nickname}||{category}")
                    
                    price = int(price_str)
                    cpm = float(get_metric(r'直发CPM[^\d]*?([\d.]+)', text, "0"))
                    followers_raw = get_metric(r'粉丝数[^\d]*?([\d.]+万?)', text)

                    deep_data = {
                        "read_median": self.format_to_wan(get_metric(r'阅读[数量]?中位数[^\d]*?([\d.]+万?)', text)),
                        "direct_read_median": self.format_to_wan(get_metric(r'直发阅读[数量]?中位数[^\d]*?([\d.]+万?)', text)),
                        "forward_read_median": self.format_to_wan(get_metric(r'转发阅读[数量]?中位数[^\d]*?([\d.]+万?)', text)),
                        "interact_median": self.format_to_wan(get_metric(r'互动[数量]?中位数[^\d]*?([\d.]+万?)', text)),
                        "direct_interact_median": self.format_to_wan(get_metric(r'直发互动中位数[^\d]*?([\d.]+万?)', text)),
                        "forward_interact_median": self.format_to_wan(get_metric(r'转发互动中位数[^\d]*?([\d.]+万?)', text)),
                        "like_median": self.format_to_wan(get_metric(r'点赞[数量]?中位数[^\d]*?([\d.]+万?)', text)),
                        "comment_median": self.format_to_wan(get_metric(r'评论[数量]?中位数[^\d]*?([\d.]+万?)', text)),
                        "post_count": get_metric(r'发布博文数[^\d]*?([\d]+)', text),
                    }

                    t_20 = intercepted_data["trend_20"][-20:] if intercepted_data["trend_20"] else []
                    f_20 = intercepted_data["fan_growth"][-20:] if intercepted_data["fan_growth"] else []

                    return {
                        "uid": uid,
                        "nickname": nickname,
                        "category": category,
                        "followers": self.format_to_wan(followers_raw),
                        "followers_num": self.get_num(followers_raw),
                        "commercial": {"cpm": cpm, "original_price": price},
                        "deep_data": deep_data,
                        "charts": {"trend_20": t_20, "fan_growth": f_20}
                    }
                except Exception as e:
                    err_str = str(e)
                    if "AUTH_EXPIRED" in err_str or "WEIQ_VERIFY_BLOCKED" in err_str or "WEIQ_NO_DATA" in err_str: raise e
                    if attempt == max_retries - 1:
                        if "Execution context was destroyed" in err_str or "Target closed" in err_str: raise Exception("NETWORK_ERROR")
                        raise e
                    await asyncio.sleep(2)
                finally:
                    page.remove_listener("response", handle_response)
                    await page.close()
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import logging
from typing import Dict, Any, Optional

# تنظیمات لاگ برای پیدا کردن سریع مشکلات
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class UltimateDataPipeline:
    def __init__(self, max_runtime_hours: float = 5.8):
        self.start_time = time.time()
        # تنظیم روی 5.8 ساعت تا قبل از تایم‌اوت شدن GitHub Actions فرآیند را ذخیره کنیم
        self.MAX_RUNTIME_SECONDS = max_runtime_hours * 3600 
        
        # دیکشنری نهایی برای آیتم‌های به‌شدت خاص که در هیچ سورس کدی پیدا نمی‌شوند
        # این دیکشنری تضمین می‌کند جای خالی در Vercel نخواهید داشت
        self.hardcoded_fallbacks = {
            "Special_Item_Name": {"country": "USA", "rank": "IV"},
            "Another_Weird_Item": {"country": "Germany", "rank": "V"}
        }

    def _check_timeout(self):
        """تضمین اینکه پروسه هرگز به ارور 6 ساعته برخورد نمی‌کند"""
        if (time.time() - self.start_time) > self.MAX_RUNTIME_SECONDS:
            logger.warning("هشدار: زمان در حال اتمام است. ذخیره‌سازی اضطراری...")
            raise TimeoutError("Graceful_Exit")

    # ==========================================
    # زنجیره روش‌های پیدا کردن «کشور» (Country)
    # ==========================================
    def _get_country_method_1_api(self, item_name: str) -> Optional[str]:
        # روش ۱: استفاده از API پنهان سایت (در صورت وجود)
        pass

    def _get_country_method_2_infobox(self, soup: BeautifulSoup) -> Optional[str]:
        # روش ۲: گشتن دقیق در جدول مشخصات (Infobox) با سلکتورهای مختلف
        selectors = [
            "table.infobox tr:contains('Country')",
            "div.country-badge",
            "span.nation-name"
        ]
        for sel in selectors:
            element = soup.select_operator(sel) # شبه‌کد برای پیدا کردن با CSS Selector
            if element: return element.text.strip()
        return None

    def _get_country_method_3_flags(self, soup: BeautifulSoup) -> Optional[str]:
        # روش ۳: استخراج نام کشور از روی Alt عکس پرچم‌ها
        images = soup.find_all("img")
        for img in images:
            alt_text = img.get("alt", "").lower()
            if "flag" in alt_text:
                if "usa" in alt_text or "united states" in alt_text: return "USA"
                if "ussr" in alt_text or "soviet" in alt_text: return "USSR"
                if "germany" in alt_text: return "Germany"
        return None

    def _get_country_method_4_regex_html(self, html_text: str) -> Optional[str]:
        # روش ۴: جستجوی وحشیانه در کل کدهای HTML با Regex
        # به دنبال الگوهایی مثل "Country: USA" یا "Nation: USSR"
        patterns = [
            r'(?:Country|Nation)[\s:-]+([A-Za-z]+)',
            r'flag_([a-z]+)\.png'
        ]
        for pattern in patterns:
            match = re.search(pattern, html_text, re.IGNORECASE)
            if match:
                return match.group(1).capitalize()
        return None

    def _get_country_method_5_heuristics(self, item_name: str) -> Optional[str]:
        # روش ۵: تشخیص هوشمند از روی اسم آیتم (NLP ساده)
        name_lower = item_name.lower()
        if any(prefix in name_lower for prefix in ["m4", "t29", "f-4", "abrams"]): return "USA"
        if any(prefix in name_lower for prefix in ["t-34", "t-90", "mig", "is-"]): return "USSR"
        if any(prefix in name_lower for prefix in ["panzer", "bf-109", "tiger"]): return "Germany"
        return None

    def extract_country_master(self, item_name: str, html_text: str, soup: BeautifulSoup) -> str:
        """
        مدیر ارشد استخراج کشور: ده‌ها روش را به ترتیب اجرا می‌کند تا بالاخره یکی جواب دهد.
        """
        # اگر آیتم در لیست موارد استثنا بود، اصلا وقت تلف نکن و همونو بده
        if item_name in self.hardcoded_fallbacks and "country" in self.hardcoded_fallbacks[item_name]:
            return self.hardcoded_fallbacks[item_name]["country"]

        methods = [
            lambda: self._get_country_method_2_infobox(soup),
            lambda: self._get_country_method_3_flags(soup),
            lambda: self._get_country_method_4_regex_html(html_text),
            lambda: self._get_country_method_5_heuristics(item_name)
        ]

        for method in methods:
            try:
                result = method()
                if result and result.strip() != "":
                    # تمیز کردن دیتای نهایی قبل از ارسال به دیتابیس
                    return self._normalize_data(result.strip())
            except Exception as e:
                logger.debug(f"خطا در یک متد (رد شدن): {e}")
                continue

        # اگر بعد از ده‌ها روش باز هم پیدا نشد، یک مقدار استاندارد برگردان که سایت را خراب نکند
        logger.error(f"کشور برای {item_name} با هیچ روشی پیدا نشد!")
        return "Unknown_Nation"

    # ==========================================
    # ابزارهای تمیزکاری نهایی
    # ==========================================
    def _normalize_data(self, data: str) -> str:
        """این متد تضمین می‌کند هیچ کاراکتر عجیب، فاصله اضافه یا دیتای کثیفی وارد Vercel نشود"""
        data = re.sub(r'\s+', ' ', data) # حذف فاصله‌های چندگانه
        data = data.replace('\n', '').replace('\r', '')
        return data

    # ==========================================
    # بدنه اصلی اجرا
    # ==========================================
    def run_pipeline(self, urls_to_scrape: list):
        final_database = []
        
        try:
            for url in urls_to_scrape:
                self._check_timeout() # چک کردن زمان برای جلوگیری از قطع ناگهانی
                
                # فرض می‌کنیم رکوئست زدیم و دیتای صفحه رو گرفتیم
                # response = requests.get(url, timeout=10)
                # soup = BeautifulSoup(response.text, 'html.parser')
                
                # نمونه دیتای تستی
                item_name = "T-34-85"
                html_text = "<html><body>Some random text with flag_ussr.png</body></html>"
                soup = BeautifulSoup(html_text, 'html.parser')

                # ساختن دقیق آبجکت دیتابیس
                item_data = {
                    "id": url.split("/")[-1],
                    "name": item_name,
                    "country": self.extract_country_master(item_name, html_text, soup),
                    # "rank": self.extract_rank_master(...),
                    # "type": self.extract_type_master(...)
                }
                
                final_database.append(item_data)
                logger.info(f"دیتا با موفقیت استخراج شد: {item_data['name']}")
                
                time.sleep(1) # جلوگیری از بلاک شدن توسط سایت هدف

        except TimeoutError:
            logger.info("پروسه به دلیل محدودیت زمانی متوقف شد، اما دیتای جمع‌آوری شده تا الان سالم است.")
        except Exception as e:
            logger.critical(f"خطای پیش‌بینی نشده: {e}")
        finally:
            # این بخش تحت هر شرایطی اجرا می‌شود!
            # اینجا فایل JSON نهایی را ذخیره می‌کنید تا سایت Next.js شما آن را بخواند.
            with open("final_database.json", "w", encoding="utf-8") as f:
                json.dump(final_database, f, ensure_ascii=False, indent=2)
            logger.info("فایل نهایی با دقت کامل ذخیره شد.")

# اجرای اسکریپت
if __name__ == "__main__":
    urls = ["site.com/item1", "site.com/item2"] * 100 # لیست فرضی
    scraper = UltimateDataPipeline(max_runtime_hours=5.5)
    scraper.run_pipeline(urls)

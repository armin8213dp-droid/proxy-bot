import asyncio
import logging
import random
import requests
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime

# ============================================
# اینجا توکن و chat_id خودت رو بذار
BOT_TOKEN = "8500441833:AAGgCPyFlvd7yvsU-sORfBT2P-OUW8VoqEs"
CHANNEL_ID = "-1003816897802"
# ============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_mtproto_proxies():
    """جمع‌آوری پروکسی MTProto"""
    proxies = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get('https://mtpro.xyz/api/?type=mtproto', headers=headers, timeout=10)
        data = response.json()
        for item in data[:10]:
            proxies.append({
                'type': 'MTProto',
                'server': item.get('host', ''),
                'port': item.get('port', ''),
                'secret': item.get('secret', ''),
                'link': f"tg://proxy?server={item.get('host')}&port={item.get('port')}&secret={item.get('secret')}"
            })
    except Exception as e:
        logger.error(f"خطا در دریافت MTProto: {e}")

    try:
        response = requests.get('https://mtpro.xyz/api/?type=socks5', headers=headers, timeout=10)
        data = response.json()
        for item in data[:10]:
            proxies.append({
                'type': 'SOCKS5',
                'server': item.get('host', ''),
                'port': item.get('port', ''),
                'user': item.get('user', ''),
                'password': item.get('pass', ''),
                'link': f"tg://socks?server={item.get('host')}&port={item.get('port')}&user={item.get('user', '')}&pass={item.get('pass', '')}"
            })
    except Exception as e:
        logger.error(f"خطا در دریافت SOCKS5: {e}")

    return proxies

def format_proxy_message(proxies):
    """ساخت پیام زیبا برای کانال"""
    now = datetime.now().strftime("%H:%M - %Y/%m/%d")
    
    msg = f"🔰 **پروکسی رایگان تلگرام**\n"
    msg += f"⏰ آپدیت: `{now}`\n"
    msg += "━━━━━━━━━━━━━━━\n\n"

    selected = random.sample(proxies, min(5, len(proxies)))

    for i, proxy in enumerate(selected, 1):
        if proxy['type'] == 'MTProto':
            msg += f"🔵 **پروکسی {i} - MTProto**\n"
            msg += f"🌐 سرور: `{proxy['server']}`\n"
            msg += f"🔌 پورت: `{proxy['port']}`\n"
            msg += f"🔑 سکرت: `{proxy['secret']}`\n"
            msg += f"[🔗 اتصال مستقیم]({proxy['link']})\n\n"
        else:
            msg += f"🟢 **پروکسی {i} - SOCKS5**\n"
            msg += f"🌐 سرور: `{proxy['server']}`\n"
            msg += f"🔌 پورت: `{proxy['port']}`\n"
            if proxy['user']:
                msg += f"👤 یوزر: `{proxy['user']}`\n"
            if proxy['password']:
                msg += f"🔒 پسورد: `{proxy['password']}`\n"
            msg += f"[🔗 اتصال مستقیم]({proxy['link']})\n\n"

    msg += "━━━━━━━━━━━━━━━\n"
    msg += "⏳ آپدیت بعدی: ۱ ساعت دیگه\n"
    msg += "📢 کانال ما رو به دوستات معرفی کن!"

    return msg

async def send_proxies():
    """ارسال پروکسی به کانال"""
    bot = Bot(token=BOT_TOKEN)
    
    while True:
        try:
            logger.info("در حال دریافت پروکسی...")
            proxies = get_mtproto_proxies()
            
            if len(proxies) >= 1:
                message = format_proxy_message(proxies)
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("پروکسی‌ها با موفقیت ارسال شدند!")
            else:
                logger.warning("پروکسی کافی پیدا نشد!")
                
        except TelegramError as e:
            logger.error(f"خطای تلگرام: {e}")
        except Exception as e:
            logger.error(f"خطای کلی: {e}")
        
        # یک ساعت صبر کن
        logger.info("انتظار ۱ ساعته...")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(send_proxies())

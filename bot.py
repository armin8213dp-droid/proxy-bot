import asyncio
import logging
import random
import requests
from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime

# ============================================
BOT_TOKEN = "8500441833:AAGgCPyFlvd7yvsU-sORfBT2P-OUW8VoqEs"
CHANNEL_ID = "-1003816897802"
# ============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_source_1():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies/mtproto"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if 'tg://proxy?' in line:
                proxies.append({'type': 'MTProto', 'link': line})
        logger.info(f"منبع ۱ (MTProto GitHub): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۱ خطا: {e}")
    return proxies

def get_source_2():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies/socks"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if 'tg://socks?' in line:
                proxies.append({'type': 'SOCKS5', 'link': line})
        logger.info(f"منبع ۲ (SOCKS GitHub): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۲ خطا: {e}")
    return proxies

def get_source_3():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    ip, port = parts
                    proxies.append({
                        'type': 'SOCKS5',
                        'server': ip,
                        'port': port,
                        'link': f"tg://socks?server={ip}&port={port}"
                    })
        logger.info(f"منبع ۳ (TheSpeedX): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۳ خطا: {e}")
    return proxies

def get_source_4():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    ip, port = parts
                    proxies.append({
                        'type': 'SOCKS5',
                        'server': ip,
                        'port': port,
                        'link': f"tg://socks?server={ip}&port={port}"
                    })
        logger.info(f"منبع ۴ (hookzof): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۴ خطا: {e}")
    return proxies

def get_source_5():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    ip, port = parts
                    proxies.append({
                        'type': 'SOCKS5',
                        'server': ip,
                        'port': port,
                        'link': f"tg://socks?server={ip}&port={port}"
                    })
        logger.info(f"منبع ۵ (ShiftyTR): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۵ خطا: {e}")
    return proxies

def get_source_6():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.json"
        r = requests.get(url, headers=HEADERS, timeout=15)
        data = r.json()
        for item in data:
            ip = item.get('ip', '')
            port = item.get('port', '')
            if ip and port:
                proxies.append({
                    'type': 'SOCKS5',
                    'server': ip,
                    'port': str(port),
                    'link': f"tg://socks?server={ip}&port={port}"
                })
        logger.info(f"منبع ۶ (proxifly): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۶ خطا: {e}")
    return proxies

def get_source_7():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    ip, port = parts
                    proxies.append({
                        'type': 'SOCKS5',
                        'server': ip,
                        'port': port,
                        'link': f"tg://socks?server={ip}&port={port}"
                    })
        logger.info(f"منبع ۷ (monosans): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۷ خطا: {e}")
    return proxies

def get_source_8():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    ip, port = parts
                    proxies.append({
                        'type': 'SOCKS5',
                        'server': ip,
                        'port': port,
                        'link': f"tg://socks?server={ip}&port={port}"
                    })
        logger.info(f"منبع ۸ (clarketm): {len(proxies)} پروکسی")
    except Exception as e:
        logger.error(f"منبع ۸ خطا: {e}")
    return proxies

def format_message(proxies):
    now = datetime.now().strftime("%H:%M - %Y/%m/%d")
    msg = "🔰 **پروکسی رایگان تلگرام**\n"
    msg += f"⏰ آپدیت: `{now}`\n"
    msg += "━━━━━━━━━━━━━━━\n\n"

    count = min(5, len(proxies))
    selected = random.sample(proxies, count)

    for i, proxy in enumerate(selected, 1):
        if proxy['type'] == 'MTProto':
            msg += f"🔵 **پروکسی {i} - MTProto**\n"
            msg += f"[🔗 اتصال مستقیم]({proxy['link']})\n\n"
        else:
            msg += f"🟢 **پروکسی {i} - SOCKS5**\n"
            if 'server' in proxy:
                msg += f"🌐 سرور: `{proxy['server']}`\n"
                msg += f"🔌 پورت: `{proxy['port']}`\n"
            msg += f"[🔗 اتصال مستقیم]({proxy['link']})\n\n"

    msg += "━━━━━━━━━━━━━━━\n"
    msg += "⏳ آپدیت بعدی: ۳۰ دقیقه دیگه\n"
    msg += "📢 کانال ما رو به دوستات معرفی کن!"
    return msg

async def send_proxies():
    bot = Bot(token=BOT_TOKEN)
    while True:
        try:
            logger.info("شروع جمع‌آوری پروکسی از همه منابع...")
            all_proxies = []
            all_proxies += get_source_1()
            all_proxies += get_source_2()
            all_proxies += get_source_3()
            all_proxies += get_source_4()
            all_proxies += get_source_5()
            all_proxies += get_source_6()
            all_proxies += get_source_7()
            all_proxies += get_source_8()

            logger.info(f"مجموع پروکسی‌های پیدا شده: {len(all_proxies)}")

            if len(all_proxies) >= 1:
                message = format_message(all_proxies)
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=message,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("پروکسی‌ها با موفقیت ارسال شدند!")
            else:
                logger.warning("هیچ پروکسی پیدا نشد!")

        except TelegramError as e:
            logger.error(f"خطای تلگرام: {e}")
        except Exception as e:
            logger.error(f"خطای کلی: {e}")

        logger.info("انتظار ۳۰ دقیقه...")
        await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(send_proxies())


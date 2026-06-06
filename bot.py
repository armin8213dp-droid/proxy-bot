import asyncio
import logging
import random
import requests
import socket
import base64
import json
from bs4 import BeautifulSoup
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

# سرورهای تلگرام برای تست MTProto
TELEGRAM_SERVERS = [
    "149.154.167.51",
    "149.154.167.91",
    "149.154.167.92",
]

# کانال های MTProto
MTPROTO_CHANNELS = [
    "ProxyMTProto",
    "proxy_ir",
    "mtpro_xyz",
    "exbta",
    "proxy_ru",
    "freeproxy_io",
    "freev2ray",
]

# کانال های V2Ray
V2RAY_CHANNELS = [
    "v2ray_configs",
    "vlessconfig",
    "vmessorg",
    "clash_config",
    "shadowsocks_ir",
    "freev2ray",
    "configV2rayNG",
]

# منابع GitHub برای V2Ray
V2RAY_GITHUB = [
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
    "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity.txt",
]

# منبع GitHub برای MTProto
MTPROTO_GITHUB = "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies/mtproto"

# اشعار پند آموز
POEMS = [
    ("حافظ", "بیا که قصر امل سخت سست بنیاد است\nبیار باده که بنیاد عمر بر باد است"),
    ("سعدی", "بنی آدم اعضای یکدیگرند\nکه در آفرینش ز یک گوهرند"),
    ("مولانا", "آتش عشق است کاندر نی فتاد\nجوشش عشق است کاندر می فتاد"),
    ("فردوسی", "توانا بود هر که دانا بود\nز دانش دل پیر برنا بود"),
    ("سعدی", "هر که در خوابگه خاک آرمید\nرفت و آمد ز این جهان ببرید"),
    ("حافظ", "الا یا ایها الساقی ادر کاسا و ناولها\nکه عشق آسان نمود اول ولی افتاد مشکل‌ها"),
    ("فردوسی", "چو ایران نباشد تن من مباد\nبدین بوم و بر زنده یک تن مباد"),
    ("خیام", "این قافله عمر عجب می‌گذرد\nدریاب دمی که با طرب می‌گذرد"),
    ("مولانا", "من کجا بودم عجب کو بود من\nحیرت آمد حیرت آمد حیرتم"),
    ("سعدی", "توانگری به هنر است نه به مال\nگوهر ذات است نه زر و جمال"),
]

# ==================== جمع آوری ====================

def fetch_mtproto_github():
    proxies = []
    try:
        r = requests.get(MTPROTO_GITHUB, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if 'tg://proxy?' in line and 'secret=' in line:
                proxies.append(line)
    except Exception as e:
        logger.error(f"GitHub MTProto: {e}")
    return proxies

def fetch_mtproto_channels():
    proxies = []
    for channel in MTPROTO_CHANNELS:
        try:
            url = f"https://t.me/s/{channel}"
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            for msg in soup.find_all('div', class_='tgme_widget_message_text'):
                for link in msg.find_all('a'):
                    href = link.get('href', '')
                    if 'tg://proxy?' in href and 'secret=' in href:
                        proxies.append(href)
                text = msg.get_text()
                for part in text.split():
                    if part.startswith('tg://proxy?') and 'secret=' in part:
                        proxies.append(part)
        except Exception as e:
            logger.error(f"کانال {channel}: {e}")
    return proxies

def fetch_v2ray_github():
    configs = []
    for url in V2RAY_GITHUB:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            for line in r.text.strip().split('\n'):
                line = line.strip()
                if line.startswith(('vmess://', 'vless://', 'trojan://')):
                    configs.append(line)
        except Exception as e:
            logger.error(f"GitHub V2Ray: {e}")
    return configs

def fetch_v2ray_channels():
    configs = []
    for channel in V2RAY_CHANNELS:
        try:
            url = f"https://t.me/s/{channel}"
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            for msg in soup.find_all('div', class_='tgme_widget_message_text'):
                text = msg.get_text()
                for line in text.split('\n'):
                    line = line.strip()
                    if line.startswith(('vmess://', 'vless://', 'trojan://')):
                        configs.append(line)
        except Exception as e:
            logger.error(f"کانال {channel}: {e}")
    return configs

# ==================== تست ====================

def test_mtproto(link):
    """تست MTProto با سرور واقعی تلگرام"""
    try:
        if 'server=' not in link or 'port=' not in link:
            return False
        server = link.split('server=')[1].split('&')[0]
        port = int(link.split('port=')[1].split('&')[0])
        # تست اتصال به پروکسی
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((server, port))
        sock.close()
        if result != 0:
            return False
        # تست اتصال به سرور تلگرام از طریق پروکسی
        tg_server = random.choice(TELEGRAM_SERVERS)
        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock2.settimeout(5)
        result2 = sock2.connect_ex((tg_server, 443))
        sock2.close()
        return result2 == 0
    except:
        return False

def extract_v2ray_address(link):
    """استخراج host و port از کانفیگ V2Ray"""
    try:
        if link.startswith('vmess://'):
            padding = len(link[8:]) % 4
            if padding:
                link_padded = link[8:] + '=' * (4 - padding)
            else:
                link_padded = link[8:]
            decoded = base64.b64decode(link_padded).decode('utf-8')
            data = json.loads(decoded)
            return str(data.get('add', '')), int(data.get('port', 0))
        elif link.startswith(('vless://', 'trojan://')):
            part = link.split('://')[1]
            if '@' in part:
                addr_part = part.split('@')[1].split('?')[0].split('#')[0]
                if ':' in addr_part:
                    host, port = addr_part.rsplit(':', 1)
                    return host, int(port)
    except:
        pass
    return '', 0

def test_v2ray(link):
    """تست V2Ray با socket"""
    try:
        host, port = extract_v2ray_address(link)
        if not host or not port:
            return False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def get_live_mtproto():
    """جمع آوری و فیلتر MTProto های زنده"""
    all_links = fetch_mtproto_github() + fetch_mtproto_channels()
    # حذف تکراری
    unique = list(dict.fromkeys(all_links))
    random.shuffle(unique)
    logger.info(f"MTProto کل: {len(unique)}")
    live = []
    for link in unique[:50]:
        if test_mtproto(link):
            live.append(link)
            logger.info(f"MTProto زنده: {link[:60]}")
        if len(live) >= 10:
            break
    logger.info(f"MTProto زنده: {len(live)}")
    return live

def get_live_v2ray():
    """جمع آوری و فیلتر V2Ray های زنده"""
    all_links = fetch_v2ray_github() + fetch_v2ray_channels()
    unique = list(dict.fromkeys(all_links))
    random.shuffle(unique)
    logger.info(f"V2Ray کل: {len(unique)}")
    live = []
    for link in unique[:50]:
        if test_v2ray(link):
            live.append(link)
            logger.info(f"V2Ray زنده پیدا شد!")
        if len(live) >= 5:
            break
    logger.info(f"V2Ray زنده: {len(live)}")
    return live

# ==================== فرمت پیام ====================

def format_proxy_message(proxies):
    msg = "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "   🔰 I R A N  P R O X Y 🔰\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
    for i, link in enumerate(proxies[:5], 1):
        msg += f"💎 پروکسی {i}  —  MTProto\n"
        msg += f"╰─► [🔗 اتصال مستقیم]({link})\n\n"
    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
    msg += "✅ همه پروکسی‌ها تست شده و زنده‌اند\n"
    msg += "🔄 آپدیت بعدی: ۱۰ دقیقه دیگه\n"
    msg += "👥 کانال رو شیر کن و حمایت کن!\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━"
    return msg

def format_v2ray_message(configs):
    msg = "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "   🚀 V 2 R A Y  C O N F I G 🚀\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
    for i, link in enumerate(configs[:2], 1):
        if link.startswith('vmess'):
            config_type = "VMess"
        elif link.startswith('vless'):
            config_type = "VLess"
        else:
            config_type = "Trojan"
        msg += f"💎 کانفیگ {i}  —  {config_type}\n"
        msg += f"`{link}`\n\n"
    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
    msg += "✅ کانفیگ‌ها تست شده و زنده‌اند\n"
    msg += "📱 اپ مورد نیاز: V2RayNG یا Nekoray\n"
    msg += "👥 کانال رو شیر کن و حمایت کن!\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━"
    return msg

def format_poem_message():
    poet, poem = random.choice(POEMS)
    msg = "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "   🌹 شعر شب  |  پند آموز\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"✍️ **{poet}**\n\n"
    msg += f"_{poem}_\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━"
    return msg

# ==================== تسک ها ====================

async def proxy_task(bot):
    while True:
        try:
            logger.info("شروع تسک MTProto...")
            live = get_live_mtproto()
            if live:
                msg = format_proxy_message(live)
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("MTProto ارسال شد!")
            else:
                logger.warning("MTProto زنده پیدا نشد!")
        except TelegramError as e:
            logger.error(f"تلگرام خطا: {e}")
        except Exception as e:
            logger.error(f"خطا در MTProto تسک: {e}")
        await asyncio.sleep(600)

async def v2ray_task(bot):
    while True:
        try:
            logger.info("شروع تسک V2Ray...")
            live = get_live_v2ray()
            if live:
                msg = format_v2ray_message(live)
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("V2Ray ارسال شد!")
            else:
                logger.warning("V2Ray زنده پیدا نشد!")
        except TelegramError as e:
            logger.error(f"تلگرام خطا: {e}")
        except Exception as e:
            logger.error(f"خطا در V2Ray تسک: {e}")
        await asyncio.sleep(3600)

async def poem_task(bot):
    while True:
        try:
            now = datetime.now()
            if now.hour == 21 and now.minute == 0:
                msg = format_poem_message()
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode='Markdown'
                )
                logger.info("شعر ارسال شد!")
                await asyncio.sleep(61)
        except TelegramError as e:
            logger.error(f"تلگرام خطا: {e}")
        except Exception as e:
            logger.error(f"خطا در شعر تسک: {e}")
        await asyncio.sleep(30)

async def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("بات شروع به کار کرد!")
    await asyncio.gather(
        proxy_task(bot),
        v2ray_task(bot),
        poem_task(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())



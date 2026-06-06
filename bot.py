import asyncio
import logging
import random
import requests
import socket
import base64
import json
import feedparser
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

TELEGRAM_CHANNELS_MTPROTO = [
    "ProxyMTProto", "proxy_ir", "mtpro_xyz",
    "exbta", "free_proxy_ru", "proxylist_ru",
    "configV2rayNG", "freev2ray"
]

TELEGRAM_CHANNELS_V2RAY = [
    "v2ray_configs", "vlessconfig", "vmessorg",
    "clash_config", "shadowsocks_ir", "freev2ray",
    "configV2rayNG"
]

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
    ("سعدی", "گر حکم شود که مست گیرند\nاول که دهند داد مستان"),
]

def get_mtproto_proxies():
    proxies = []
    try:
        url = "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies/mtproto"
        r = requests.get(url, headers=HEADERS, timeout=15)
        for line in r.text.strip().split('\n'):
            line = line.strip()
            if 'tg://proxy?' in line and 'secret=' in line:
                proxies.append({'type': 'MTProto', 'link': line})
    except Exception as e:
        logger.error(f"GitHub MTProto خطا: {e}")

    for channel in TELEGRAM_CHANNELS_MTPROTO:
        try:
            url = f"https://t.me/s/{channel}"
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            for msg in messages:
                links = msg.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if 'tg://proxy?' in href and 'secret=' in href:
                        proxies.append({'type': 'MTProto', 'link': href})
        except Exception as e:
            logger.error(f"خطا در {channel}: {e}")
    return proxies

def get_v2ray_configs():
    configs = []
    v2ray_sources = [
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
        "https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/Eternity.txt",
    ]
    for url in v2ray_sources:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            for line in r.text.strip().split('\n'):
                line = line.strip()
                if line.startswith('vmess://') or line.startswith('vless://') or line.startswith('trojan://'):
                    configs.append({'type': 'V2Ray', 'link': line})
        except Exception as e:
            logger.error(f"V2Ray GitHub خطا: {e}")

    for channel in TELEGRAM_CHANNELS_V2RAY:
        try:
            url = f"https://t.me/s/{channel}"
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            for msg in messages:
                text = msg.get_text()
                for line in text.split('\n'):
                    line = line.strip()
                    if line.startswith('vmess://') or line.startswith('vless://') or line.startswith('trojan://'):
                        configs.append({'type': 'V2Ray', 'link': line})
        except Exception as e:
            logger.error(f"خطا در {channel}: {e}")
    return configs

def extract_v2ray_address(config):
    """استخراج IP و پورت از کانفیگ V2Ray"""
    try:
        link = config['link']
        if link.startswith('vmess://'):
            decoded = base64.b64decode(link[8:] + '==').decode('utf-8')
            data = json.loads(decoded)
            return data.get('add', ''), int(data.get('port', 0))
        elif link.startswith('vless://') or link.startswith('trojan://'):
            part = link.split('://')[1]
            if '@' in part:
                addr_part = part.split('@')[1].split('?')[0].split('#')[0]
                if ':' in addr_part:
                    host, port = addr_part.rsplit(':', 1)
                    return host, int(port)
    except:
        pass
    return '', 0

def test_socket(host, port, timeout=5):
    """تست اتصال با socket"""
    try:
        if not host or not port:
            return False
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_mtproto(proxy):
    try:
        link = proxy['link']
        if 'server=' in link and 'port=' in link:
            server = link.split('server=')[1].split('&')[0]
            port = int(link.split('port=')[1].split('&')[0])
            return test_socket(server, port)
        return False
    except:
        return False

def test_v2ray(config):
    """تست V2Ray با socket"""
    host, port = extract_v2ray_address(config)
    if host and port:
        return test_socket(host, port)
    return False

def get_live_mtproto(proxies):
    live = []
    seen = set()
    unique = []
    for p in proxies:
        if p['link'] not in seen:
            seen.add(p['link'])
            unique.append(p)
    random.shuffle(unique)
    for proxy in unique[:30]:
        if test_mtproto(proxy):
            live.append(proxy)
        if len(live) >= 10:
            break
    return live

def get_live_v2ray(configs):
    """فیلتر V2Ray های زنده"""
    live = []
    seen = set()
    unique = []
    for c in configs:
        if c['link'] not in seen:
            seen.add(c['link'])
            unique.append(c)
    random.shuffle(unique)
    logger.info(f"تست {min(30, len(unique))} کانفیگ V2Ray...")
    for config in unique[:30]:
        if test_v2ray(config):
            live.append(config)
            logger.info("V2Ray زنده پیدا شد!")
        if len(live) >= 5:
            break
    return live

def get_news():
    news = []
    feeds = [
        ("ایران اینترنشنال", "https://www.iranintl.com/rss"),
        ("BBC فارسی", "https://feeds.bbci.co.uk/persian/rss.xml"),
        ("رادیو فردا", "https://www.radiofarda.com/api/zpdvqmiqte"),
        ("رویترز", "https://feeds.reuters.com/reuters/topNews"),
    ]
    for source, url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                news.append({
                    'source': source,
                    'title': entry.title,
                })
        except Exception as e:
            logger.error(f"خطا در RSS {source}: {e}")
    return news

def format_proxy_message(proxies):
    msg = "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "   🔰 I R A N  P R O X Y 🔰\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
    for i, proxy in enumerate(proxies[:5], 1):
        msg += f"💎 پروکسی {i}  —  MTProto\n"
        msg += f"╰─► [🔗 اتصال مستقیم]({proxy['link']})\n\n"
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
    selected = configs[:2]
    for i, config in enumerate(selected, 1):
        if config['link'].startswith('vmess'):
            config_type = "VMess"
        elif config['link'].startswith('vless'):
            config_type = "VLess"
        else:
            config_type = "Trojan"
        msg += f"💎 کانفیگ {i}  —  {config_type}\n"
        msg += f"`{config['link']}`\n\n"
    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
    msg += "✅ کانفیگ‌ها تست شده و زنده‌اند\n"
    msg += "📱 برای استفاده: V2RayNG یا Nekoray نصب کن\n"
    msg += "👥 کانال رو شیر کن و حمایت کن!\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━"
    return msg

def format_news_message(news):
    msg = "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "   📰 A X B A R  |  اخبار مهم\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    for item in news[:5]:
        msg += f"🔴 **{item['title']}**\n"
        msg += f"📌 منبع: {item['source']}\n\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "📢 کانال ما رو دنبال کن!"
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

async def proxy_task(bot):
    while True:
        try:
            logger.info("جمع‌آوری پروکسی MTProto...")
            all_proxies = get_mtproto_proxies()
            live = get_live_mtproto(all_proxies)
            if live:
                msg = format_proxy_message(live)
                await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
                logger.info("پروکسی ارسال شد!")
            else:
                logger.warning("پروکسی زنده پیدا نشد!")
        except Exception as e:
            logger.error(f"خطا در پروکسی: {e}")
        await asyncio.sleep(600)

async def v2ray_task(bot):
    while True:
        try:
            logger.info("جمع‌آوری V2Ray...")
            configs = get_v2ray_configs()
            live = get_live_v2ray(configs)
            if live:
                msg = format_v2ray_message(live)
                await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
                logger.info("V2Ray ارسال شد!")
            else:
                logger.warning("V2Ray زنده پیدا نشد!")
        except Exception as e:
            logger.error(f"خطا در V2Ray: {e}")
        await asyncio.sleep(3600)

async def news_task(bot):
    while True:
        try:
            logger.info("جمع‌آوری اخبار...")
            news = get_news()
            if news:
                msg = format_news_message(news)
                await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown', disable_web_page_preview=True)
                logger.info("اخبار ارسال شد!")
        except Exception as e:
            logger.error(f"خطا در اخبار: {e}")
        await asyncio.sleep(3600)

async def poem_task(bot):
    while True:
        now = datetime.now()
        if now.hour == 21 and now.minute < 1:
            try:
                msg = format_poem_message()
                await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode='Markdown')
                logger.info("شعر ارسال شد!")
            except Exception as e:
                logger.error(f"خطا در شعر: {e}")
            await asyncio.sleep(60)
        await asyncio.sleep(30)

async def main():
    bot = Bot(token=BOT_TOKEN)
    await asyncio.gather(
        proxy_task(bot),
        v2ray_task(bot),
        news_task(bot),
        poem_task(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())



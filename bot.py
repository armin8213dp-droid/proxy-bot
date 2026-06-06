import asyncio
import logging
import random
import requests
import socket
import feedparser
from bs4 import BeautifulSoup
from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime
import jdatetime

# ============================================
BOT_TOKEN = "8500441833:AAGgCPyFlvd7yvsU-sORfBT2P-OUW8VoqEs"
CHANNEL_ID = "-1003816897802"
# ============================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# کانال های تلگرامی
TELEGRAM_CHANNELS = [
    # ایرانی
    "ProxyMTProto", "proxy_ir", "shadowsocks_ir",
    "v2ray_configs", "freev2ray", "vlessconfig",
    # روسی
    "mtpro_xyz", "exbta", "proxy_socks5", "freeproxy_io",
    "proxy_ru", "rusproxy", "socksproxy", "proxysocks",
    "free_proxy_ru", "proxylist_ru",
    # بین المللی
    "configV2rayNG", "vmessorg", "clash_config"
]

# منابع GitHub
GITHUB_SOURCES = [
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies/mtproto",
    "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies/socks",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
]

# اشعار پند آموز
POEMS = [
    ("حافظ", "بیا که قصر امل سخت سست بنیاد است\nبیار باده که بنیاد عمر بر باد است"),
    ("سعدی", "بنی آدم اعضای یکدیگرند\nکه در آفرینش ز یک گوهرند"),
    ("مولانا", "آتش عشق است کاندر نی فتاد\nجوشش عشق است کاندر می فتاد"),
    ("فردوسی", "توانا بود هر که دانا بود\nز دانش دل پیر برنا بود"),
    ("سعدی", "هر که در خوابگه خاک آرمید\nرفت و آمد ز این جهان ببرید"),
    ("حافظ", "الا یا ایها الساقی ادر کاسا و ناولها\nکه عشق آسان نمود اول ولی افتاد مشکل‌ها"),
    ("مولانا", "من کجا بودم عجب کو بود من\nحیرت آمد حیرت آمد حیرتم"),
    ("خیام", "می خور که ز دل کثرت و قلت ببرد\nوین آب طربناک خجالت ببرد"),
    ("سعدی", "گر حکم شود که مست گیرند\nاول که دهند داد مستان"),
    ("حافظ", "شراب تلخ می‌خواهم که مرد افکن بود زورش\nکه تا یک دم بیاسایم ز دنیا و شر و شورش"),
]

def get_proxies_from_telegram():
    proxies = []
    for channel in TELEGRAM_CHANNELS:
        try:
            url = f"https://t.me/s/{channel}"
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            for msg in messages:
                text = msg.get_text()
                links = msg.find_all('a')
                for link in links:
                    href = link.get('href', '')
                    if 'tg://proxy?' in href:
                        proxies.append({'type': 'MTProto', 'link': href})
                    elif 'tg://socks?' in href:
                        proxies.append({'type': 'SOCKS5', 'link': href})
                if 'tg://proxy?' in text:
                    for part in text.split():
                        if part.startswith('tg://proxy?'):
                            proxies.append({'type': 'MTProto', 'link': part})
                if 'tg://socks?' in text:
                    for part in text.split():
                        if part.startswith('tg://socks?'):
                            proxies.append({'type': 'SOCKS5', 'link': part})
            logger.info(f"کانال {channel}: {len(proxies)} پروکسی")
        except Exception as e:
            logger.error(f"خطا در {channel}: {e}")
    return proxies

def get_proxies_from_github():
    proxies = []
    for url in GITHUB_SOURCES:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            for line in r.text.strip().split('\n'):
                line = line.strip()
                if 'tg://proxy?' in line:
                    proxies.append({'type': 'MTProto', 'link': line})
                elif 'tg://socks?' in line:
                    proxies.append({'type': 'SOCKS5', 'link': line})
                elif ':' in line and not line.startswith('#'):
                    parts = line.split(':')
                    if len(parts) == 2:
                        ip, port = parts
                        try:
                            socket.inet_aton(ip)
                            proxies.append({
                                'type': 'SOCKS5',
                                'server': ip,
                                'port': port,
                                'link': f"tg://socks?server={ip}&port={port}"
                            })
                        except:
                            pass
        except Exception as e:
            logger.error(f"GitHub خطا: {e}")
    return proxies

def test_proxy(proxy):
    try:
        if 'server' in proxy:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((proxy['server'], int(proxy['port'])))
            sock.close()
            return result == 0
        return True
    except:
        return False

def get_live_proxies(all_proxies):
    live = []
    random.shuffle(all_proxies)
    for proxy in all_proxies[:50]:
        if test_proxy(proxy):
            live.append(proxy)
        if len(live) >= 10:
            break
    return live

def get_news():
    news = []
    feeds = [
        ("BBC فارسی", "https://feeds.bbci.co.uk/persian/rss.xml"),
        ("ایران اینترنشنال", "https://www.iranintl.com/rss"),
        ("رویترز", "https://feeds.reuters.com/reuters/topNews"),
    ]
    for source, url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                news.append({
                    'source': source,
                    'title': entry.title,
                    'link': entry.link
                })
        except Exception as e:
            logger.error(f"خطا در RSS {source}: {e}")
    return news

def format_proxy_message(proxies):
    now = datetime.now()
    jdate = jdatetime.datetime.fromgregorian(datetime=now).strftime("%Y/%m/%d")
    time_str = now.strftime("%H:%M")

    msg = "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "   🔰 I R A N  P R O X Y 🔰\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🕐 {time_str}  |  📅 {jdate}\n\n"
    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"

    selected = proxies[:5]
    for i, proxy in enumerate(selected, 1):
        if proxy['type'] == 'MTProto':
            msg += f"💎 پروکسی {i}  —  MTProto\n"
            msg += f"╰─► [🔗 اتصال مستقیم]({proxy['link']})\n\n"
        else:
            msg += f"💎 پروکسی {i}  —  SOCKS5\n"
            if 'server' in proxy:
                msg += f"🌐 `{proxy['server']}:{proxy['port']}`\n"
            msg += f"╰─► [🔗 اتصال مستقیم]({proxy['link']})\n\n"

    msg += "▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n\n"
    msg += "🔄 آپدیت بعدی: ۱۰ دقیقه دیگه\n"
    msg += "👥 کانال رو شیر کن و حمایت کن!\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━"
    return msg

def format_news_message(news):
    now = datetime.now()
    time_str = now.strftime("%H:%M")

    msg = "━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "   📰 A X B A R  |  اخبار مهم\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🕐 {time_str}\n\n"

    for item in news[:5]:
        msg += f"🔴 **{item['title']}**\n"
        msg += f"📌 منبع: {item['source']}\n"
        msg += f"╰─► [🔗 ادامه خبر]({item['link']})\n\n"

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
            logger.info("جمع‌آوری پروکسی...")
            all_proxies = get_proxies_from_telegram() + get_proxies_from_github()
            logger.info(f"کل پروکسی: {len(all_proxies)}")
            live = get_live_proxies(all_proxies)
            logger.info(f"پروکسی زنده: {len(live)}")
            if live:
                msg = format_proxy_message(live)
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("پروکسی ارسال شد!")
            else:
                logger.warning("پروکسی زنده پیدا نشد!")
        except Exception as e:
            logger.error(f"خطا در پروکسی: {e}")
        await asyncio.sleep(600)

async def news_task(bot):
    while True:
        try:
            logger.info("جمع‌آوری اخبار...")
            news = get_news()
            if news:
                msg = format_news_message(news)
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode='Markdown',
                    disable_web_page_preview=True
                )
                logger.info("اخبار ارسال شد!")
        except Exception as e:
            logger.error(f"خطا در اخبار: {e}")
        await asyncio.sleep(3600)

async def poem_task(bot):
    while True:
        now = datetime.now()
        # هر شب ساعت 21
        if now.hour == 21 and now.minute == 0:
            try:
                msg = format_poem_message()
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=msg,
                    parse_mode='Markdown'
                )
                logger.info("شعر ارسال شد!")
            except Exception as e:
                logger.error(f"خطا در شعر: {e}")
            await asyncio.sleep(60)
        await asyncio.sleep(30)

async def main():
    bot = Bot(token=BOT_TOKEN)
    await asyncio.gather(
        proxy_task(bot),
        news_task(bot),
        poem_task(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())


import os
import time
import requests
from bs4 import BeautifulSoup

TOKEN   = os.environ.get("TG_TOKEN", "8935698700:AAF8xiDXD4aq9w24zQzX1ugDGPst3K2KHiQ")
CHAT_ID = os.environ.get("TG_CHAT",  "7526922234")
URL     = "https://tvgfbf.gov.tr/duyurular"
INTERVAL = 900  # 15 dakikada bir kontrol

KW_IZMIR = ["izmir", "İzmir", "IZMIR", "İZMİR"]
KW_KURS  = ["1. kademe", "1.kademe", "1. Kademe", "birinci kademe"]

def send_telegram(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram hatası: {e}")

def check():
    try:
        r = requests.get(URL, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        html = r.text
    except Exception as e:
        print(f"Site alınamadı: {e}")
        return False

    has_izmir = any(k in html for k in KW_IZMIR)
    has_kurs  = any(k.lower() in html.lower() for k in KW_KURS)

    if has_izmir and has_kurs:
        # Başlığı bulmaya çalış
        try:
            soup = BeautifulSoup(html, "html.parser")
            links = soup.find_all("a", href=True)
            title = "İzmir 1. Kademe Antrenörlük Kursu duyurusu yayınlandı!"
            for a in links:
                text = a.get_text(strip=True)
                if any(k in text for k in KW_IZMIR) and any(k.lower() in text.lower() for k in KW_KURS):
                    title = text
                    break
        except:
            title = "İzmir 1. Kademe Antrenörlük Kursu duyurusu yayınlandı!"

        msg = (
            f"🎉 <b>İZMİR 1. KADEME KURS AÇILDI!</b>\n\n"
            f"{title}\n\n"
            f"🔗 {URL}"
        )
        send_telegram(msg)
        print(f"KURS BULUNDU: {title}")
        return True

    print(f"Kontrol tamam — İzmir kursu yok ({time.strftime('%H:%M:%S')})")
    return False

# Başlangıç mesajı
send_telegram("✅ <b>TVGFBF İzleyici başlatıldı!</b>\n\nİzmir 1. Kademe kurs duyurusu çıkınca buraya mesaj gelecek.\n\n⏱ Her 15 dakikada bir kontrol ediyorum.")
print("Bot başlatıldı.")

while True:
    found = check()
    if found:
        # Kurs bulundu, tekrar bildirim gönderme — 6 saatte bir hatırlat
        time.sleep(21600)
    else:
        time.sleep(INTERVAL)

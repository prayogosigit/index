import os
import re
import time
import json
from instagrapi import Client
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")
URLS_RAW = os.getenv("IG_URLS", "")
SESSION_FILE = "session/ig_session.json"

# Set OpenAI API key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_comment_from_caption(caption):
    """
    Generate a comment from the given caption using OpenAI ChatGPT API.
    """
    prompt = f"""Tolong buat komentar singkat yang pakai bahasa sehari-hari, santai, tidak terlalu baku. Jangan gunakan:
- kata "wah"
- hashtag
- emoji

Caption:
\"{caption}\"

Komentar:"""
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Kamu adalah orang Indonesia biasa yang suka kasih komentar santai dan positif di Instagram."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7,
            n=1
        )
        comment = response.choices[0].message.content.strip()
        if comment:
            return comment
    except Exception as e:
        print(f"[!] Gagal generate komentar AI: {e}")
    # Fallback default comment
    return "Keren banget! 👍"

cl = Client()

def login():
    if os.path.exists(SESSION_FILE) and os.path.getsize(SESSION_FILE) > 0:
        print("[i] Memuat sesi login...")
        with open(SESSION_FILE, "r") as f:
            try:
                settings = json.load(f)
                cl.set_settings(settings)
                cl.login(USERNAME, PASSWORD)
                print("[✓] Berhasil login dengan sesi tersimpan.")
                return
            except Exception as e:
                print(f"[!] Gagal login dengan sesi lama: {e}")
                os.remove(SESSION_FILE)

    print("[i] Login pertama kali...")
    try:
        cl.login(USERNAME, PASSWORD)
    except Exception as e:
        if "TwoFactorRequired" in str(type(e)):
            code = input("Masukkan kode 2FA (6 digit): ")
            cl.login(USERNAME, PASSWORD, verification_code=code)
        else:
            raise e

    with open(SESSION_FILE, "w") as f:
        json.dump(cl.get_settings(), f)
    print("[✓] Login berhasil dan sesi disimpan.")

def extract_shortcode(url):
    match = re.search(r"instagram\.com/(p|reel)/([A-Za-z0-9_-]+)", url)
    return match.group(2) if match else None

# Fungsi untuk follow user jika belum difollow
def follow_if_not_following(url):
    try:
        media_id = cl.media_pk_from_url(url)
        media_info = cl.media_info(media_id)
        user = media_info.user
        user_id = user.pk
        username = user.username
        is_following = user.following
        if not is_following:
            cl.user_follow(user_id)
            print(f"[+] Followed user: {username}")
        else:
            print(f"[=] Sudah follow user: {username}")
    except Exception as e:
        print(f"[!] Gagal follow user dari {url}: {e}")

def auto_like(urls, delay=10):
    for url in urls:
        shortcode = extract_shortcode(url)
        if not shortcode:
            print(f"[!] URL tidak valid: {url}")
            continue

        try:
            media_id = cl.media_pk_from_url(url)
            cl.media_like(media_id)
            print(f"[✓] Berhasil like: {url}")
            # Ambil info media & caption, generate komentar, lalu komen
            media_info = cl.media_info(media_id)
            caption = getattr(media_info, "caption_text", "") if hasattr(media_info, "caption_text") else ""
            print(f"[i] Caption: {caption}")
            comment = generate_comment_from_caption(caption)
            print(f"[i] Generated comment: {comment}")
            try:
                cl.media_comment(media_id, comment)
                print(f"[💬] Berhasil komen: {comment}")
            except Exception as e:
                print(f"[!] Gagal komen: {e}")
            follow_if_not_following(url)
        except Exception as e:
            print(f"[x] Gagal like {url} - {e}")
        
        print(f"[i] Tunggu {delay} detik sebelum lanjut ke URL berikutnya...")
        time.sleep(delay)

if __name__ == "__main__":
    if not USERNAME or not PASSWORD or not URLS_RAW:
        print("❌ IG_USERNAME, IG_PASSWORD, atau IG_URLS belum di-set di .env")
        exit(1)

    url_list = [u.strip() for u in URLS_RAW.split(",") if u.strip()]
    login()
    auto_like(url_list, delay=10)

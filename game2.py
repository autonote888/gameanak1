import pygame
import random
import sys
import os

# 1. Inisialisasi & Path
pygame.init()
skrip_dir = os.path.dirname(__file__) 
os.chdir(skrip_dir) 

# --- PENYESUAIAN LAYAR ANDROID (PORTRAIT) ---
# Menggunakan rasio 9:16 yang umum di HP
LEBAR, TINGGI = 450, 800 
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("🎣 Mancing Mania Mobile")

# --- FUNGSI LOAD GAMBAR ---
def muat_aset(nama_file, ukuran):
    path_lengkap = os.path.join(skrip_dir, nama_file)
    if os.path.exists(path_lengkap):
        try:
            img = pygame.image.load(path_lengkap)
            if nama_file.endswith('.png'): img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey((255, 255, 255)) 
            return pygame.transform.scale(img, ukuran)
        except: return None
    return None

# 2. Muat Aset (Ukuran disesuaikan untuk layar HP yang lebih kecil)
ASET = {
    "ikan": muat_aset('ikan.png', (50, 35)),
    "buaya": muat_aset('buaya.png', (100, 45)),
    "kudanil": muat_aset('kudanil.png', (90, 65)),
    "ular": muat_aset('ular.png', (120, 50)), 
    "kepiting": muat_aset('kepiting.png', (45, 35)),
    "kudalaut": muat_aset('kudalaut.png', (30, 45)),
    "hiu": muat_aset('hiu.png', (120, 60)),
    "pausorca": muat_aset('pausorca.png', (140, 75)),
    "lumba-lumba": muat_aset('lumba-lumba.png', (90, 55)),
    "zombi1": muat_aset('zombi1.png', (70, 85)),
    "zombi2": muat_aset('zombi2.png', (70, 85)),
    "virus": muat_aset('virus.png', (50, 50))
}
GAMBAR_PEMANCING = muat_aset('pemancing.jpg', (100, 100))

# Warna & Font
BIRU_LANGIT = (173, 216, 230); AIR = (0, 191, 255); PASIR = (255, 239, 184)
PUTIH = (255, 255, 255); HITAM = (0, 0, 0); MERAH = (200, 0, 0); HIJAU = (0, 150, 0)
font_skor = pygame.font.SysFont("Comic Sans MS", 18, bold=True)
font_tombol = pygame.font.SysFont("Arial", 24, bold=True)

# 3. Variabel Game & Tata Letak
statistik = {k: 0 for k in ASET.keys()}
biota_list = []
permukaan_air = 320    
game_pause = False # Status Pause

# Tombol Rect
btn_stop = pygame.Rect(LEBAR - 110, 20, 90, 40)
btn_lanjut = pygame.Rect(LEBAR // 2 - 75, TINGGI // 2 - 25, 150, 50)

def buat_biota():
    jenis = random.choice(list(ASET.keys()))
    sisi = random.choice(["kiri", "kanan"])
    y = 750 if jenis == "kepiting" else random.randint(permukaan_air + 50, 750)
    x = -200 if sisi == "kiri" else LEBAR + 200
    arah = 1 if sisi == "kiri" else -1
    
    if ASET[jenis]: rect = ASET[jenis].get_rect()
    else: rect = pygame.Rect(0, 0, 50, 35)
    
    rect.topleft = (x, y)
    return {"rect": rect, "jenis": jenis, "arah": arah, "speed": random.randint(2, 4), "melompat": False, "v_y": 0, "y_awal": y, "rotasi": 0}

for _ in range(10): biota_list.append(buat_biota())

kedalaman_kail = permukaan_air
sedang_mancing = False; kail_turun = False; objek_didapat = None
clock = pygame.time.Clock()

# --- LOOP UTAMA ---
while True:
    layar.fill(BIRU_LANGIT)
    mx, my = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Cek klik tombol Stop
            if btn_stop.collidepoint(mx, my):
                game_pause = True
            # Cek klik tombol Lanjut (saat pause)
            elif game_pause and btn_lanjut.collidepoint(mx, my):
                game_pause = False
            # Logika mancing (hanya jika tidak sedang pause)
            elif not game_pause and not sedang_mancing:
                kail_turun = True; sedang_mancing = True

    if not game_pause:
        # --- LOGIKA GAME JALAN ---
        ujung_x, ujung_y = mx + 55, permukaan_air - 80

        if sedang_mancing:
            if kail_turun:
                kedalaman_kail += 10
                if kedalaman_kail >= 780: kail_turun = False
            else:
                kedalaman_kail -= 14
                if objek_didapat: objek_didapat["rect"].center = (ujung_x, kedalaman_kail + 15)
                if kedalaman_kail <= permukaan_air:
                    if objek_didapat: statistik[objek_didapat["jenis"]] += 1; objek_didapat = None
                    sedang_mancing = False; kedalaman_kail = permukaan_air

        for b in biota_list[:]:
            b["rect"].x += b["arah"] * b["speed"]
            # Fisika lompat sederhana
            if not b["melompat"] and b["jenis"] != "kepiting" and random.random() < 0.003:
                b["melompat"] = True; b["v_y"] = -14; b["y_awal"] = b["rect"].y
            if b["melompat"]:
                b["rect"].y += b["v_y"]; b["v_y"] += 0.8
                if b["rect"].y >= b["y_awal"]: b["rect"].y = b["y_awal"]; b["melompat"] = False
            
            # Tabrakan
            kail_hitbox = pygame.Rect(ujung_x - 10, kedalaman_kail, 20, 20)
            if not objek_didapat and sedang_mancing and kail_hitbox.colliderect(b["rect"]):
                objek_didapat = b; biota_list.remove(b); biota_list.append(buat_biota()); kail_turun = False
            
            if b["rect"].x > LEBAR + 300 or b["rect"].x < -300:
                biota_list.remove(b); biota_list.append(buat_biota())

    # --- DRAWING ---
    pygame.draw.rect(layar, AIR, (0, permukaan_air, LEBAR, 500)) 
    pygame.draw.rect(layar, PASIR, (0, 780, LEBAR, 25)) 
    
    # Nelayan & Pancing
    ujung_x = mx + 55
    pygame.draw.line(layar, PUTIH, (ujung_x, permukaan_air-80), (ujung_x, kedalaman_kail), 2)
    if GAMBAR_PEMANCING: layar.blit(GAMBAR_PEMANCING, (mx - 50, permukaan_air - 100))
    
    # Biota
    for b in biota_list:
        img_base = ASET[b["jenis"]]
        if img_base:
            img = img_base if b["arah"] == 1 else pygame.transform.flip(img_base, True, False)
            layar.blit(img, b["rect"])
    if objek_didapat and ASET[objek_didapat["jenis"]]:
        layar.blit(ASET[objek_didapat["jenis"]], objek_didapat["rect"])

    # Papan Skor Mobile
    pygame.draw.rect(layar, PUTIH, (10, 10, 300, 150), border_radius=10)
    sx, sy = 25, 20
    for i, (jenis, jml) in enumerate(list(statistik.items())[:6]): # Tampilkan 6 teratas agar tidak penuh
        if ASET[jenis]: layar.blit(pygame.transform.scale(ASET[jenis], (30, 20)), (sx, sy))
        layar.blit(font_skor.render(f": {jml}", True, HITAM), (sx + 40, sy - 5))
        sy += 22
        if (i+1) % 3 == 0: sx += 100; sy = 20

    # Tombol Stop (Pojok Kanan)
    pygame.draw.rect(layar, MERAH, btn_stop, border_radius=8)
    layar.blit(font_tombol.render("STOP", True, PUTIH), (btn_stop.x + 10, btn_stop.y + 5))

    # Layar Pause
    if game_pause:
        s = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150)) # Overlay gelap
        layar.blit(s, (0,0))
        pygame.draw.rect(layar, HIJAU, btn_lanjut, border_radius=12)
        layar.blit(font_tombol.render("LANJUT", True, PUTIH), (btn_lanjut.x + 30, btn_lanjut.y + 10))

    pygame.display.flip()
    clock.tick(60)
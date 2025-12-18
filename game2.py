import pygame
import random
import sys
import os

# 1. Inisialisasi & Path (Sistem Baru Anti-Error)
pygame.init()
# Mengambil path folder tempat skrip berada tanpa berpindah direktori (os.chdir)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# --- PENYESUAIAN LAYAR ANDROID (PORTRAIT) ---
LEBAR, TINGGI = 450, 800 
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("🎣 Mancing Mania Mobile")

# --- FUNGSI LOAD GAMBAR AMAN (MENGGUNAKAN PATH ABSOLUT) ---
def muat_aset(nama_file, ukuran):
    path_lengkap = os.path.join(BASE_PATH, nama_file)
    if os.path.exists(path_lengkap):
        try:
            img = pygame.image.load(path_lengkap)
            if nama_file.endswith('.png'): 
                img = img.convert_alpha()
            else:
                img = img.convert()
                img.set_colorkey((255, 255, 255)) 
            return pygame.transform.scale(img, ukuran)
        except Exception as e:
            print(f"Error loading {nama_file}: {e}")
            return None
    return None

# 2. Muat Aset (Ukuran Skor diperbesar untuk Anak-anak)
ASET = {
    "ikan": muat_aset('ikan.png', (50, 35)),
    "buaya": muat_aset('buaya.png', (100, 45)),
    "kudanil": muat_aset('kudanil.png', (90, 65)),
    "ular": muat_aset('ular.png', (130, 50)), 
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

# Warna & Font (Diperbesar untuk Anak)
BIRU_LANGIT = (173, 216, 230); AIR = (0, 191, 255); PASIR = (255, 239, 184)
PUTIH = (255, 255, 255); HITAM = (0, 0, 0); MERAH = (200, 0, 0); HIJAU = (0, 150, 0)
font_skor_besar = pygame.font.SysFont("Comic Sans MS", 24, bold=True)
font_tombol = pygame.font.SysFont("Arial", 28, bold=True)

# 3. Variabel Game
statistik = {k: 0 for k in ASET.keys()}
biota_list = []
permukaan_air = 350 # Nelayan diturunkan agar tidak tertutup skor
game_pause = False 

# Tombol Mobile (Lebar)
btn_stop = pygame.Rect(LEBAR - 110, 20, 90, 50)
btn_lanjut = pygame.Rect(LEBAR // 2 - 80, TINGGI // 2 - 30, 160, 60)

def buat_biota():
    jenis = random.choice(list(ASET.keys()))
    sisi = random.choice(["kiri", "kanan"])
    y = 750 if jenis == "kepiting" else random.randint(permukaan_air + 80, 750)
    x = -200 if sisi == "kiri" else LEBAR + 200
    arah = 1 if sisi == "kiri" else -1
    return {"rect": pygame.Rect(x, y, 60, 45), "jenis": jenis, "arah": arah, "speed": random.randint(2, 4)}

for _ in range(12): biota_list.append(buat_biota())

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
            if btn_stop.collidepoint(mx, my):
                game_pause = True
            elif game_pause and btn_lanjut.collidepoint(mx, my):
                game_pause = False
            elif not game_pause and not sedang_mancing:
                kail_turun = True; sedang_mancing = True

    if not game_pause:
        ujung_x = mx + 55
        if sedang_mancing:
            if kail_turun:
                kedalaman_kail += 12
                if kedalaman_kail >= 780: kail_turun = False
            else:
                kedalaman_kail -= 16
                if objek_didapat: objek_didapat["rect"].center = (ujung_x, kedalaman_kail + 20)
                if kedalaman_kail <= permukaan_air:
                    if objek_didapat: statistik[objek_didapat["jenis"]] += 1; objek_didapat = None
                    sedang_mancing = False; kedalaman_kail = permukaan_air

        for b in biota_list:
            b["rect"].x += b["arah"] * b["speed"]
            if b["rect"].x > LEBAR + 300 or b["rect"].x < -300:
                b["rect"].x = -200 if b["arah"] == 1 else LEBAR + 200
            
            # Hitbox Kail diperbesar agar mudah untuk anak
            kail_rect = pygame.Rect(ujung_x - 15, kedalaman_kail, 30, 30)
            if not objek_didapat and sedang_mancing and kail_rect.colliderect(b["rect"]):
                objek_didapat = b; biota_list.remove(b); biota_list.append(buat_biota()); kail_turun = False

    # --- DRAWING ---
    pygame.draw.rect(layar, AIR, (0, permukaan_air, LEBAR, 500)) 
    pygame.draw.line(layar, PUTIH, (mx+55, permukaan_air-80), (mx+55, kedalaman_kail), 2)
    
    if GAMBAR_PEMANCING: 
        layar.blit(GAMBAR_PEMANCING, (mx - 50, permukaan_air - 100))
    
    for b in biota_list:
        img = ASET[b["jenis"]]
        if img:
            render = img if b["arah"] == 1 else pygame.transform.flip(img, True, False)
            layar.blit(render, b["rect"])

    # Papan Skor (Diperbesar & Font Lebih Jelas)
    pygame.draw.rect(layar, PUTIH, (10, 10, 320, 180), border_radius=15)
    sx, sy = 25, 25
    for i, (jenis, jml) in enumerate(list(statistik.items())[:8]): # Menampilkan 8 hewan agar anak senang
        if ASET[jenis]:
            layar.blit(pygame.transform.scale(ASET[jenis], (40, 30)), (sx, sy))
        txt = font_skor_besar.render(f": {jml}", True, HITAM)
        layar.blit(txt, (sx + 45, sy - 5))
        sy += 40
        if (i+1) % 4 == 0: sx += 140; sy = 25

    # Tombol STOP
    pygame.draw.rect(layar, MERAH, btn_stop, border_radius=12)
    layar.blit(font_tombol.render("STOP", True, PUTIH), (btn_stop.x + 10, btn_stop.y + 8))

    if game_pause:
        overlay = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        layar.blit(overlay, (0,0))
        pygame.draw.rect(layar, HIJAU, btn_lanjut, border_radius=15)
        layar.blit(font_tombol.render("LANJUT", True, PUTIH), (btn_lanjut.x + 25, btn_lanjut.y + 12))

    pygame.display.flip()
    clock.tick(60)

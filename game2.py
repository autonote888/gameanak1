import pygame
import random
import sys
import os

# 1. Inisialisasi & Path Absolut (Penting untuk Cloud & Lokal)
pygame.init()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# --- SETINGAN LAYAR PORTRAIT ANDROID ---
LEBAR, TINGGI = 450, 850 
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("🎣 Mancing Mania Mobile V2")

# --- FUNGSI MUAT GAMBAR AMAN ---
def muat_aset(nama_file, ukuran):
    path_lengkap = os.path.join(BASE_PATH, nama_file)
    if os.path.exists(path_lengkap):
        try:
            img = pygame.image.load(path_lengkap)
            # Menghapus warning iCCP dengan convert
            img = img.convert_alpha() if nama_file.endswith('.png') else img.convert()
            if not nama_file.endswith('.png'): img.set_colorkey((255, 255, 255))
            return pygame.transform.scale(img, ukuran)
        except Exception:
            return None
    return None

# 2. Daftar Aset Lengkap (Termasuk Zombie & Virus)
ASET = {
    "ikan": muat_aset('ikan.png', (55, 40)),
    "buaya": muat_aset('buaya.png', (110, 55)),
    "kudanil": muat_aset('kudanil.png', (100, 75)),
    "ular": muat_aset('ular.png', (135, 60)), 
    "hiu": muat_aset('hiu.png', (145, 75)),
    "pausorca": muat_aset('pausorca.png', (170, 95)),
    "lumba-lumba": muat_aset('lumba-lumba.png', (100, 60)),
    "zombi1": muat_aset('zombi1.png', (85, 110)),
    "zombi2": muat_aset('zombi2.png', (85, 110)),
    "virus": muat_aset('virus.png', (65, 65))
}
GAMBAR_PEMANCING = muat_aset('pemancing.jpg', (120, 120))

# --- PERBAIKAN FONT (ANTI-ERROR) ---
# Menggunakan None agar Pygame menggunakan font internal sistem yang tersedia
font_skor = pygame.font.SysFont(None, 32)
font_tombol = pygame.font.SysFont(None, 45)

# 3. Variabel Game
statistik = {k: 0 for k in ASET.keys()}
biota_list = []
permukaan_air = 380 
game_pause = False 

btn_stop = pygame.Rect(LEBAR - 100, 20, 80, 45)
btn_lanjut = pygame.Rect(LEBAR // 2 - 75, TINGGI // 2 - 25, 150, 50)

def buat_biota():
    jenis = random.choice(list(ASET.keys()))
    sisi = random.choice(["kiri", "kanan"])
    y = 800 if jenis == "kepiting" else random.randint(permukaan_air + 80, 780)
    x = -250 if sisi == "kiri" else LEBAR + 250
    arah = 1 if sisi == "kiri" else -1
    return {"rect": pygame.Rect(x, y, 70, 50), "jenis": jenis, "arah": arah, "speed": random.randint(2, 5)}

for _ in range(12): biota_list.append(buat_biota())

kedalaman_kail = permukaan_air
sedang_mancing = False; kail_turun = False; objek_didapat = None
clock = pygame.time.Clock()

# --- LOOP UTAMA ---
while True:
    layar.fill((173, 216, 230)) # Langit
    mx, my = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_stop.collidepoint(mx, my): game_pause = True
            elif game_pause and btn_lanjut.collidepoint(mx, my): game_pause = False
            elif not game_pause and not sedang_mancing: kail_turun = True; sedang_mancing = True

    if not game_pause:
        # Logika Mancing
        ujung_x = mx + 65
        if sedang_mancing:
            if kail_turun:
                kedalaman_kail += 12
                if kedalaman_kail >= 810: kail_turun = False
            else:
                kedalaman_kail -= 18
                if objek_didapat: objek_didapat["rect"].center = (ujung_x, kedalaman_kail + 20)
                if kedalaman_kail <= permukaan_air:
                    if objek_didapat: statistik[objek_didapat["jenis"]] += 1; objek_didapat = None
                    sedang_mancing = False; kedalaman_kail = permukaan_air

        # Logika Biota
        for b in biota_list:
            b["rect"].x += b["arah"] * b["speed"]
            if b["rect"].x > LEBAR + 350 or b["rect"].x < -350:
                b["rect"].x = -250 if b["arah"] == 1 else LEBAR + 250
            
            kail_rect = pygame.Rect(ujung_x - 15, kedalaman_kail, 30, 30)
            if not objek_didapat and sedang_mancing and kail_rect.colliderect(b["rect"]):
                objek_didapat = b; kail_turun = False

    # --- GAMBAR ---
    pygame.draw.rect(layar, (0, 191, 255), (0, permukaan_air, LEBAR, 600)) # Laut
    pygame.draw.line(layar, (255, 255, 255), (mx + 65, permukaan_air - 95), (mx + 65, kedalaman_kail), 2)
    
    if GAMBAR_PEMANCING: 
        layar.blit(GAMBAR_PEMANCING, (mx - 60, permukaan_air - 115))
    
    for b in biota_list:
        img = ASET[b["jenis"]]
        if img:
            render = img if b["arah"] == 1 else pygame.transform.flip(img, True, False)
            layar.blit(render, b["rect"])

    # UI Papan Skor (3 Kolom x 4 Baris agar muat semua)
    pygame.draw.rect(layar, (255, 255, 255), (10, 10, 320, 200), border_radius=15)
    sx, sy = 25, 25
    for i, (jenis, jml) in enumerate(list(statistik.items())):
        if ASET[jenis]:
            layar.blit(pygame.transform.scale(ASET[jenis], (40, 30)), (sx, sy))
        txt = font_skor.render(f": {jml}", True, (0,0,0))
        layar.blit(txt, (sx + 45, sy - 5))
        sy += 42
        if (i+1) % 4 == 0: sx += 140; sy = 25

    # Tombol STOP
    pygame.draw.rect(layar, (200, 0, 0), btn_stop, border_radius=10)
    layar.blit(font_tombol.render("STOP", True, (255,255,255)), (btn_stop.x + 5, btn_stop.y + 10))

    if game_pause:
        overlay = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        layar.blit(overlay, (0,0))
        pygame.draw.rect(layar, (0, 150, 0), btn_lanjut, border_radius=15)
        layar.blit(font_tombol.render("RESUME", True, (255,255,255)), (btn_lanjut.x + 15, btn_lanjut.y + 10))

    pygame.display.flip()
    clock.tick(60)

import pygame
import random
import sys
import os
import math

# 1. Inisialisasi & Path
pygame.init()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

LEBAR, TINGGI = 450, 800 
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("🎣 Mancing Mania Mobile V2")

def muat_aset(nama_file, ukuran):
    path_lengkap = os.path.join(BASE_PATH, nama_file)
    if os.path.exists(path_lengkap):
        try:
            img = pygame.image.load(path_lengkap)
            img = img.convert_alpha() if nama_file.endswith('.png') else img.convert()
            if not nama_file.endswith('.png'): img.set_colorkey((255, 255, 255))
            return pygame.transform.scale(img, ukuran)
        except: return None
    return None

# 2. Aset & Variabel
ASET = {
    "ikan": muat_aset('ikan.png', (55, 40)),
    "buaya": muat_aset('buaya.png', (110, 50)),
    "kudanil": muat_aset('kudanil.png', (100, 70)),
    "ular": muat_aset('ular.png', (130, 55)), 
    "hiu": muat_aset('hiu.png', (140, 70)),
    "pausorca": muat_aset('pausorca.png', (160, 90)),
    "zombi1": muat_aset('zombi1.png', (80, 100)),
    "zombi2": muat_aset('zombi2.png', (80, 100)),
    "virus": muat_aset('virus.png', (60, 60))
}
GAMBAR_PEMANCING = muat_aset('pemancing.jpg', (110, 110))

# Font (Gunakan font default agar anti-error di semua sistem)
font_skor = pygame.font.SysFont(None, 30)
font_tombol = pygame.font.SysFont(None, 40)

statistik = {k: 0 for k in ASET.keys()}
biota_list = []
gelembung_list = []
permukaan_air = 360
game_pause = False 
offset_gelombang = 0

# Tombol
btn_stop = pygame.Rect(LEBAR - 100, 20, 80, 45)
btn_lanjut = pygame.Rect(LEBAR // 2 - 75, TINGGI // 2 - 25, 150, 50)

def buat_biota():
    jenis = random.choice(list(ASET.keys()))
    sisi = random.choice(["kiri", "kanan"])
    y = random.randint(permukaan_air + 60, 740)
    x = -200 if sisi == "kiri" else LEBAR + 200
    arah = 1 if sisi == "kiri" else -1
    return {"rect": pygame.Rect(x, y, 70, 50), "jenis": jenis, "arah": arah, "speed": random.randint(2, 5)}

def buat_gelembung():
    return {"x": random.randint(0, LEBAR), "y": TINGGI, "r": random.randint(2, 5), "speed": random.uniform(1, 3)}

for _ in range(12): biota_list.append(buat_biota())
for _ in range(15): gelembung_list.append(buat_gelembung())

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
        # 1. Animasi Gelombang
        offset_gelombang += 0.05
        
        # 2. Animasi Gelembung
        for g in gelembung_list:
            g["y"] -= g["speed"]
            if g["y"] < permukaan_air: 
                g["y"] = TINGGI; g["x"] = random.randint(0, LEBAR)

        # 3. Logika Pancing
        ujung_x = mx + 60
        if sedang_mancing:
            if kail_turun:
                kedalaman_kail += 12
                if kedalaman_kail >= 770: kail_turun = False
            else:
                kedalaman_kail -= 16
                if objek_didapat: objek_didapat["rect"].center = (ujung_x, kedalaman_kail + 20)
                if kedalaman_kail <= permukaan_air:
                    if objek_didapat: statistik[objek_didapat["jenis"]] += 1; objek_didapat = None
                    sedang_mancing = False; kedalaman_kail = permukaan_air

        # 4. Logika Biota
        for b in biota_list:
            b["rect"].x += b["arah"] * b["speed"]
            # Efek goyang sedikit (sinusoidal)
            b["rect"].y += math.sin(pygame.time.get_ticks() * 0.005 + b["rect"].x) * 0.5
            
            if b["rect"].x > LEBAR + 300 or b["rect"].x < -300:
                b["rect"].x = -200 if b["arah"] == 1 else LEBAR + 200
            
            kail_hitbox = pygame.Rect(ujung_x - 15, kedalaman_kail, 30, 30)
            if not objek_didapat and sedang_mancing and kail_hitbox.colliderect(b["rect"]):
                objek_didapat = b; kail_turun = False

    # --- DRAWING ---
    # Draw Air
    pygame.draw.rect(layar, (0, 191, 255), (0, permukaan_air, LEBAR, 500))
    
    # Draw Gelembung
    for g in gelembung_list:
        pygame.draw.circle(layar, (255, 255, 255), (int(g["x"]), int(g["y"])), g["r"], 1)

    # Draw Gelombang Permukaan
    for i in range(0, LEBAR, 20):
        y_wave = permukaan_air + math.sin(i * 0.1 + offset_gelombang) * 5
        pygame.draw.line(layar, (255, 255, 255), (i, y_wave), (i+10, y_wave), 2)

    # Tali Pancing
    pygame.draw.line(layar, (255, 255, 255), (mx + 60, permukaan_air - 95), (mx + 60, kedalaman_kail), 2)
    
    # Nelayan
    if GAMBAR_PEMANCING: layar.blit(GAMBAR_PEMANCING, (mx - 50, permukaan_air - 110))
    
    # Biota
    for b in biota_list:
        img = ASET[b["jenis"]]
        if img:
            render = img if b["arah"] == 1 else pygame.transform.flip(img, True, False)
            layar.blit(render, b["rect"])

    # UI Papan Skor
    pygame.draw.rect(layar, (255, 255, 255), (10, 10, 320, 160), border_radius=15)
    sx, sy = 25, 25
    for i, (jenis, jml) in enumerate(list(statistik.items())[:8]):
        if ASET[jenis]:
            layar.blit(pygame.transform.scale(ASET[jenis], (35, 25)), (sx, sy))
        txt = font_skor.render(f": {jml}", True, (0, 0, 0))
        layar.blit(txt, (sx + 45, sy - 2))
        sy += 35
        if (i+1) % 4 == 0: sx += 140; sy = 25

    # Tombol STOP
    pygame.draw.rect(layar, (200, 0, 0), btn_stop, border_radius=10)
    layar.blit(font_tombol.render("STOP", True, (255, 255, 255)), (btn_stop.x + 5, btn_stop.y + 10))

    # Layar Pause
    if game_pause:
        overlay = pygame.Surface((LEBAR, TINGGI), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        layar.blit(overlay, (0,0))
        pygame.draw.rect(layar, (0, 150, 0), btn_lanjut, border_radius=15)
        layar.blit(font_tombol.render("RESUME", True, (255, 255, 255)), (btn_lanjut.x + 15, btn_lanjut.y + 10))

    pygame.display.flip()
    clock.tick(60)

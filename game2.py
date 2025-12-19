import pygame
import random
import sys
import os

# 1. Inisialisasi & Path Absolut
pygame.init()
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# --- TAMPILAN PORTRAIT HP ---
LEBAR, TINGGI = 450, 800 
layar = pygame.display.set_mode((LEBAR, TINGGI))
pygame.display.set_caption("🎣 Mancing Mania Mobile")

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

# 2. Muat Aset
ASET = {
    "ikan": muat_aset('ikan.png', (50, 35)),
    "buaya": muat_aset('buaya.png', (100, 45)),
    "kudanil": muat_aset('kudanil.png', (90, 65)),
    "ular": muat_aset('ular.png', (120, 50)), 
    "kepiting": muat_aset('kepiting.png', (45, 35)),
    "hiu": muat_aset('hiu.png', (120, 60)),
    "pausorca": muat_aset('pausorca.png', (140, 75)),
    "zombi1": muat_aset('zombi1.png', (70, 85)),
    "zombi2": muat_aset('zombi2.png', (70, 85)),
    "virus": muat_aset('virus.png', (50, 50))
}
# Pastikan file pemancing.jpg ada di folder
GAMBAR_PEMANCING = muat_aset('pemancing.jpg', (120, 120))

# Gunakan Font None agar tidak error di server Streamlit
font_skor = pygame.font.SysFont(None, 30)
font_tombol = pygame.font.SysFont(None, 40)

statistik = {k: 0 for k in ASET.keys()}
biota_list = []
permukaan_air = 380 # Garis laut diturunkan agar nelayan terlihat

def buat_biota():
    jenis = random.choice(list(ASET.keys()))
    sisi = random.choice(["kiri", "kanan"])
    y = random.randint(permukaan_air + 60, 750)
    x = -200 if sisi == "kiri" else LEBAR + 200
    arah = 1 if sisi == "kiri" else -1
    return {"rect": pygame.Rect(x, y, 60, 45), "jenis": jenis, "arah": arah, "speed": random.randint(2, 4)}

for _ in range(12): biota_list.append(buat_biota())

kedalaman_kail = permukaan_air
sedang_mancing = False; kail_turun = False; objek_didapat = None
clock = pygame.time.Clock()

while True:
    layar.fill((173, 216, 230)) # Langit
    mx, my = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not sedang_mancing: kail_turun = True; sedang_mancing = True

    # Logika Kail
    ujung_x = mx + 60
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

    # Logika Hewan
    for b in biota_list:
        b["rect"].x += b["arah"] * b["speed"]
        if b["rect"].x > LEBAR + 300 or b["rect"].x < -300:
            b["rect"].x = -200 if b["arah"] == 1 else LEBAR + 200
        
        kail_rect = pygame.Rect(ujung_x - 15, kedalaman_kail, 30, 30)
        if not objek_didapat and sedang_mancing and kail_rect.colliderect(b["rect"]):
            objek_didapat = b; kail_turun = False

    # --- DRAWING ---
    pygame.draw.rect(layar, (0, 191, 255), (0, permukaan_air, LEBAR, 500)) # Air
    pygame.draw.line(layar, (255,255,255), (mx + 60, permukaan_air - 90), (mx + 60, kedalaman_kail), 2) # Tali
    
    # Nelayan (Nempel di Air)
    if GAMBAR_PEMANCING: 
        layar.blit(GAMBAR_PEMANCING, (mx - 50, permukaan_air - 110))
    
    # Hewan (Hanya gambar jika ada, jika tidak ada jangan gambar kotak abu-abu)
    for b in biota_list:
        img = ASET[b["jenis"]]
        if img:
            render = img if b["arah"] == 1 else pygame.transform.flip(img, True, False)
            layar.blit(render, b["rect"])
    
    if objek_didapat and ASET[objek_didapat["jenis"]]:
        layar.blit(ASET[objek_didapat["jenis"]], objek_didapat["rect"])

    # Skor
    pygame.draw.rect(layar, (255,255,255), (10, 10, 300, 150), border_radius=10)
    sx, sy = 25, 20
    for i, (jenis, jml) in enumerate(list(statistik.items())[:6]):
        txt = font_skor.render(f"{jenis}: {jml}", True, (0,0,0))
        layar.blit(txt, (sx, sy))
        sy += 22
        if (i+1) % 3 == 0: sx += 120; sy = 20

    pygame.display.flip()
    clock.tick(60)

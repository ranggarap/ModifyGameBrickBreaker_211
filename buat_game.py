import pygame
import os

pygame.init()
size = (600, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Menu Futuristik")
clock = pygame.time.Clock()

# ==========================
#  FONT CUSTOM
# ==========================
FONT_NAME = "Orbitron.ttf"   # gunakan font custom di folder yang sama
if not os.path.exists(FONT_NAME):
    FONT_NAME = pygame.font.get_default_font()

font_big = pygame.font.Font(FONT_NAME, 60)
font_small = pygame.font.Font(FONT_NAME, 32)

# ==========================
#  FUNGSI TEKS DENGAN GLOW
# ==========================
def render_glow(text, font, color, glow_color, glow_size=4):
    base = font.render(text, True, color)
    glow = []

    # buat lapisan glow di sekitar teks
    for i in range(glow_size):
        glow.append(font.render(text, True, glow_color))

    # buat surface lebih besar untuk glow
    w = base.get_width() + glow_size * 4
    h = base.get_height() + glow_size * 4
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # tempel glow dengan offset
    for g in glow:
        surf.blit(g, (glow_size*2, glow_size*2))

    # tempel teks asli
    surf.blit(base, (glow_size*2, glow_size*2))
    return surf

# ==========================
#  ANIMASI FADE-IN
# ==========================
alpha_title = 0
alpha_menu = 0
fade_speed = 3

# ==========================
#  MENU OPTIONS
# ==========================
menu_items = ["START", "OPTIONS", "EXIT"]
menu_surfaces = []

for item in menu_items:
    surf = render_glow(item, font_small,
                       color=(255, 255, 255),
                       glow_color=(100, 200, 255))
    menu_surfaces.append(surf)

running = True
while running:
    screen.fill((10, 15, 25))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ------------------------------
    # Animasi Fade-in Title
    # ------------------------------
    if alpha_title < 255:
        alpha_title += fade_speed

    title = render_glow("ROCKET BREAKER", font_big,
                        color=(255, 255, 255),
                        glow_color=(0, 150, 255))

    title.set_alpha(alpha_title)
    screen.blit(title, (size[0]//2 - title.get_width()//2, 80))

    # ------------------------------
    # Animasi Fade-in Menu
    # ------------------------------
    if alpha_title >= 200 and alpha_menu < 255:
        alpha_menu += fade_speed

    y = 240
    for surf in menu_surfaces:
        draw = surf.copy()
        draw.set_alpha(alpha_menu)
        screen.blit(draw, (size[0]//2 - draw.get_width()//2, y))
        y += 70

    pygame.display.update()
    clock.tick(60)

pygame.quit()

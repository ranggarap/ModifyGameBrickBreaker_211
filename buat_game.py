import pygame
import os

pygame.init()
size = (600, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Menu Futuristik")
clock = pygame.time.Clock()

# ---------------------- ASSETS (optional) ----------------------
def try_load_image(name, size_hint=None):
    try:
        img = pygame.image.load(name).convert_alpha()
        if size_hint:
            img = pygame.transform.smoothscale(img, size_hint)
        return img
    except Exception:
        return None

rocket_img = try_load_image("rocket.png", (600, 600))
paddle_img = try_load_image("paddle.png")

# ---------------------- COLORS ----------------------
WHITE  = (255, 255, 255)
BLACK  = (6, 6, 20)
PINK   = (255, 60, 170)
GREEN  = (28, 252, 106)
RED    = (255, 60, 60)
CYAN   = (0, 180, 255)
BRICK_COLORS = [
    (255,150,0),(255,80,80),(80,200,255),
    (150,80,255),(255,255,100),(180,255,180),(255,180,200)
]

# ---------------------- FONTS ----------------------
# Put fonts in assets/fonts/, e.g. "Orbitron-Bold.ttf", "Roboto-Bold.ttf"
def load_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except Exception:
        return pygame.font.Font(None, size)

FONT_TITLE = load_font("assets/fonts/Orbitron-Bold.ttf", 56)
FONT_BUTTON = load_font("assets/fonts/Roboto-Bold.ttf", 30)
FONT_INFO = pygame.font.Font(None, 26)

# ---------------------- HIGH SCORE PERSISTENCE ----------------------
HS_FILE = "highscore.txt"
def load_highscore():
    try:
        with open(HS_FILE, "r") as f:
            return int(f.read().strip() or 0)
    except Exception:
        return 0
def save_highscore(v):
    try:
        with open(HS_FILE, "w") as f:
            f.write(str(int(v)))
    except Exception:
        pass

highscore = load_highscore()

# ---------------------- GAME STATE ----------------------
current_level = 1
max_level = 3
score = 0
lives = 3
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
while running:
    now = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

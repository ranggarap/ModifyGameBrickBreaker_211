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
playing = False
level_cleared = False
game_over = False
in_main_menu = True
show_message_until = 0

# ---------------------- MENU ANIMATION STATE ----------------------
menu_alpha = 0
menu_fade_speed = 6   # bigger = faster fade-in
menu_hover_scale = 1.08  # scale when hovering button

# ---------------------- LEVEL PARAMETERS ----------------------
level_params = {
    1: {"ball_speed": 1.0, "paddle_speed": 12, "rows": 5},
    2: {"ball_speed": 1.35, "paddle_speed": 13, "rows": 6},
    3: {"ball_speed": 1.8, "paddle_speed": 14, "rows": 8},
}

# ---------------------- SOUNDS (optional) ----------------------
def load_sound(name):
    try:
        return pygame.mixer.Sound(name)
    except Exception:
        return None

hit_sound = load_sound("hit.wav")
brick_sound = load_sound("brick.wav")
win_sound = load_sound("win.wav")
gameover_sound = load_sound("gameover.wav")

def play(s):
    try:
        if s: s.play()
    except Exception:
        pass

# ---------------------- BRICKS ----------------------
def create_bricks(level):
    rows = level_params[level]["rows"]
    bricks_out = []
    y_start = 60
    for r in range(rows):
        color = BRICK_COLORS[r % len(BRICK_COLORS)]
        row = []
        for i in range(6):
            rect = pygame.Rect(1 + i * 100, y_start, 98, 35)
            row.append([rect, color])
        bricks_out.append(row)
        y_start += 40
    return bricks_out

# ---------------------- GAME OBJECTS ----------------------
floor = pygame.Rect(200, 550, 200, 16)
ball = pygame.Rect(294, 294, 12, 12)
ball_dir = [4, -4]

# central menu buttons (panel)
start_btn = pygame.Rect(250 - 60, 300 - 22, 120, 36)
level_btn = pygame.Rect(250 - 60, 350 - 22, 120, 36)
quit_btn  = pygame.Rect(250 - 60, 400 - 22, 120, 36)

# top bar small buttons during gameplay
top_start_btn = pygame.Rect(40, 15, 90, 30)
top_level_btn = pygame.Rect(460, 15, 90, 30)
top_quit_btn  = pygame.Rect(250, 15, 90, 30)

# ---------------------- HELPERS & RESET ----------------------
def reset_for_level(level):
    global ball, ball_dir, floor, bricks, score, lives, playing, level_cleared, game_over, highscore
    ball.x, ball.y = 294, 294
    sp = level_params[level]["ball_speed"]
    ball_dir[0] = max(1, int(4 * sp))
    ball_dir[1] = -max(1, int(4 * sp))
    floor.x = 200
    bricks[:] = create_bricks(level)
    if score > load_highscore():
        save_highscore(score)
        try:
            globals()['highscore'] = load_highscore()
        except:
            pass
    score = 0
    lives = 3
    playing = False
    level_cleared = False
    game_over = False

def reset_after_life():
    global ball, ball_dir, playing
    ball.x, ball.y = 294, 294
    sp = level_params[current_level]["ball_speed"]
    ball_dir[0] = max(1, int(4 * sp))
    ball_dir[1] = -max(1, int(4 * sp))
    floor.x = 200
    playing = False

def bricks_count():
    return sum(len(row) for row in bricks)

# ---------------------- PADDLE PERFECT VARIABLES ----------------------
paddle_color_base = (255, 80, 200)
paddle_color = list(paddle_color_base)
paddle_hit_timer = 0
last_floor_x = floor.x

# ---------------------- DRAW UTILS ----------------------
def draw_glow_text(surf, text, font, x, y, color, glow_color, glow_strength=5, glow_alpha=28):
    # Draw multiple slightly-offset glow layers
    for i in range(1, glow_strength + 1):
        offs = i
        glow_surf = font.render(text, True, glow_color)
        # reduce alpha to make glow soft
        try:
            glow_surf.set_alpha(max(6, glow_alpha - i*3))
        except Exception:
            pass
        surf.blit(glow_surf, (x - offs, y - offs))
        surf.blit(glow_surf, (x + offs, y - offs))
        surf.blit(glow_surf, (x - offs, y + offs))
        surf.blit(glow_surf, (x + offs, y + offs))
    # main text
    surf.blit(font.render(text, True, color), (x, y))

def draw_button_with_glow(target, rect, label, base_color, text_color, glow_color, mouse_pos):
    # Hover detection
    hovering = rect.collidepoint(mouse_pos)
    if hovering:
        scale = menu_hover_scale
        # scaled rect centered
        new_w = int(rect.width * scale)
        new_h = int(rect.height * scale)
        nx = rect.centerx - new_w//2
        ny = rect.centery - new_h//2
        draw_rect = pygame.Rect(nx, ny, new_w, new_h)
    else:
        draw_rect = rect
    # button body and border
    pygame.draw.rect(target, base_color, draw_rect, border_radius=10)
    pygame.draw.rect(target, (255,255,255,30), draw_rect, 2, border_radius=10)
    # label centered
    text_surf = FONT_BUTTON.render(label, True, text_color)
    tx = draw_rect.x + (draw_rect.width - text_surf.get_width())//2
    ty = draw_rect.y + (draw_rect.height - text_surf.get_height())//2
    draw_glow_text(target, label, FONT_BUTTON, tx, ty, text_color, glow_color, glow_strength=6, glow_alpha=36)
    return hovering

# ---------------------- PADDLE DRAW: PERFECT (with surf for alpha) ----------------------
def draw_perfect_paddle(ball_rect, y_override=None):
    global paddle_hit_timer, last_floor_x, paddle_color
    x, y, w, h = floor.x, floor.y if y_override is None else y_override, floor.width, floor.height
    move_speed = abs(floor.x - last_floor_x)
    stretch = min(move_speed * 0.45, 20)
    last_floor_x = floor.x
    elastic_rect = pygame.Rect(int(x - stretch/2), y, int(w + stretch), h)

    if paddle_hit_timer > 0:
        boost = min(120, paddle_hit_timer * 18)
        pc = (
            min(255, paddle_color_base[0] + boost),
            min(255, paddle_color_base[1] + boost//2),
            min(255, paddle_color_base[2] + boost)
        )
        paddle_hit_timer -= 1
    else:
        pc = paddle_color_base

    glow_surf = pygame.Surface((elastic_rect.width + 80, elastic_rect.height + 60), pygame.SRCALPHA)
    gx = 40; gy = 20
    for i, a in enumerate([100, 70, 40, 20], start=0):
        col = (pc[0], int(pc[1]*0.6), pc[2], a)
        rect = pygame.Rect(gx - i*8, gy - i*6, elastic_rect.width + i*16, elastic_rect.height + i*12)
        pygame.draw.ellipse(glow_surf, col, rect)
    screen.blit(glow_surf, (elastic_rect.x - gx, elastic_rect.y - gy), special_flags=0)

    body_surf = pygame.Surface((elastic_rect.width + 4, elastic_rect.height + 4), pygame.SRCALPHA)
    body_rect = pygame.Rect(2, 2, elastic_rect.width, elastic_rect.height)
    pygame.draw.ellipse(body_surf, (18,18,30), body_rect)
    inner = body_rect.inflate(-2, -4)
    pygame.draw.ellipse(body_surf, pc, inner)
    if ball_rect:
        rel = (ball_rect.centerx - (elastic_rect.x + elastic_rect.width/2)) / (elastic_rect.width/2)
        rel = max(-1, min(1, rel))
        hl_x = int((inner.width - inner.width*0.6)/2 + (rel * inner.width*0.18))
    else:
        hl_x = int(inner.width*0.2)
    hl = pygame.Rect(inner.x + hl_x, inner.y + 2, int(inner.width*0.6), int(inner.height*0.5))
    pygame.draw.ellipse(body_surf, (255,255,255,120), hl)
    bottom = pygame.Rect(inner.x + 6, inner.y + inner.height - 6, inner.width - 12, 6)
    pygame.draw.ellipse(body_surf, (0,0,0,100), bottom)
    led_w = 6
    left_led = pygame.Rect(0, 6, led_w, elastic_rect.height - 12)
    right_led = pygame.Rect(elastic_rect.width + 4 - led_w, 6, led_w, elastic_rect.height - 12)
    pygame.draw.rect(body_surf, (255,90,200,200), left_led, border_radius=3)
    pygame.draw.rect(body_surf, (255,90,200,200), right_led, border_radius=3)

    screen.blit(body_surf, (elastic_rect.x - 2, elastic_rect.y - 2))

    if paddle_img:
        im = pygame.transform.smoothscale(paddle_img, (elastic_rect.width, elastic_rect.height))
        screen.blit(im, (elastic_rect.x, elastic_rect.y))
    pygame.draw.ellipse(screen, (255,255,255,30), elastic_rect, 2)

# ---------------------- UI DRAW HELPERS (upgraded) ----------------------
def draw_top_buttons():
    pygame.draw.rect(screen, (0,180,255), top_start_btn, border_radius=6)
    pygame.draw.rect(screen, (255,200,0), top_level_btn, border_radius=6)
    pygame.draw.rect(screen, (255,60,60), top_quit_btn, border_radius=6)
    bf = pygame.font.Font(None, 22)
    screen.blit(bf.render("START", True, BLACK), (top_start_btn.x + 14, top_start_btn.y + 6))
    screen.blit(bf.render("LEVEL", True, BLACK), (top_level_btn.x + 20, top_level_btn.y + 6))
    screen.blit(bf.render("QUIT", True, BLACK), (top_quit_btn.x + 30, top_quit_btn.y + 6))

def draw_info():
    f = pygame.font.Font(None, 34)
    screen.blit(f.render(f"Score: {score}", True, WHITE), (220, 15))
    screen.blit(f.render(f"Lives: {lives}", True, GREEN), (10, 15))
    screen.blit(f.render(f"Level: {current_level}", True, CYAN), (480, 15))

def draw_panel_menu_fade(target, mouse_pos):
    panel_w, panel_h = 380, 260
    panel_x = (600 - panel_w)//2
    panel_y = (600 - panel_h)//2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    # background blur-ish outer rect
    pygame.draw.rect(target, (12,12,30,220), panel_rect, border_radius=16)
    pygame.draw.rect(target, (60,60,90,200), panel_rect, 2, border_radius=16)

    # title with strong glow
    title_x = panel_x + (panel_w - FONT_TITLE.size("ROCKET BREAKER")[0])//2
    draw_glow_text(
        target,
        "ROCKET BREAKER",
        FONT_TITLE,
        title_x,
        panel_y + 12,
        CYAN,
        (0, 120, 255),
        glow_strength=8,
        glow_alpha=48
    )

    # Buttons (draw with glow and hover scale)
    draw_button_with_glow(target, start_btn, "START", (0,180,255), BLACK, (160,220,255), mouse_pos)
    draw_button_with_glow(target, level_btn, f"LEVEL: {current_level}", (255,200,0), BLACK, (255,210,140), mouse_pos)
    draw_button_with_glow(target, quit_btn, "QUIT", (255,80,80), BLACK, (255,150,150), mouse_pos)

    # Highscore & controls
    hs_font = FONT_INFO
    target.blit(hs_font.render(f"High Score: {highscore}", True, WHITE), (panel_x + 20, panel_y + panel_h - 48))
    target.blit(hs_font.render("Controls: ← →  |  Left click buttons", True, WHITE), (panel_x + 20, panel_y + panel_h - 24))

# ---------------------- INITIAL RESET ----------------------
bricks = create_bricks(current_level)
reset_for_level(current_level)

# ---------------------- MAIN LOOP ----------------------

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if in_main_menu:
                # consider hover-scale: use original rects for logic
                if start_btn.collidepoint(mx, my):
                    in_main_menu = False
                    reset_for_level(current_level)
                    playing = True
                    menu_alpha = 0
                elif level_btn.collidepoint(mx, my):
                    current_level = (current_level % max_level) + 1
                    bricks = create_bricks(current_level)
                elif quit_btn.collidepoint(mx, my):
                    running = False
            else:
                # in-game top small buttons
                if top_start_btn.collidepoint(mx, my):
                    reset_for_level(current_level)
                    playing = True
                elif top_level_btn.collidepoint(mx, my):
                    current_level = (current_level % max_level) + 1
                    bricks = create_bricks(current_level)
                    reset_for_level(current_level)
                elif top_quit_btn.collidepoint(mx, my):
                    in_main_menu = True
                    if score > load_highscore():
                        save_highscore(score)
                        highscore = load_highscore()
                    playing = False
                    menu_alpha = 0

    # paddle keyboard control
    keys = pygame.key.get_pressed()
    ps = level_params[current_level]["paddle_speed"]
    floor.x += (keys[pygame.K_RIGHT] * ps) - (keys[pygame.K_LEFT] * ps)
    floor.x = max(0, min(600 - floor.width, floor.x))

    # draw background
    if rocket_img:
        screen.blit(rocket_img, (0, 0))
    else:
        screen.fill(BLACK)
        for sx in range(40, 560, 80):
            pygame.draw.circle(screen, (30,30,50), (sx, 120), 2)
            pygame.draw.circle(screen, (25,25,45), (sx+20, 200), 1)

    # main menu panel (overlay with fade)
    if in_main_menu:
        # fade-in
        menu_alpha = min(255, menu_alpha + menu_fade_speed)
        # draw preview paddle behind the panel but lower so it won't overlap text
        draw_perfect_paddle(ball, y_override=panel_y + 200 if (panel_y := (600 - 260)//2) else 520)
        # create menu surface and draw UI to it
        menu_surf = pygame.Surface((600, 600), pygame.SRCALPHA)
        draw_panel_menu_fade(menu_surf, mouse_pos)
        menu_surf.set_alpha(menu_alpha)
        screen.blit(menu_surf, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        continue

    # gameplay UI
    draw_top_buttons()
    draw_info()

    # draw bricks
    for row in bricks:
        for br, col in row:
            pygame.draw.rect(screen, col, br, border_radius=6)
            pygame.draw.rect(screen, WHITE, br, 2, border_radius=6)

    # draw ball
    pygame.draw.ellipse(screen, WHITE, ball)

    # draw perfect paddle
    draw_perfect_paddle(ball)

    # ball physics
    if playing and not game_over and not level_cleared:
        ball.x += ball_dir[0]
        ball.y += ball_dir[1]

        # left/right walls
        if ball.x <= 0 or ball.x + ball.width >= 600:
            ball_dir[0] = -ball_dir[0]
            play(hit_sound)
        # top barrier
        if ball.y <= 55:
            ball_dir[1] = -ball_dir[1]
            play(hit_sound)

        # paddle collision
        if floor.colliderect(ball):
            offset = (ball.centerx - floor.centerx) / (floor.width / 2)
            speed_x = max(1, abs(ball_dir[0]))
            ball_dir[0] = int(speed_x * 1.3 * offset) or (1 if ball_dir[0] > 0 else -1)
            ball_dir[1] = -abs(ball_dir[1])
            paddle_hit_timer = 12
            play(hit_sound)

        # bricks collisions
        hits = 0
        for row in bricks:
            for br_data in row[:]:
                rect, _ = br_data
                if rect.colliderect(ball):
                    row.remove(br_data)
                    hits += 1
                    play(brick_sound)
        if hits:
            score += hits
            ball_dir[1] = -ball_dir[1]

        # ball fell
        if ball.y >= 600:
            lives -= 1
            play(gameover_sound if lives <= 0 else hit_sound)
            if lives <= 0:
                if score > load_highscore():
                    save_highscore(score)
                    highscore = load_highscore()
                playing = False
                game_over = True
                show_message_until = now + 2000
            else:
                reset_after_life()
                show_message_until = now + 700

    # draw ball (again top of paddle)
    pygame.draw.ellipse(screen, WHITE, ball)

    # check win condition for current level
    if bricks_count() == 0 and not level_cleared:
        level_cleared = True
        playing = False
        play(win_sound)
        show_message_until = now + 1500

    # handle level cleared transition
    if level_cleared:
        f = pygame.font.Font(None, 56)
        screen.blit(f.render(f"Level {current_level} Cleared!", True, GREEN), (80, 260))
        if now > show_message_until:
            if current_level < max_level:
                current_level += 1
                bricks = create_bricks(current_level)
                reset_for_level(current_level)
                level_cleared = False
            else:
                if score > load_highscore():
                    save_highscore(score)
                    highscore = load_highscore()
                f2 = pygame.font.Font(None, 48)
                screen.blit(f2.render("YOU WIN THE GAME!", True, GREEN), (90, 330))
                pygame.display.flip()
                pygame.time.wait(1400)
                in_main_menu = True
                playing = False
                level_cleared = False

    # handle game over
    if game_over:
        f = pygame.font.Font(None, 72)
        screen.blit(f.render("GAME OVER", True, RED), (120, 240))
        f2 = pygame.font.Font(None, 36)
        screen.blit(f2.render(f"Score: {score}", True, WHITE), (250, 320))
        if now > show_message_until:
            in_main_menu = True
            game_over = False
            playing = False
            current_level = 1
            bricks = create_bricks(current_level)
            reset_for_level(1)

    # small transient message
    if now < show_message_until:
        f = pygame.font.Font(None, 28)
        screen.blit(f.render("Action applied...", True, WHITE), (200, 560))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

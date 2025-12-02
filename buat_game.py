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

import pygame
import os
import math
import random
import sys
import json
import random



pygame.init()
WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cannon Battle Deluxe")

WHITE, RED, BLUE, BLACK, ORANGE, GREEN = (255,255,255), (200,50,50), (50,50,200), (0,0,0), (255,165,0), (0,200,0)
FONT = pygame.font.SysFont(None, 36)

TANK_FOLDER = os.path.join("assets", "tanks")
SOUNDS_FOLDER = os.path.join("assets")
DATA_FILE = "player_data.json"

fire_sound = pygame.mixer.Sound(os.path.join(SOUNDS_FOLDER, "fire.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join(SOUNDS_FOLDER, "explosion.wav"))

TANK_STATS = {
    'blue': 0.8, 'best1': 1.0, 'sifi': 1.1, 'sifi2': 1.3, 'sifi3': 1.5
}
TANK_PRICES = {'best1': 20, 'sifi': 30, 'sifi2': 40, 'sifi3': 50}

PLAYER_POS = [100, HEIGHT - 120]
AI_POS = [WIDTH - 200, HEIGHT - 120]
GRAVITY = 0.5
MAX_HEALTH = 100
WIN_SCORE = 3

# Game state
turn = "player"
player_power = 20
projectiles = []
explosions = []
player_health = ai_health = MAX_HEALTH
player_score = ai_score = 0
player_points = 0
unlocked_tanks = ["blue"]
selected_player_tank = "blue"
selected_ai_tank = "red"
player_fired = ai_fired = False

def load_data():
    global player_points, unlocked_tanks
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            player_points = data.get("points", 0)
            unlocked_tanks = data.get("unlocked", ["blue"])

def save_data():
    with open(DATA_FILE, 'w') as f:
        json.dump({"points": player_points, "unlocked": unlocked_tanks}, f)

def load_tank_images():
    images = {}
    for file in os.listdir(TANK_FOLDER):
        if file.endswith(".png"):
            name = file[:-4]
            path = os.path.join(TANK_FOLDER, file)
            images[name] = pygame.transform.scale(pygame.image.load(path), (96, 96))
    return images

TANK_IMAGES = load_tank_images()

def tank_selection_menu():
    global selected_player_tank
    selecting = True
    while selecting:
        WIN.fill(WHITE)
        WIN.blit(FONT.render("Choose Your Tank:", True, BLACK), (WIDTH // 2 - 150, 30))
        WIN.blit(FONT.render(f"Points: {player_points}", True, BLACK), (WIDTH - 200, 30))
        available = unlocked_tanks
        for i, name in enumerate(available):
            x = 100 + i * 220
            WIN.blit(TANK_IMAGES[name], (x, 100))
            WIN.blit(FONT.render(name, True, BLACK), (x + 10, 210))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, name in enumerate(available):
                    x = 100 + i * 220
                    if x < mx < x + 96 and 100 < my < 196:
                        selected_player_tank = name
                        selecting = False

def draw_health_bar(x, y, health, color):
    pygame.draw.rect(WIN, BLACK, (x, y, 204, 24))
    pygame.draw.rect(WIN, color, (x+2, y+2, max(0, health * 2), 20))

def draw_window():
    WIN.fill(WHITE)
    WIN.blit(TANK_IMAGES[selected_player_tank], PLAYER_POS)
    WIN.blit(TANK_IMAGES[selected_ai_tank], AI_POS)
    for p in projectiles:
        pygame.draw.circle(WIN, BLACK, (int(p['x']), int(p['y'])), 8)
    for ex in explosions:
        pygame.draw.circle(WIN, ORANGE, (int(ex['x']), int(ex['y'])), ex['radius'])
    draw_health_bar(20, 20, player_health, BLUE)
    draw_health_bar(WIDTH - 230, 20, ai_health, RED)
    WIN.blit(FONT.render(f"{turn.upper()}'s Turn", True, BLACK), (20, 60))
    WIN.blit(FONT.render(f"Score: Player {player_score} | AI {ai_score}", True, BLACK), (WIDTH // 2 - 160, HEIGHT - 40))
    WIN.blit(FONT.render(f"Points: {player_points}", True, BLACK), (WIDTH - 200, 60))
    pygame.display.update()

def fire_cannon(from_pos, angle, power):
    fire_sound.play()
    rad = math.radians(angle)
    vx = math.cos(rad) * power
    vy = -math.sin(rad) * power
    projectiles.append({'x': from_pos[0], 'y': from_pos[1], 'vx': vx, 'vy': vy})

def update_projectiles():
    global turn, player_fired, ai_fired
    new_p = []
    for p in projectiles:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['vy'] += GRAVITY
        if p['x'] < 0 or p['x'] > WIDTH or p['y'] > HEIGHT:
            continue
        if turn == "player" and abs(p['x'] - AI_POS[0]) < 40 and abs(p['y'] - AI_POS[1]) < 40:
            damage_ai(25 * TANK_STATS[selected_player_tank], p)
            return
        elif turn == "ai" and abs(p['x'] - PLAYER_POS[0]) < 40 and abs(p['y'] - PLAYER_POS[1]) < 40:
            damage_player(25, p)
            return
        new_p.append(p)
    if not new_p and projectiles:
        turn_change()
    projectiles[:] = new_p

def update_explosions():
    for ex in explosions:
        ex['radius'] += 2
    explosions[:] = [e for e in explosions if e['radius'] < 30]

def damage_ai(dmg, p):
    global ai_health, player_score, player_points
    ai_health -= dmg
    explosion_sound.play()
    explosions.append({'x': p['x'], 'y': p['y'], 'radius': 1})
    if ai_health <= 0:
        player_score += 1
        player_points += 20
        save_data()
        check_end()

def damage_player(dmg, p):
    global player_health, ai_score
    player_health -= dmg
    explosion_sound.play()
    explosions.append({'x': p['x'], 'y': p['y'], 'radius': 1})
    if player_health <= 0:
        ai_score += 1
        check_end()

def turn_change():
    global turn, player_fired, ai_fired
    turn = "ai" if turn == "player" else "player"
    player_fired = ai_fired = False

def reset_round():
    global player_health, ai_health, projectiles, explosions
    player_health = ai_health = MAX_HEALTH
    projectiles.clear()
    explosions.clear()
    turn_change()

def check_end():
    if player_score >= WIN_SCORE or ai_score >= WIN_SCORE:
        post_game_menu()

def post_game_menu():
    global player_score, ai_score
    selecting = True
    while selecting:
        WIN.fill(WHITE)
        WIN.blit(FONT.render("Match Over", True, BLACK), (WIDTH // 2 - 60, 50))
        WIN.blit(FONT.render("R - Rematch", True, BLACK), (WIDTH // 2 - 60, 100))
        WIN.blit(FONT.render("T - Change Tank", True, BLACK), (WIDTH // 2 - 60, 140))
        WIN.blit(FONT.render("B - Buy Tank", True, BLACK), (WIDTH // 2 - 60, 180))
        WIN.blit(FONT.render("Q - Quit", True, BLACK), (WIDTH // 2 - 60, 220))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_data(); pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_match(); selecting = False
                elif event.key == pygame.K_t:
                    reset_match(); tank_selection_menu(); selecting = False
                elif event.key == pygame.K_b:
                    purchase_menu()
                elif event.key == pygame.K_q:
                    save_data(); pygame.quit(); sys.exit()

def reset_match():
    global player_score, ai_score
    player_score = ai_score = 0
    reset_round()

def purchase_menu():
    global player_points
    selecting = True
    while selecting:
        WIN.fill(WHITE)
        WIN.blit(FONT.render("Buy a Tank", True, BLACK), (WIDTH // 2 - 60, 30))
        WIN.blit(FONT.render(f"Points: {player_points}", True, BLACK), (WIDTH - 200, 30))
        for i, tank in enumerate(TANK_PRICES):
            x = 100 + i * 220
            WIN.blit(TANK_IMAGES[tank], (x, 100))
            status = "Unlocked" if tank in unlocked_tanks else f"{TANK_PRICES[tank]} pts"
            color = GREEN if tank in unlocked_tanks else RED
            WIN.blit(FONT.render(tank, True, BLACK), (x + 10, 210))
            WIN.blit(FONT.render(status, True, color), (x + 5, 250))
        WIN.blit(FONT.render("ESC to return", True, BLACK), (WIDTH // 2 - 60, HEIGHT - 40))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_data(); pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                selecting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, tank in enumerate(TANK_PRICES):
                    x = 100 + i * 220
                    if x < mx < x + 96 and 100 < my < 196:
                        if tank not in unlocked_tanks and player_points >= TANK_PRICES[tank]:
                            unlocked_tanks.append(tank)
                            player_points -= TANK_PRICES[tank]
                            save_data()

def ai_turn():
    angle = random.randint(110, 130)
    power = 20
    fire_cannon(AI_POS, angle, power)

def main():
    global player_fired, ai_fired
    clock = pygame.time.Clock()
    load_data()
    tank_selection_menu()
    while True:
        clock.tick(60)
        draw_window()
        update_projectiles()
        update_explosions()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_data(); pygame.quit(); sys.exit()
            if turn == "player" and event.type == pygame.MOUSEBUTTONDOWN and not player_fired:
                mx, my = pygame.mouse.get_pos()
                dx = mx - PLAYER_POS[0]
                dy = PLAYER_POS[1] - my
                angle = math.degrees(math.atan2(dy, dx))
                fire_cannon(PLAYER_POS, angle, player_power)
                player_fired = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: PLAYER_POS[0] = max(0, PLAYER_POS[0] - 4)
        if keys[pygame.K_RIGHT]: PLAYER_POS[0] = min(WIDTH - 100, PLAYER_POS[0] + 4)

        if turn == "ai" and not projectiles and not ai_fired:
            pygame.time.wait(800)
            ai_turn()
            ai_fired = True

if __name__ == "__main__":
    main()
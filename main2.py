import pygame
import os
import math
import random
import json
import sys

# --- Initialize pygame ---
pygame.init()
WIDTH, HEIGHT = 1000, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cannon Battle - Final")

# --- Colors and Fonts ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (30, 144, 255)
GREEN = (0, 200, 0)
ORANGE = (255, 140, 0)
FONT = pygame.font.SysFont("arial", 28)

# --- Folders ---
TANK_FOLDER = os.path.join("assets", "tanks")
SOUND_FOLDER = os.path.join("assets")
POINTS_FILE = "player_data.json"

# --- Load Sounds ---
fire_sound = pygame.mixer.Sound(os.path.join(SOUND_FOLDER, "fire.wav"))
explosion_sound = pygame.mixer.Sound(os.path.join(SOUND_FOLDER, "explosion.wav"))

# --- Game Constants ---
GRAVITY = 0.5
MAX_HEALTH = 100
WIN_SCORE = 3

# --- Tank Stats and Unlocking ---
TANK_STATS = {
    'blue': 0.8, 'best1': 1.0, 'sifi': 1.2, 'sifi2': 1.4, 'sifi3': 1.6,
}
TANK_PRICES = {'best1': 20, 'sifi': 40, 'sifi2': 60, 'sifi3': 80}
DEFAULT_UNLOCKED = ['blue']

# --- Global Variables ---
TANK_IMAGES = {}
PLAYER_POS = [80, HEIGHT - 100]
AI_POS = [WIDTH - 140, HEIGHT - 100]
projectiles, explosions = [], []
player_power = 20
turn = "player"
player_score = ai_score = 0
player_health = ai_health = MAX_HEALTH
player_fired = ai_fired = False
selected_player_tank = "blue"
selected_ai_tank = random.choice(["red", "red1"])
player_data = {"points": 0, "unlocked": DEFAULT_UNLOCKED[:]}

# --- Load Tank Images ---
def load_tank_images():
    images = {}
    for file in os.listdir(TANK_FOLDER):
        if file.endswith(".png"):
            name = file[:-4]
            path = os.path.join(TANK_FOLDER, file)
            images[name] = pygame.transform.scale(pygame.image.load(path), (100, 100))
    return images

# --- Load or Initialize Player Data ---
def load_player_data():
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, "r") as f:
            return json.load(f)
    return {"points": 0, "unlocked": DEFAULT_UNLOCKED[:]}

def save_player_data():
    with open(POINTS_FILE, "w") as f:
        json.dump(player_data, f)

# --- Tank Selection Menu ---
def tank_selection_menu():
    global selected_player_tank, selected_ai_tank, player_data
    selecting = True
    while selecting:
        WIN.fill(WHITE)
        WIN.blit(FONT.render("Select Your Tank", True, BLACK), (WIDTH//2 - 120, 40))
        WIN.blit(FONT.render(f"Points: {player_data['points']}", True, GREEN), (20, 20))

        for i, name in enumerate(TANK_STATS.keys()):
            x = 80 + i * 140
            y = 150
            if name in TANK_IMAGES:
                WIN.blit(TANK_IMAGES[name], (x, y))
                WIN.blit(FONT.render(name, True, BLACK), (x + 10, y + 110))
                if name not in player_data['unlocked']:
                    pygame.draw.rect(WIN, RED, (x, y, 100, 100), 5)
                    price = TANK_PRICES.get(name, 999)
                    WIN.blit(FONT.render(f"{price} pts", True, BLACK), (x + 5, y + 130))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player_data()
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for i, name in enumerate(TANK_STATS.keys()):
                    x = 80 + i * 140
                    if x < mx < x + 100 and 150 < my < 250:
                        if name in player_data['unlocked']:
                            selected_player_tank = name
                            selected_ai_tank = random.choice(["red", "red1"])
                            selecting = False
                        elif name in TANK_PRICES:
                            cost = TANK_PRICES[name]
                            if player_data['points'] >= cost:
                                player_data['points'] -= cost
                                player_data['unlocked'].append(name)
                                save_player_data()

# --- Drawing Functions ---
def draw_health_bar(x, y, health, color):
    pygame.draw.rect(WIN, BLACK, (x, y, 104, 14))
    pygame.draw.rect(WIN, color, (x + 2, y + 2, max(0, health), 10))

def draw_window():
    WIN.fill(WHITE)
    WIN.blit(TANK_IMAGES[selected_player_tank], PLAYER_POS)
    WIN.blit(TANK_IMAGES[selected_ai_tank], AI_POS)
    for p in projectiles:
        pygame.draw.circle(WIN, BLACK, (int(p['x']), int(p['y'])), 6)
    for ex in explosions:
        pygame.draw.circle(WIN, ORANGE, (int(ex['x']), int(ex['y'])), ex['radius'])
    draw_health_bar(20, 20, player_health, BLUE)
    draw_health_bar(WIDTH - 130, 20, ai_health, RED)
    WIN.blit(FONT.render(f"Turn: {turn.upper()}", True, BLACK), (WIDTH//2 - 80, 20))
    WIN.blit(FONT.render(f"Points: {player_data['points']}", True, GREEN), (20, 50))
    WIN.blit(FONT.render(f"Score: Player {player_score} | AI {ai_score}", True, BLACK), (WIDTH//2 - 120, HEIGHT - 40))
    pygame.display.update()

# --- Firing and Game Logic ---
def fire_cannon(from_pos, angle, power):
    fire_sound.play()
    rad = math.radians(angle)
    vx = math.cos(rad) * power
    vy = -math.sin(rad) * power
    projectiles.append({'x': from_pos[0], 'y': from_pos[1], 'vx': vx, 'vy': vy})

def update_projectiles():
    global player_score, ai_score, turn, player_fired, ai_fired
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
            damage_player(25 * TANK_STATS.get(selected_ai_tank, 1.0), p)
            return
        new_p.append(p)
    if not new_p and projectiles:
        switch_turn()
    projectiles[:] = new_p

def update_explosions():
    for ex in explosions:
        ex['radius'] += 2
    explosions[:] = [e for e in explosions if e['radius'] < 30]

def damage_ai(damage, p):
    global ai_health, player_score, projectiles
    ai_health -= damage
    explosion_sound.play()
    explosions.append({'x': p['x'], 'y': p['y'], 'radius': 1})
    projectiles.clear()
    if ai_health <= 0:
        player_score += 1
        player_data['points'] += 20
        save_player_data()
        reset_round()
    else:
        switch_turn()

def damage_player(damage, p):
    global player_health, ai_score, projectiles
    player_health -= damage
    explosion_sound.play()
    explosions.append({'x': p['x'], 'y': p['y'], 'radius': 1})
    projectiles.clear()
    if player_health <= 0:
        ai_score += 1
        reset_round()
    else:
        switch_turn()

def switch_turn():
    global turn, player_fired, ai_fired
    turn = "ai" if turn == "player" else "player"
    player_fired = False
    ai_fired = False

def reset_round():
    global player_health, ai_health, projectiles, explosions, turn, player_fired, ai_fired, player_score, ai_score

    if player_score >= WIN_SCORE:
        show_winner("Player")
        player_score = 0
        ai_score = 0
        player_data['points'] += 50
        save_player_data()

    elif ai_score >= WIN_SCORE:
        show_winner("AI")
        player_score = 0
        ai_score = 0

    player_health = ai_health = MAX_HEALTH
    projectiles.clear()
    explosions.clear()
    turn = "player"
    player_fired = False
    ai_fired = False

def show_winner(winner):
    while True:
        WIN.fill(WHITE)
        text = FONT.render(f"{winner} Wins the Match!", True, GREEN if winner == "Player" else RED)
        prompt = FONT.render("Click to play again or press [Q] to Quit", True, BLACK)
        WIN.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
        WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player_data()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                save_player_data()
                pygame.quit()
                sys.exit()

# --- AI Logic ---
def ai_fire():
    angle = random.randint(120, 160)
    fire_cannon(AI_POS, angle, 22)

# --- Main Loop ---
def main():
    global player_fired, ai_fired
    clock = pygame.time.Clock()
    tank_selection_menu()
    while True:
        clock.tick(60)
        draw_window()
        update_projectiles()
        update_explosions()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_player_data()
                pygame.quit(); sys.exit()
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

        if turn == "ai" and not ai_fired and not projectiles:
            pygame.time.wait(600)
            ai_fire()
            ai_fired = True

if __name__ == "__main__":
    TANK_IMAGES = load_tank_images()
    player_data = load_player_data()
    main()

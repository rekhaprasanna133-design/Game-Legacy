import pygame
import random
import math
import sys

# Game window size
WIDTH, HEIGHT = 800, 600

# Define damage values
ATTACK_DAMAGE = 25  # Normal attack damage
SKILL_DAMAGE = 75  # Skill damage

# Define character classes with updated HP
CLASSES = {
    "Knight": {"maxHp": 660, "speed": 1.2, "color": (37, 99, 235), "special_skill": "Divine Shield", "shield_duration": 2.0},
    "Assassin": {"maxHp": 660, "speed": 2.2, "color": (124, 58, 237), "stealth_duration": 3.0, "special_skill": "Stealth"},
    "Mage": {"maxHp": 660, "speed": 1.5, "color": (251, 146, 60), "special_skill": "Fireball", "skill_damage": 75},
    "Healer": {"maxHp": 660, "speed": 1.4, "color": (16, 185, 129), "special_skill": "Heal"},
    "Summoner": {"maxHp": 660, "speed": 1.3, "color": (146, 64, 14), "special_skill": "Summon Beast"},
    "Warrior": {"maxHp": 660, "speed": 1.6, "color": (239, 68, 68), "special_skill": "Charge", "charge_speed": 400, "charge_duration": 0.5, "charge_damage": 75},
    "Beast": {"maxHp": 660, "speed": 1.8, "color": (17, 24, 39), "attackCooldown": 1.5, "attackDamage": 25, "lifespan": 9.0},
}

# Unique skill keys for each player
PLAYER1_SKILL_KEY = pygame.K_f
PLAYER2_SKILL_KEY = pygame.K_h
UNIVERSAL_COOLDOWN = 10.0

# Image and Sound asset cache
ASSETS = {}

def load_assets():
    """Loads and caches all necessary game assets."""
    global ASSETS
    
    # --- AUDIO ASSETS ---
    try:
        pygame.mixer.music.load('bg_music.ogg')
        ASSETS['hit_sound'] = pygame.mixer.Sound('hit_sound.wav')
        ASSETS['skill_sound'] = pygame.mixer.Sound('skill_sound.wav')
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Warning: Could not load audio files. Sound effects and music will be disabled.")
        ASSETS['hit_sound'] = None
        ASSETS['skill_sound'] = None

    # --- IMAGE ASSETS ---
    try:
        bg_image_raw = pygame.image.load('arena_background.png').convert()
        ASSETS['background'] = pygame.transform.scale(bg_image_raw, (WIDTH, HEIGHT))
    except pygame.error:
        print("Warning: Could not load arena_background.png. Using a solid color background.")
        ASSETS['background'] = None

def create_entity(class_name, team, x, y, is_player=False, player_id=""):
    c = CLASSES.get(class_name, CLASSES["Knight"])
    entity = {
        "id": f"player-{player_id}" if is_player else f"{team}-{class_name}-{random.randint(1000,9999)}",
        "className": class_name,
        "team": team,
        "x": float(x),
        "y": float(y),
        "hp": c["maxHp"],
        "maxHp": c["maxHp"],
        "speed": c["speed"],
        "radius": 16,
        "color": c["color"],
        "isPlayer": is_player,
        "attackCooldown": 0,
        "skillCooldown": 0,
        "is_stealthed": False,
        "stealth_timer": 0,
        "is_charging": False,
        "charge_timer": 0,
        "charge_direction_x": 0,
        "charge_direction_y": 0,
        "is_invulnerable": False,
        "invulnerable_timer": 0,
        "original_skill_damage": CLASSES["Mage"]["skill_damage"] if class_name == "Mage" else CLASSES["Warrior"]["charge_damage"] if class_name == "Warrior" else 0
    }
    
    if class_name == "Beast":
        entity["lifespan_timer"] = c["lifespan"]
        entity["attackCooldown"] = 0
    return entity

def dist(a, b):
    dx = a["x"] - b["x"]
    dy = a["y"] - b["y"]
    return math.sqrt(dx * dx + dy * dy)

def draw_stick_figure(screen, entity):
    x, y = int(entity["x"]), int(entity["y"])
    color = entity["color"]
    head_radius = entity["radius"] // 2
    body_length = entity["radius"] * 1.5
    limb_length = entity["radius"] * 0.8

    # Head
    pygame.draw.circle(screen, color, (x, y - head_radius - (body_length / 2)), head_radius)
    
    # Body
    body_top_y = y - (body_length / 2)
    body_bottom_y = y + (body_length / 2)
    pygame.draw.line(screen, color, (x, body_top_y), (x, body_bottom_y), 3)

    # Arms
    pygame.draw.line(screen, color, (x, y), (x - limb_length, y - limb_length / 2), 3)
    pygame.draw.line(screen, color, (x, y), (x + limb_length, y - limb_length / 2), 3)

    # Legs
    pygame.draw.line(screen, color, (x, body_bottom_y), (x - limb_length / 2, body_bottom_y + limb_length), 3)
    pygame.draw.line(screen, color, (x, body_bottom_y), (x + limb_length / 2, body_bottom_y + limb_length), 3)

# -------- FIXED MAIN MENU --------
def main_menu(screen, font):
    input_box1 = pygame.Rect(300, 150, 200, 32)
    input_box2 = pygame.Rect(300, 250, 200, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color1, color2 = color_inactive, color_inactive
    active_box = None
    text1, text2 = '', ''
    selected_role1, selected_role2 = None, None
    role_names = ["Knight", "Assassin", "Mage", "Healer", "Summoner", "Warrior"]

    while True:
        screen.fill((30, 30, 30))
        title = font.render("Throne of Seals - Battle Ground", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        # Player 1 ID
        label1 = font.render("Player 1 ID:", True, (255, 255, 255))
        screen.blit(label1, (input_box1.x, input_box1.y - 30))
        txt_surface1 = font.render(text1, True, color1)
        input_box1.w = max(200, txt_surface1.get_width() + 10)
        screen.blit(txt_surface1, (input_box1.x + 5, input_box1.y + 5))
        pygame.draw.rect(screen, color1, input_box1, 2)

        # Player 2 ID
        label2 = font.render("Player 2 ID:", True, (255, 255, 255))
        screen.blit(label2, (input_box2.x, input_box2.y - 30))
        txt_surface2 = font.render(text2, True, color2)
        input_box2.w = max(200, txt_surface2.get_width() + 10)
        screen.blit(txt_surface2, (input_box2.x + 5, input_box2.y + 5))
        pygame.draw.rect(screen, color2, input_box2, 2)

        # Role selection
        role_label = font.render("Select Roles:", True, (255, 255, 255))
        screen.blit(role_label, (100, 320))

        role_rects = []
        for i, r in enumerate(role_names):
            # Player 1 roles
            role_color1 = (0, 200, 0) if selected_role1 == r else (200, 200, 200)
            role_btn1 = font.render(r, True, role_color1)
            rect1 = role_btn1.get_rect(topleft=(100, 350 + i * 30))
            screen.blit(role_btn1, rect1)

            # Player 2 roles
            role_color2 = (0, 200, 0) if selected_role2 == r else (200, 200, 200)
            role_btn2 = font.render(r, True, role_color2)
            rect2 = role_btn2.get_rect(topleft=(300, 350 + i * 30))
            screen.blit(role_btn2, rect2)

            role_rects.append((r, rect1, rect2))

        # Play button
        play_button = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 100, 100, 50)
        pygame.draw.rect(screen, (0, 200, 0), play_button)
        play_text = font.render("PLAY", True, (255, 255, 255))
        screen.blit(play_text, (play_button.x + (play_button.width - play_text.get_width()) // 2,
                                 play_button.y + (play_button.height - play_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box1.collidepoint(event.pos):
                    active_box = 1
                elif input_box2.collidepoint(event.pos):
                    active_box = 2
                else:
                    active_box = None
                color1 = color_active if active_box == 1 else color_inactive
                color2 = color_active if active_box == 2 else color_inactive

                # Select roles separately
                for r, rect1, rect2 in role_rects:
                    if rect1.collidepoint(event.pos):
                        selected_role1 = r
                    if rect2.collidepoint(event.pos):
                        selected_role2 = r

                # Start game
                if play_button.collidepoint(event.pos):
                    if text1 and text2 and selected_role1 and selected_role2:
                        return text1, selected_role1, text2, selected_role2

            if event.type == pygame.KEYDOWN:
                if active_box == 1:
                    if event.key == pygame.K_RETURN:
                        active_box = None
                    elif event.key == pygame.K_BACKSPACE:
                        text1 = text1[:-1]
                    else:
                        text1 += event.unicode
                elif active_box == 2:
                    if event.key == pygame.K_RETURN:
                        active_box = None
                    elif event.key == pygame.K_BACKSPACE:
                        text2 = text2[:-1]
                    else:
                        text2 += event.unicode

# ---------------- GAME LOOP ----------------
def game_loop(screen, font, player1_id, player1_role, player2_id, player2_role):
    clock = pygame.time.Clock()
    entities = []
    projectiles = []
    
    # Create players
    player1 = create_entity(player1_role, "A", WIDTH // 4, HEIGHT // 2, True, player1_id)
    player2 = create_entity(player2_role, "B", 3 * WIDTH // 4, HEIGHT // 2, True, player2_id)
    entities.extend([player1, player2])

    # Helper function to display on-screen text
    def draw_text(text, x, y, color=(255, 255, 255)):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

    # In-game menu for controls
    def show_controls_menu():
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        draw_text("Controls:", 50, 50)
        draw_text("WASD: Move (Player 1)", 50, 80)
        draw_text("Arrow Keys: Move (Player 2)", 50, 110)
        draw_text("E: Attack (Player 1)", 50, 140)
        draw_text("Right Shift: Attack (Player 2)", 50, 170)
        draw_text(f"{pygame.key.name(PLAYER1_SKILL_KEY).upper()}: Player 1 Skill", 50, 200)
        draw_text(f"{pygame.key.name(PLAYER2_SKILL_KEY).upper()}: Player 2 Skill", 50, 230)
        draw_text("Press 'Esc' to hide this menu", 50, 260)
        
        draw_text("Skills:", 50, 320)
        draw_text(f"Player 1 ({player1_role}): {CLASSES[player1_role]['special_skill']}", 50, 350)
        draw_text(f"Player 2 ({player2_role}): {CLASSES[player2_role]['special_skill']}", 50, 380)

        pygame.display.flip()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

    show_controls_menu()
    
    running = True
    winner = None
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_controls_menu()
                
                # Player 1 skill activation
                if event.key == PLAYER1_SKILL_KEY and player1["skillCooldown"] <= 0:
                    if ASSETS['skill_sound']: ASSETS['skill_sound'].play()
                    if player1["className"] == "Mage":
                        CLASSES["Mage"]["skill_damage"] = SKILL_DAMAGE
                        dx, dy = player2["x"] - player1["x"], player2["y"] - player1["y"]
                        dist_val = math.sqrt(dx * dx + dy * dy)
                        if dist_val > 0:
                            dx /= dist_val
                            dy /= dist_val
                        projectiles.append({
                            "x": player1["x"], "y": player1["y"], "dx": dx * 300, "dy": dy * 300, "radius": 8,
                            "team": player1["team"], "damage": CLASSES["Mage"]["skill_damage"],
                        })
                    elif player1["className"] == "Healer":
                        for ally in entities:
                            if ally["team"] == player1["team"] and ally["hp"] > 0:
                                ally["hp"] = min(ally["maxHp"], ally["hp"] + 30)
                    elif player1["className"] == "Summoner":
                        entities.append(create_entity("Beast", player1["team"], player1["x"] + 40, player1["y"], False))
                    elif player1["className"] == "Assassin":
                        player1["is_stealthed"] = True
                        player1["stealth_timer"] = CLASSES["Assassin"]["stealth_duration"]
                    elif player1["className"] == "Warrior":
                        CLASSES["Warrior"]["charge_damage"] = SKILL_DAMAGE
                        dx, dy = player2["x"] - player1["x"], player2["y"] - player1["y"]
                        dist_val = math.sqrt(dx * dx + dy * dy)
                        if dist_val > 0:
                            player1["charge_direction_x"] = dx / dist_val
                            player1["charge_direction_y"] = dy / dist_val
                        player1["is_charging"] = True
                        player1["charge_timer"] = CLASSES["Warrior"]["charge_duration"]
                    elif player1["className"] == "Knight":
                        player1["is_invulnerable"] = True
                        player1["invulnerable_timer"] = CLASSES["Knight"]["shield_duration"]
                    
                    player1["skillCooldown"] = UNIVERSAL_COOLDOWN

                # Player 2 skill activation
                if event.key == PLAYER2_SKILL_KEY and player2["skillCooldown"] <= 0:
                    if ASSETS['skill_sound']: ASSETS['skill_sound'].play()
                    if player2["className"] == "Mage":
                        CLASSES["Mage"]["skill_damage"] = SKILL_DAMAGE
                        dx, dy = player1["x"] - player2["x"], player1["y"] - player2["y"]
                        dist_val = math.sqrt(dx * dx + dy * dy)
                        if dist_val > 0:
                            dx /= dist_val
                            dy /= dist_val
                        projectiles.append({
                            "x": player2["x"], "y": player2["y"], "dx": dx * 300, "dy": dy * 300, "radius": 8,
                            "team": player2["team"], "damage": CLASSES["Mage"]["skill_damage"],
                        })
                    elif player2["className"] == "Healer":
                        for ally in entities:
                            if ally["team"] == player2["team"] and ally["hp"] > 0:
                                ally["hp"] = min(ally["maxHp"], ally["hp"] + 30)
                    elif player2["className"] == "Summoner":
                        entities.append(create_entity("Beast", player2["team"], player2["x"] - 40, player2["y"], False))
                    elif player2["className"] == "Assassin":
                        player2["is_stealthed"] = True
                        player2["stealth_timer"] = CLASSES["Assassin"]["stealth_duration"]
                    elif player2["className"] == "Warrior":
                        CLASSES["Warrior"]["charge_damage"] = SKILL_DAMAGE
                        dx, dy = player1["x"] - player2["x"], player1["y"] - player2["y"]
                        dist_val = math.sqrt(dx * dx + dy * dy)
                        if dist_val > 0:
                            player2["charge_direction_x"] = dx / dist_val
                            player2["charge_direction_y"] = dy / dist_val
                        player2["is_charging"] = True
                        player2["charge_timer"] = CLASSES["Warrior"]["charge_duration"]
                    elif player2["className"] == "Knight":
                        player2["is_invulnerable"] = True
                        player2["invulnerable_timer"] = CLASSES["Knight"]["shield_duration"]
                    
                    player2["skillCooldown"] = UNIVERSAL_COOLDOWN
    
        # Game logic and updates
        
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Player 1 Movement (WASD)
        if not player1["is_charging"]:
            move_x1, move_y1 = 0, 0
            if keys[pygame.K_w]: move_y1 -= 1
            if keys[pygame.K_s]: move_y1 += 1
            if keys[pygame.K_a]: move_x1 -= 1
            if keys[pygame.K_d]: move_x1 += 1
            
            if move_x1 != 0 or move_y1 != 0:
                length = math.sqrt(move_x1**2 + move_y1**2)
                player1["x"] += move_x1 / length * player1["speed"] * 100 * dt
                player1["y"] += move_y1 / length * player1["speed"] * 100 * dt

        # Player 2 Movement (Arrow Keys)
        if not player2["is_charging"]:
            move_x2, move_y2 = 0, 0
            if keys[pygame.K_UP]: move_y2 -= 1
            if keys[pygame.K_DOWN]: move_y2 += 1
            if keys[pygame.K_LEFT]: move_x2 -= 1
            if keys[pygame.K_RIGHT]: move_x2 += 1

            if move_x2 != 0 or move_y2 != 0:
                length = math.sqrt(move_x2**2 + move_y2**2)
                player2["x"] += move_x2 / length * player2["speed"] * 100 * dt
                player2["y"] += move_y2 / length * player2["speed"] * 100 * dt
        
        # --- Manual Melee Attacks ---
        # Player 1 (E key)
        if keys[pygame.K_e] and player1["attackCooldown"] <= 0:
            if dist(player1, player2) < player1["radius"] * 2:
                if not player2["is_invulnerable"] and not player2["is_stealthed"]:
                    player2["hp"] -= ATTACK_DAMAGE
                    if ASSETS['hit_sound']: ASSETS['hit_sound'].play()
                    player1["attackCooldown"] = 0 # <<<< CHANGED TO 0
                    
        # Player 2 (Right Shift key)
        if keys[pygame.K_RSHIFT] and player2["attackCooldown"] <= 0:
            if dist(player2, player1) < player2["radius"] * 2:
                if not player1["is_invulnerable"] and not player1["is_stealthed"]:
                    player1["hp"] -= ATTACK_DAMAGE
                    if ASSETS['hit_sound']: ASSETS['hit_sound'].play()
                    player2["attackCooldown"] = 0 # <<<< CHANGED TO 0
        
        # Update entity states
        for entity in entities:
            # Cooldowns
            if entity["attackCooldown"] > 0:
                entity["attackCooldown"] -= dt
            if entity["skillCooldown"] > 0:
                entity["skillCooldown"] -= dt
            
            # Special skill timers
            if entity["className"] == "Assassin" and entity["is_stealthed"]:
                entity["stealth_timer"] -= dt
                if entity["stealth_timer"] <= 0:
                    entity["is_stealthed"] = False
            
            if entity["className"] == "Warrior" and entity["is_charging"]:
                entity["x"] += entity["charge_direction_x"] * CLASSES["Warrior"]["charge_speed"] * dt
                entity["y"] += entity["charge_direction_y"] * CLASSES["Warrior"]["charge_speed"] * dt
                entity["charge_timer"] -= dt
                if entity["charge_timer"] <= 0:
                    entity["is_charging"] = False
                
                # Check for charge collision
                for other in entities:
                    if entity != other and entity["team"] != other["team"] and dist(entity, other) < entity["radius"] + other["radius"]:
                        if not other["is_invulnerable"] and not other["is_stealthed"]:
                            other["hp"] -= CLASSES["Warrior"]["charge_damage"]
                            if ASSETS['hit_sound']: ASSETS['hit_sound'].play()
                        entity["is_charging"] = False

            if entity["className"] == "Knight" and entity["is_invulnerable"]:
                entity["invulnerable_timer"] -= dt
                if entity["invulnerable_timer"] <= 0:
                    entity["is_invulnerable"] = False

            # Beast lifespan
            if entity["className"] == "Beast":
                entity["lifespan_timer"] -= dt
                if entity["lifespan_timer"] <= 0:
                    entities.remove(entity)
                    continue

                # Beast AI
                target = player1 if entity["team"] == "B" else player2
                if target:
                    dx, dy = target["x"] - entity["x"], target["y"] - entity["y"]
                    dist_val = math.sqrt(dx * dx + dy * dy)
                    if dist_val > 0:
                        entity["x"] += (dx / dist_val) * entity["speed"] * 100 * dt
                        entity["y"] += (dy / dist_val) * entity["speed"] * 100 * dt
                    
                    if dist_val < entity["radius"] + target["radius"] and entity["attackCooldown"] <= 0:
                        target["hp"] -= CLASSES["Beast"]["attackDamage"]
                        entity["attackCooldown"] = CLASSES["Beast"]["attackCooldown"]
                        if ASSETS['hit_sound']: ASSETS['hit_sound'].play()
            
            # Boundary checks
            entity["x"] = max(entity["radius"], min(WIDTH - entity["radius"], entity["x"]))
            entity["y"] = max(entity["radius"], min(HEIGHT - entity["radius"], entity["y"]))

        # Update and draw projectiles
        new_projectiles = []
        for p in projectiles:
            p["x"] += p["dx"] * dt
            p["y"] += p["dy"] * dt
            
            hit = False
            for entity in entities:
                if entity["team"] != p["team"] and dist(p, entity) < p["radius"] + entity["radius"]:
                    if not entity["is_invulnerable"] and not entity["is_stealthed"]:
                        entity["hp"] -= p["damage"]
                        if ASSETS['hit_sound']: ASSETS['hit_sound'].play()
                    hit = True
                    break
            
            if not hit and 0 <= p["x"] < WIDTH and 0 <= p["y"] < HEIGHT:
                new_projectiles.append(p)
        projectiles = new_projectiles
        
        # Remove dead entities
        entities = [e for e in entities if e["hp"] > 0]
        
        # Check for winner
        player1_alive = any(e for e in entities if e["isPlayer"] and e["id"] == player1["id"])
        player2_alive = any(e for e in entities if e["isPlayer"] and e["id"] == player2["id"])

        if not player1_alive:
            winner = player2_id
            running = False
        if not player2_alive:
            winner = player1_id
            running = False
            
        # Drawing
        if ASSETS['background']:
            screen.blit(ASSETS['background'], (0, 0))
        else:
            screen.fill((20, 20, 20))
            
        for entity in entities:
            # Draw health bar
            bar_width = entity["radius"] * 2
            bar_height = 5
            hp_percent = entity["hp"] / entity["maxHp"]
            hp_bar_fill = int(bar_width * hp_percent)
            
            bar_x = int(entity["x"] - entity["radius"])
            bar_y = int(entity["y"] - entity["radius"] - 10)
            
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, hp_bar_fill, bar_height))
            
            if not (entity["is_stealthed"] and entity["isPlayer"]):
                draw_stick_figure(screen, entity)
        
        for p in projectiles:
            pygame.draw.circle(screen, (255, 255, 255), (int(p["x"]), int(p["y"])), p["radius"])

        # UI: Display player info
        draw_text(f"{player1_id} ({player1_role}) HP: {int(player1.get('hp', 0))}", 10, 10, player1.get('color', (255,255,255)))
        draw_text(f"P1 Skill CD: {player1['skillCooldown']:.1f}", 10, 30)

        draw_text(f"{player2_id} ({player2_role}) HP: {int(player2.get('hp', 0))}", WIDTH - 200, 10, player2.get('color', (255,255,255)))
        draw_text(f"P2 Skill CD: {player2['skillCooldown']:.1f}", WIDTH - 200, 30)
        
        pygame.display.flip()

    # End Game Screen
    end_screen(screen, font, winner)

def end_screen(screen, font, winner):
    screen.fill((0, 0, 0))
    if winner:
        message = f"Winner: {winner}!"
    else:
        message = "Game Over!"
    
    text_surface = font.render(message, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text_surface, text_rect)
    
    restart_text = font.render("Press 'R' to Restart or 'Q' to Quit", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                    return
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Throne of Seals - Battle Ground")
    font = pygame.font.Font(None, 24)
    
    load_assets()
    
    p1_id, p1_role, p2_id, p2_role = main_menu(screen, font)
    game_loop(screen, font, p1_id, p1_role, p2_id, p2_role)

if __name__ == "__main__":
    main()
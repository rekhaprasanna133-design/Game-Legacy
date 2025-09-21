import pygame
import random
import math
import sys

# Game window size
WIDTH, HEIGHT = 800, 600
ATTACK_DAMAGE = 25  # Normal attack damage
SKILL_DAMAGE = 75  # Skill damage

# Define character classes
CLASSES = {
    "Knight": {"maxHp": 660, "speed": 1.2, "color": (37, 99, 235), "special_skill": "Divine Shield", "shield_duration": 2.0},
    "Assassin": {"maxHp": 660, "speed": 2.2, "color": (124, 58, 237), "stealth_duration": 3.0, "special_skill": "Stealth"},
    "Mage": {"maxHp": 660, "speed": 1.5, "color": (251, 146, 60), "special_skill": "Fireball", "attackDamage": 75},
    "Healer": {"maxHp": 660, "speed": 1.4, "color": (16, 185, 129), "special_skill": "Heal"},
    "Summoner": {"maxHp": 660, "speed": 1.3, "color": (146, 64, 14), "special_skill": "Summon Beast"},
    "Warrior": {"maxHp": 660, "speed": 1.6, "color": (239, 68, 68), "special_skill": "Charge", "charge_speed": 400, "charge_duration": 0.5, "charge_damage": 30},
    "Beast": {"maxHp": 660, "speed": 1.8, "color": (17, 24, 39), "attackCooldown": 1.5, "attackDamage": 20, "lifespan": 3.0},
}

# Unique skill keys for each player
PLAYER1_SKILL_KEY = pygame.K_f
PLAYER2_SKILL_KEY = pygame.K_h
UNIVERSAL_COOLDOWN = 10.0

# Sound asset cache
ASSETS = {}

def load_assets():
    """Loads and caches all necessary game assets."""
    global ASSETS
    
    try:
        pygame.mixer.music.load('bg_music.mp3')
        ASSETS['hit_sound'] = pygame.mixer.Sound('hit_sound.wav')
        ASSETS['skill_sound'] = pygame.mixer.Sound('skill_sound.wav')
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Warning: Could not load audio files. Sound effects and music will be disabled.")
        ASSETS['hit_sound'] = None
        ASSETS['skill_sound'] = None

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
    }
    if class_name == "Beast":
        entity["lifespan_timer"] = c["lifespan"]
        entity["attackCooldown"] = 0
    return entity

def dist(a, b):
    dx = a["x"] - b["x"]
    dy = a["y"] - b["y"]
    return math.sqrt(dx * dx + dy * dy)

# -------- MAIN MENU --------
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
        title = font.render("Throne of Seals - Arena", True, (255, 255, 255))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 40))

        label1 = font.render("Player 1 ID:", True, (255, 255, 255))
        screen.blit(label1, (input_box1.x, input_box1.y - 30))
        txt_surface1 = font.render(text1, True, color1)
        input_box1.w = max(200, txt_surface1.get_width() + 10)
        screen.blit(txt_surface1, (input_box1.x + 5, input_box1.y + 5))
        pygame.draw.rect(screen, color1, input_box1, 2)

        label2 = font.render("Player 2 ID:", True, (255, 255, 255))
        screen.blit(label2, (input_box2.x, input_box2.y - 30))
        txt_surface2 = font.render(text2, True, color2)
        input_box2.w = max(200, txt_surface2.get_width() + 10)
        screen.blit(txt_surface2, (input_box2.x + 5, input_box2.y + 5))
        pygame.draw.rect(screen, color2, input_box2, 2)

        role_label = font.render("Select Roles:", True, (255, 255, 255))
        screen.blit(role_label, (100, 320))

        role_rects = []
        for i, r in enumerate(role_names):
            role_color1 = (0, 200, 0) if selected_role1 == r else (200, 200, 200)
            role_btn1 = font.render(r, True, role_color1)
            rect1 = role_btn1.get_rect(topleft=(100, 350 + i * 30))
            screen.blit(role_btn1, rect1)

            role_color2 = (0, 200, 0) if selected_role2 == r else (200, 200, 200)
            role_btn2 = font.render(r, True, role_color2)
            rect2 = role_btn2.get_rect(topleft=(300, 350 + i * 30))
            screen.blit(role_btn2, rect2)

            role_rects.append((r, rect1, rect2))

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

                for r, rect1, rect2 in role_rects:
                    if rect1.collidepoint(event.pos):
                        selected_role1 = r
                    if rect2.collidepoint(event.pos):
                        selected_role2 = r

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
    
    player1 = create_entity(player1_role, "A", WIDTH // 4, HEIGHT // 2, True, player1_id)
    player2 = create_entity(player2_role, "B", 3 * WIDTH // 4, HEIGHT // 2, True, player2_id)
    entities.extend([player1, player2])

    def draw_text(text, x, y, color=(255, 255, 255)):
        text_surface = font.render(text, True, color)
        screen.blit(text_surface, (x, y))

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
                
                # Player 1 skill logic
                if event.key == PLAYER1_SKILL_KEY and player1["skillCooldown"] <= 0:
                    if ASSETS['skill_sound']: ASSETS['skill_sound'].play()
                    if player1["className"] == "Mage":
                        dx, dy = player2["x"] - player1["x"], player2["y"] - player1["y"]
                        dist_val = math.sqrt(dx * dx + dy * dy)
                        if dist_val > 0:
                            dx /= dist_val
                            dy /= dist_val
                        projectiles.append({
                            "x": player1["x"], "y": player1["y"], "dx": dx * 300, "dy": dy * 300, "radius": 8,
                            "team": player1["team"], "damage": SKILL_DAMAGE,
                        })
                    elif player1["className"] == "Healer":
                        for ally in entities:
                            if ally["team"] == player1["team"] and ally["hp"] > 0:
                                ally["hp"] = min(ally["maxHp"], ally["hp"] + SKILL_DAMAGE)
                    elif player1["className"] == "Summoner":
                        entities.append(create_entity("Beast", player1["team"], player1["x"] + 40, player1["y"], False))
                    elif player1["className"] == "Assassin":
                        player1["is_stealthed"] = True
                        player1["stealth_timer"] = CLASSES["Assassin"]["stealth_duration"]
                    elif player1["className"] == "Warrior":
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

                # Player 2 skill logic
                if event.key == PLAYER2_SKILL_KEY and player2["skillCooldown"] <= 0:
                    if ASSETS['skill_sound']: ASSETS['skill_sound'].play()
                    if player2["className"] == "Mage":
                        dx, dy = player1["x"] - player2["x"], player1["y"] - player2["y"]
                        dist_val = math.sqrt(dx * dx + dy * dy)
                        if dist_val > 0:
                            dx /= dist_val
                            dy /= dist_val
                        projectiles.append({
                            "x": player2["x"], "y": player2["y"], "dx": dx * 300, "dy": dy * 300, "radius": 8,
                            "team": player2["team"], "damage": SKILL_DAMAGE,
                        })
                    elif player2["className"] == "Healer":
                        for ally in entities:
                            if ally["team"] == player2["team"] and ally["hp"] > 0:
                                ally["hp"] = min(ally["maxHp"], ally["hp"] + SKILL_DAMAGE)
                    elif player2["className"] == "Summoner":
                        entities.append(create_entity("Beast", player2["team"], player2["x"] - 40, player2["y"], False))
                    elif player2["className"] == "Assassin":
                        player2["is_stealthed"] = True
                        player2["stealth_timer"] = CLASSES["Assassin"]["stealth_duration"]
                    elif player2["className"] == "Warrior":
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

        keys = pygame.key.get_pressed()
        
        # Player 1 movement and basic attack
        if not player1.get("is_charging", False):
            if keys[pygame.K_w]: player1["y"] -= player1["speed"] * 120 * dt
            if keys[pygame.K_s]: player1["y"] += player1["speed"] * 120 * dt
            if keys[pygame.K_a]: player1["x"] -= player1["speed"] * 120 * dt
            if keys[pygame.K_d]: player1["x"] += player1["speed"] * 120 * dt
        
        if keys[pygame.K_e] and player1["attackCooldown"] <= 0:
            target = player2
            dx, dy = target["x"] - player1["x"], target["y"] - player1["y"]
            dist_val = math.sqrt(dx * dx + dy * dy)
            if dist_val > 0:
                dx /= dist_val
                dy /= dist_val
            projectiles.append({
                "x": player1["x"], "y": player1["y"], "dx": dx * 300, "dy": dy * 300,
                "radius": 5, "team": player1["team"], "damage": ATTACK_DAMAGE,
            })
            player1["attackCooldown"] = 0.6
        
        # Player 2 movement and basic attack
        if not player2.get("is_charging", False):
            if keys[pygame.K_UP]: player2["y"] -= player2["speed"] * 120 * dt
            if keys[pygame.K_DOWN]: player2["y"] += player2["speed"] * 120 * dt
            if keys[pygame.K_LEFT]: player2["x"] -= player2["speed"] * 120 * dt
            if keys[pygame.K_RIGHT]: player2["x"] += player2["speed"] * 120 * dt
        
        if keys[pygame.K_RSHIFT] and player2["attackCooldown"] <= 0:
            target = player1
            dx, dy = target["x"] - player2["x"], target["y"] - player2["y"]
            dist_val = math.sqrt(dx * dx + dy * dy)
            if dist_val > 0:
                dx /= dist_val
                dy /= dist_val
            projectiles.append({
                "x": player2["x"], "y": player2["y"], "dx": dx * 300, "dy": dy * 300,
                "radius": 5, "team": player2["team"], "damage": ATTACK_DAMAGE,
            })
            player2["attackCooldown"] = 0.6
        
        # Update entity states
        for p in [player1, player2]:
            # Warrior charge logic
            if p.get("is_charging", False):
                p["x"] += p["charge_direction_x"] * CLASSES["Warrior"]["charge_speed"] * dt
                p["y"] += p["charge_direction_y"] * CLASSES["Warrior"]["charge_speed"] * dt
                
                # Collision check during charge
                enemy = player1 if p["team"] == "B" else player2
                if dist(p, enemy) < p["radius"] + enemy["radius"] and not enemy.get("is_invulnerable", False):
                    enemy["hp"] -= CLASSES["Warrior"]["charge_damage"]
                    if ASSETS['hit_sound']: ASSETS['hit_sound'].play()
                
                p["charge_timer"] -= dt
                if p["charge_timer"] <= 0:
                    p["is_charging"] = False

        # Update summoned entities
        for e in entities[:]:
            if e["className"] == "Beast":
                e["lifespan_timer"] -= dt
                if e["lifespan_timer"] <= 0:
                    entities.remove(e)
                    continue

                enemy = player1 if e["team"] == "B" else player2
                if enemy in entities:
                    # Chase the enemy
                    dx, dy = enemy["x"] - e["x"], enemy["y"] - e["y"]
                    dist_val = dist(e, enemy)
                    if dist_val > 0:
                        e["x"] += (dx / dist_val) * e["speed"] * 120 * dt
                        e["y"] += (dy / dist_val) * e["speed"] * 120 * dt
                    
                    # Attack when close
                    if "attackCooldown" in e and e["attackCooldown"] <= 0 and dist_val < 300:
                        ndx, ndy = dx, dy
                        if dist_val > 0:
                            ndx /= dist_val
                            ndy /= dist_val
                        projectiles.append({
                            "x": e["x"], "y": e["y"], "dx": ndx * 300, "dy": ndy * 300,
                            "radius": 5, "team": e["team"], "damage": CLASSES["Beast"]["attackDamage"],
                        })
                        e["attackCooldown"] = CLASSES["Beast"]["attackCooldown"]
        
        # Update cooldowns and timers for all entities
        for e in entities:
            if "attackCooldown" in e and e["attackCooldown"] > 0: e["attackCooldown"] -= dt
            if "skillCooldown" in e and e["skillCooldown"] > 0: e["skillCooldown"] -= dt
            if e.get("is_stealthed", False):
                e["stealth_timer"] -= dt
                if e["stealth_timer"] <= 0:
                    e["is_stealthed"] = False
            if e.get("is_invulnerable", False):
                e["invulnerable_timer"] -= dt
                if e["invulnerable_timer"] <= 0:
                    e["is_invulnerable"] = False


        # Update and check for projectile hits
        for proj in projectiles[:]:
            proj["x"] += proj["dx"] * dt
            proj["y"] += proj["dy"] * dt
            
            if not (0 <= proj["x"] <= WIDTH and 0 <= proj["y"] <= HEIGHT):
                projectiles.remove(proj)
                continue
            
            for e in entities:
                # Check for immunity before applying damage
                is_immune = e.get("is_invulnerable", False) or e.get("is_stealthed", False)
                
                if e["team"] != proj["team"] and e["hp"] > 0 and not is_immune:
                    if dist(proj, e) < e["radius"]:
                        e["hp"] -= proj["damage"]
                        if ASSETS['hit_sound']: ASSETS['hit_sound'].play()
                        if e["hp"] <= 0:
                            e["hp"] = 0
                        if proj in projectiles:
                            projectiles.remove(proj)
                        break

        # Win condition check
        if player1["hp"] <= 0:
            winner = player2["id"]
            running = False
        elif player2["hp"] <= 0:
            winner = player1["id"]
            running = False

        # Drawing
        if ASSETS['background']:
            screen.blit(ASSETS['background'], (0, 0))
        else:
            screen.fill((243, 244, 246))

        idle_offset = math.sin(pygame.time.get_ticks() / 200.0) * 3
        
        for e in entities:
            if e["hp"] <= 0:
                continue

            # Skip drawing if the Assassin is stealthed
            if e["className"] == "Assassin" and e.get("is_stealthed", False):
                continue

            draw_x = int(e["x"])
            draw_y = int(e["y"])

            if e["isPlayer"]:
                draw_y += idle_offset

            pygame.draw.circle(screen, e["color"], (draw_x, draw_y), e["radius"])
            
            hp_ratio = e["hp"] / e["maxHp"]
            hp_bar_width = 40
            hp_bar_height = 6
            hp_bar_x = e["x"] - hp_bar_width // 2
            hp_bar_y = (e["y"] - e["radius"] - 10) + idle_offset
            pygame.draw.rect(screen, (200, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, (0, 200, 0), (hp_bar_x, hp_bar_y, hp_bar_width * hp_ratio, hp_bar_height))
            
            label = font.render(e["className"], True, (0, 0, 0))
            screen.blit(label, (e["x"] - label.get_width() // 2, (e["y"] + e["radius"] + 5) + idle_offset))

        # Draw cooldowns
        p1_cooldown_text = f"P1 Skill CD: {player1['skillCooldown']:.1f}" if player1['skillCooldown'] > 0 else "P1 Skill Ready"
        p2_cooldown_text = f"P2 Skill CD: {player2['skillCooldown']:.1f}" if player2['skillCooldown'] > 0 else "P2 Skill Ready"
        draw_text(p1_cooldown_text, 10, 10, (0, 0, 0))
        draw_text(p2_cooldown_text, WIDTH - 150, 10, (0, 0, 0))

        if player1["className"] == "Knight" and player1.get("is_invulnerable", False):
            pygame.draw.circle(screen, (255, 255, 0), (int(player1["x"]), int(player1["y"])), player1["radius"] + 5, 3)
        if player2["className"] == "Knight" and player2.get("is_invulnerable", False):
            pygame.draw.circle(screen, (255, 255, 0), (int(player2["x"]), int(player2["y"])), player2["radius"] + 5, 3)

        # Draw projectiles
        for proj in projectiles:
            pygame.draw.circle(screen, (0, 0, 0), (int(proj["x"]), int(proj["y"])), proj["radius"])
        
        pygame.display.flip()

    if winner:
        game_over_screen(screen, font, winner)

    pygame.quit()
    sys.exit()

def game_over_screen(screen, font, winner_id):
    pygame.mixer.music.stop()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return

        screen.fill((30, 30, 30))
        winner_text = f"Congratulations! {winner_id} wins!"
        win_surface = font.render(winner_text, True, (0, 255, 0))
        text_rect = win_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_surface, text_rect)
        
        info_text = "Press any key to exit."
        info_surface = font.render(info_text, True, (255, 255, 255))
        info_rect = info_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        screen.blit(info_surface, info_rect)

        pygame.display.flip()

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Throne of Seals — Arena")
    font = pygame.font.SysFont("Arial", 22)
    
    load_assets()
    
    player1_id, player1_role, player2_id, player2_role = main_menu(screen, font)
    game_loop(screen, font, player1_id, player1_role, player2_id, player2_role)

if __name__ == "__main__":
    main()

import pygame
import sys
pygame.init()

# --- Screen Setup ---
WIDTH, HEIGHT = 1000, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Quad Multiplayer Grid Game")

# --- Constants ---
WHITE, BLACK, GRAY, BUTTON_COLOR = (255,255,255), (0,0,0), (200,200,200), (180,180,250)
FONT = pygame.font.SysFont(None, 30)
BIG_FONT = pygame.font.SysFont(None, 50)
TILE_SIZE, ROWS, COLS = 50, 5, 5
center_tile = pygame.Rect(WIDTH//2 - TILE_SIZE//2, HEIGHT//2 - TILE_SIZE//2, TILE_SIZE, TILE_SIZE)
winner = None

# --- Player Setup ---
player_keys = [
    {"up":pygame.K_w,"down":pygame.K_s,"left":pygame.K_a,"right":pygame.K_d,"swap":pygame.K_f},  # P1
    {"up":pygame.K_i,"down":pygame.K_k,"left":pygame.K_j,"right":pygame.K_l,"swap":pygame.K_u},  # P2
    {"up":pygame.K_1,"down":pygame.K_3,"left":pygame.K_2,"right":pygame.K_4,"swap":pygame.K_5},  # P3
    {"up":pygame.K_UP,"down":pygame.K_DOWN,"left":pygame.K_LEFT,"right":pygame.K_RIGHT,"swap":pygame.K_m}  # P4
]
grid_offsets = [(100,50),(WIDTH-350,50),(100,HEIGHT-300),(WIDTH-350,HEIGHT-300)]

player_matrices = {
    "P1": [['X','.','.','X','X'],['.','S','.','.','X'],['X','.','X','.','X'],['X','.','.','.','X'],['X','X','X','X','X']],
    "P2": [['X','X','.','S','X'],['.','.','.','.','X'],['X','.','X','.','X'],['X','.','.','.','X'],['X','X','X','X','X']],
    "P3": [['X','X','X','X','X'],['.','.','.','.','X'],['X','.','S','.','X'],['X','.','.','.','X'],['X','X','X','X','X']],
    "P4": [['X','X','X','X','X'],['.','.','.','.','X'],['X','.','.','S','X'],['X','.','.','.','X'],['X','X','X','X','X']]
}

players = {}
for i, pid in enumerate(["P1","P2","P3","P4"]):
    matrix = player_matrices[pid]
    for r in range(ROWS):
        for c in range(COLS):
            if matrix[r][c] == 'S':
                players[pid] = {
                    "pos":[r,c],
                    "keys":player_keys[i],
                    "cooldown":0,
                    "offset":grid_offsets[i],
                    "matrix":matrix
                }

# --- Drawing Functions ---
def draw_grid(pid):
    p = players[pid]
    x, y = p['offset']
    mat = p['matrix']
    btn = pygame.Rect(x, y - 40, COLS * TILE_SIZE, 30)
    pygame.draw.rect(WIN, BUTTON_COLOR, btn)
    pygame.draw.rect(WIN, BLACK, btn, 2)
    WIN.blit(FONT.render("SWAP", True, BLACK), (btn.x + btn.width // 2 - 25, btn.y + 5))
    p['swap_rect'] = btn

    for r in range(ROWS):
        for c in range(COLS):
            rect = pygame.Rect(x + c * TILE_SIZE, y + r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(WIN, WHITE, rect)
            pygame.draw.rect(WIN, BLACK, rect, 2)

            if [r, c] == p['pos']:
                WIN.blit(FONT.render(pid, True, BLACK), (rect.x + 5, rect.y + 12))
            else:
                symbol = mat[r][c]
                if symbol != '.':
                    WIN.blit(FONT.render(symbol, True, BLACK), (rect.x + 15, rect.y + 12))

def draw_controls(pid):
    p = players[pid]
    x = p['offset'][0] + COLS*TILE_SIZE + 20
    y = p['offset'][1]
    control_labels = {
        "P1": ["W = Up", "A = Left", "S = Down", "D = Right", "F = Swap"],
        "P2": ["I = Up", "J = Left", "K = Down", "L = Right", "U = Swap"],
        "P3": ["1 = Up", "2 = Left", "3 = Down", "4 = Right", "5 = Swap"],
        "P4": ["↑ = Up", "← = Left", "↓ = Down", "→ = Right", "M = Swap"]
    }
    WIN.blit(FONT.render("Controls:", True, BLACK), (x, y))
    for i, line in enumerate(control_labels[pid]):
        WIN.blit(FONT.render(line, True, BLACK), (x, y + 25 + i*25))

def draw_center_tile():
    pygame.draw.rect(WIN, GRAY, center_tile)
    pygame.draw.rect(WIN, BLACK, center_tile, 2)

def draw_winner_box():
    box = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 50, 300, 100)
    pygame.draw.rect(WIN, GRAY, box)
    pygame.draw.rect(WIN, BLACK, box, 3)
    WIN.blit(BIG_FONT.render(f"{winner} WINS!", True, BLACK), (box.x + 60, box.y + 30))

# --- Game Logic ---
def move_player(pid, dr, dc):
    global winner
    p = players[pid]
    r, c = p['pos']
    nr, nc = r + dr, c + dc
    if 0 <= nr < ROWS and 0 <= nc < COLS and p['matrix'][nr][nc] != 'X':
        p['pos'] = [nr, nc]
        ax = p['offset'][0] + nc*TILE_SIZE
        ay = p['offset'][1] + nr*TILE_SIZE
        if center_tile.collidepoint(ax + TILE_SIZE//2, ay + TILE_SIZE//2):
            winner = pid

def swap_player(pid):
    global winner
    p = players[pid]
    r, c = p['pos']
    for sr in range(ROWS):
        for sc in range(COLS):
            if p['matrix'][sr][sc] == 'S' and [sr, sc] != [r, c]:
                p['pos'] = [sr, sc]
                ax = p['offset'][0] + sc*TILE_SIZE
                ay = p['offset'][1] + sr*TILE_SIZE
                if center_tile.collidepoint(ax + TILE_SIZE//2, ay + TILE_SIZE//2):
                    winner = pid
                return

# --- Main Loop ---
def main():
    global winner
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(30)
        WIN.fill(WHITE)
        keys = pygame.key.get_pressed()
        for pid, p in players.items():
            if p['cooldown'] > 0:
                p['cooldown'] -= 1
                continue
            k = p['keys']
            if keys[k['up']]: move_player(pid, -1, 0); p['cooldown'] = 5
            elif keys[k['down']]: move_player(pid, 1, 0); p['cooldown'] = 5
            elif keys[k['left']]: move_player(pid, 0, -1); p['cooldown'] = 5
            elif keys[k['right']]: move_player(pid, 0, 1); p['cooldown'] = 5
            elif keys[k['swap']]: swap_player(pid); p['cooldown'] = 5
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for pid, p in players.items():
                    if 'swap_rect' in p and p['swap_rect'].collidepoint(mx, my):
                        swap_player(pid)
        for pid in players:
            draw_grid(pid)
            draw_controls(pid)
        draw_center_tile()
        if winner:
            draw_winner_box()
        pygame.display.update()
    pygame.quit()
    sys.exit()

try:
    main()
except Exception as e:
    print("Error:", e)
    pygame.quit()
    sys.exit()
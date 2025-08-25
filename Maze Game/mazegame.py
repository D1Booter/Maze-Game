import pygame, sys, random, time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === GOOGLE SHEETS SETUP ===
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = mazegameservice@speedrun-leaderboard.iam.gserviceaccount.com("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Speedrun Leaderboard").sheet1  # Make sure spreadsheet name matches
    return sheet

def save_score(name, time_taken):
    sheet = connect_sheet()
    sheet.append_row([name, time_taken])

def load_scores():
    sheet = connect_sheet()
    records = sheet.get_all_records()
    sorted_scores = sorted(records, key=lambda x: int(x["Time"]))[:5]
    return [(r["Name"], r["Time"]) for r in sorted_scores]

# === GAME SETUP ===
pygame.init()
WIDTH, HEIGHT = 600, 600
ROWS, COLS = 15, 15
CELL_SIZE = WIDTH // COLS
WHITE, BLACK, GREEN, RED, BLUE, YELLOW = (255,255,255), (0,0,0), (0,255,0), (255,0,0), (0,0,255), (255,255,0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Maze Speedrun / Endless")
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

# === MAZE GENERATION ===
def make_maze(rows, cols):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    stack = []
    start = (0, 0)
    maze[0][0] = 0
    stack.append(start)

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(2,0), (-2,0), (0,2), (0,-2)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] == 1:
                neighbors.append((nx, ny))
        if neighbors:
            nx, ny = random.choice(neighbors)
            maze[(x+nx)//2][(y+ny)//2] = 0
            maze[nx][ny] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    return maze

# === MAIN GAME LOOP ===
def play_game(mode, player_name):
    maze = make_maze(ROWS, COLS)
    player_cell = [0,0]
    exit_cell = [ROWS-1,COLS-1]

    # Ensure exit not inside wall
    if maze[exit_cell[0]][exit_cell[1]] == 1:
        found = False
        for i in range(ROWS-1, -1, -1):
            for j in range(COLS-1, -1, -1):
                if maze[i][j] == 0:
                    exit_cell = [i,j]
                    found = True
                    break
            if found:
                break

    start_time = time.time()
    level = 1
    running = True

    while running:
        screen.fill(WHITE)

        # Draw maze
        for r in range(ROWS):
            for c in range(COLS):
                color = WHITE if maze[r][c] == 0 else BLACK
                pygame.draw.rect(screen, color, (c*CELL_SIZE, r*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw player and exit
        pygame.draw.rect(screen, BLUE, (player_cell[1]*CELL_SIZE, player_cell[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GREEN, (exit_cell[1]*CELL_SIZE, exit_cell[0]*CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Timer
        elapsed = int(time.time() - start_time)
        timer_text = font.render(f"Time: {elapsed}", True, RED)
        screen.blit(timer_text, (10,10))

        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player_cell[0]>0 and maze[player_cell[0]-1][player_cell[1]]==0:
                    player_cell[0] -= 1
                elif event.key == pygame.K_DOWN and player_cell[0]<ROWS-1 and maze[player_cell[0]+1][player_cell[1]]==0:
                    player_cell[0] += 1
                elif event.key == pygame.K_LEFT and player_cell[1]>0 and maze[player_cell[0]][player_cell[1]-1]==0:
                    player_cell[1] -= 1
                elif event.key == pygame.K_RIGHT and player_cell[1]<COLS-1 and maze[player_cell[0]][player_cell[1]+1]==0:
                    player_cell[1] += 1

        # Win check
        if player_cell == exit_cell:
            if mode == "speedrun":
                if level == 100:
                    total_time = int(time.time() - start_time)
                    save_score(player_name, total_time)
                    return
                else:
                    level += 1
                    maze = make_maze(ROWS, COLS)
                    player_cell = [0,0]
                    exit_cell = [ROWS-1,COLS-1]
            else:  # endless
                maze = make_maze(ROWS, COLS)
                player_cell = [0,0]
                exit_cell = [ROWS-1,COLS-1]

        clock.tick(30)

# === HOME SCREEN ===
def home_screen():
    input_box = pygame.Rect(WIDTH//2-100, HEIGHT//2-100, 200, 40)
    player_name = ""
    active = False

    while True:
        screen.fill(WHITE)

        title = font.render("Maze Game", True, BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        # Input box
        txt_surface = font.render(player_name, True, BLACK)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, RED if active else BLACK, input_box, 2)

        # Buttons
        speedrun_btn = font.render("Speedrun to 100", True, GREEN)
        endless_btn = font.render("Endless Mode", True, GREEN)
        leaderboard_btn = font.render("Leaderboard", True, YELLOW)

        screen.blit(speedrun_btn, (WIDTH//2 - speedrun_btn.get_width()//2, HEIGHT//2))
        screen.blit(endless_btn, (WIDTH//2 - endless_btn.get_width()//2, HEIGHT//2+60))
        screen.blit(leaderboard_btn, (WIDTH//2 - leaderboard_btn.get_width()//2, HEIGHT//2+120))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                else:
                    active = False

                if speedrun_btn.get_rect(topleft=(WIDTH//2 - speedrun_btn.get_width()//2, HEIGHT//2)).collidepoint(event.pos):
                    if player_name.strip():
                        play_game("speedrun", player_name.strip())
                if endless_btn.get_rect(topleft=(WIDTH//2 - endless_btn.get_width()//2, HEIGHT//2+60)).collidepoint(event.pos):
                    if player_name.strip():
                        play_game("endless", player_name.strip())
                if leaderboard_btn.get_rect(topleft=(WIDTH//2 - leaderboard_btn.get_width()//2, HEIGHT//2+120)).collidepoint(event.pos):
                    scores = load_scores()
                    show_leaderboard(scores)

            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        active = False
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

def show_leaderboard(scores):
    while True:
        screen.fill(WHITE)
        title = font.render("Leaderboard (Top 5)", True, BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

        for i, (name, score) in enumerate(scores):
            txt = font.render(f"{i+1}. {name} - {score}s", True, BLACK)
            screen.blit(txt, (WIDTH//2 - txt.get_width()//2, 150 + i*40))

        back_txt = font.render("Press ESC to go back", True, RED)
        screen.blit(back_txt, (WIDTH//2 - back_txt.get_width()//2, HEIGHT-60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

# === START GAME ===
home_screen()

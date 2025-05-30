import pygame
import random
from collections import deque
pygame.init()

# fungsi grid
GRID_SIZE = 40
CELL_SIZE = 15
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 50, 255)
GREEN = (0, 200, 0)
RED = (255, 50, 50)
GRAY = (230, 230, 230)
ORANGE = (255, 165, 0)
PINK = (255, 200, 200)
YELLOW = (255, 255, 0)

class Semut:
    def __init__(self, pos):
        self.pos = pos
        self.path = []
        self.target = None
        self.step_index = 0
        self.state = "to_food"

# Setup layar
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulasi Semut")

# Matriks grid: 0 = jalan, 1 = rintangan
grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Posisi
sarang_pos = (20, 20)
makanan_pos = (GRID_SIZE - 2, GRID_SIZE - 2)
semut_pos = sarang_pos
targeted_foods = []

# variable multi makanan
food_list = []

# Buat beberapa rintangan acak
for _ in range(200):
    x = random.randint(0, GRID_SIZE - 1)
    y = random.randint(0, GRID_SIZE - 1)
    if (x, y) != sarang_pos and (x, y) not in food_list:
        grid[y][x] = 1

# Fungsi mencari jalur (BFS: Breadth First Search)
def bfs(start, goal):
    queue = deque()
    queue.append((start, [start]))
    visited = set()
    visited.add(start)

    while queue:
        current, path = queue.popleft()
        if current == goal:
            return path
        
        x, y = current
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    return None

# Fungsi cari makanan terdekat
def find_nearest_food(start_pos):
    available_foods = [f for f in food_list if f not in targeted_foods]
    if not food_list:
        return None, []
    min_path = None
    nearest = None
    for food in available_foods:
        path = bfs(start_pos, food)
        if path and (min_path is None or len(path) < len(min_path)):
            min_path = path
            nearest = food
    return nearest, min_path

#inisialisasi BFS
path = bfs(sarang_pos, makanan_pos)
step_index = 0

# Fungsi menggambar grid
def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pos = (x, y)
            if pos == sarang_pos:
                color = BLUE
            elif any(semut.pos == pos for semut in semut_list):
                semut = next(s for s in semut_list if s.pos == pos)
                color = GREEN if semut.state == "to_nest" else ORANGE
            elif grid[y][x] == 1:
                color = BLACK
            elif pos in food_list:
                color = GREEN
            elif pos in trail:
                color = PINK
            else:
                color = WHITE
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)

semut_list = [Semut(sarang_pos) for _ in range(3)]  # variable JUMLAH SEMUT
started = False
trail = []  # variable jejak semut

def draw_instructions():
    font = pygame.font.SysFont(None, 24)
    instructions = []
    for i, line in enumerate(instructions):
        text = font.render(line, True, (0, 0, 0))
        screen.blit(text, (10, 10 + i * 20))

# Fungsi visual pergerakan
running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not started:
                    started = True
                    for semut in semut_list:
                        semut.target, semut.path = find_nearest_food(semut.pos)
                        semut.step_index = 0
                        semut.state = "to_food"
                    print("Spasi ditekan! Semut mulai berjalan.")

            elif event.key == pygame.K_r:        # Reset makanan dan jejak, tetap pertahankan rintangan
                food_list.clear()
                trail.clear()
                targeted_foods.clear()
                for semut in semut_list:
                    semut.pos = sarang_pos
                    semut.path = []
                    semut.target = None
                    semut.step_index = 0
                    semut.state = "to_food"
                started = False
                print("Reset makanan dan jejak!")

            elif event.key == pygame.K_t:       # Reset total: makanan, jejak, rintangan, dan status semut
                food_list.clear()
                trail.clear()
                targeted_foods.clear()

                for y in range(GRID_SIZE):      # Hapus semua rintangan
                    for x in range(GRID_SIZE):
                        if grid[y][x] == 1:
                            grid[y][x] = 0
                for _ in range(80):             # Buat ulang rintangan baru
                    x = random.randint(0, GRID_SIZE - 1)
                    y = random.randint(0, GRID_SIZE - 1)
                    pos = (x, y)
                    if pos != sarang_pos:
                        grid[y][x] = 1

                for semut in semut_list:        # Reset semut
                    semut.pos = sarang_pos
                    semut.path = []
                    semut.target = None
                    semut.step_index = 0
                    semut.state = "to_food"
                started = False
                print("Reset total: makanan, rintangan, jejak, semut!")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            grid_x = mx // CELL_SIZE
            grid_y = my // CELL_SIZE
            pos = (grid_x, grid_y)
            if len(food_list) < 10 and pos != sarang_pos and pos not in food_list:
                food_list.append(pos)

    # Fungsi pergerakan semut
    if started:
        for semut in semut_list:
            if not semut.path:  # Jika belum punya path, cari path
                if semut.state == "to_food":
                    semut.target, semut.path = find_nearest_food(semut.pos)
                    if semut.target:
                        targeted_foods.append(semut.target)
                    semut.step_index = 0
                elif semut.state == "to_nest":
                    semut.path = bfs(semut.pos, sarang_pos)
                    semut.target = sarang_pos
                    semut.step_index = 0

            # Gerakkan semut
            if semut.path and semut.step_index < len(semut.path):
                semut.pos = semut.path[semut.step_index]
                semut.step_index += 1
                trail.append(semut.pos)

            elif semut.path and semut.step_index >= len(semut.path):
                if semut.state == "to_food":
                    if semut.target in food_list:
                        food_list.remove(semut.target)
                    if semut.target in targeted_foods:
                        targeted_foods.remove(semut.target)
                    semut.state = "to_nest"
                    semut.path = []
                    semut.step_index = 0

                elif semut.state == "to_nest":
                    semut.state = "to_food"
                    semut.path = []
                    semut.target = None
                    semut.step_index = 0


    clock.tick(10)  # FPS
    screen.fill(WHITE)
    draw_grid()
    if not started:
        draw_instructions()
    pygame.display.flip()

pygame.quit()

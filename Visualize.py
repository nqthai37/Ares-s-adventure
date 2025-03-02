import pygame
import sys
from collections import deque
import numpy as np

# Constants
WALL = "#"
FREE_SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_PLACED_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

# Direction mapping
direction = {
    (0, 1): 'r',
    (0, -1): 'l',
    (1, 0): 'd',
    (-1, 0): 'u'
}

# Initialize Pygame
pygame.init()

# Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Visualize Tool")

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (165, 42, 42)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GRAY = (200, 200, 200)

# Button and Dropdown Variables
level_button = pygame.Rect(10, 10, 100, 40)
start_button = pygame.Rect(120, 10, 100, 40)
pause_button = pygame.Rect(230, 10, 100, 40)
reset_button = pygame.Rect(340, 10, 100, 40)
level_button_dropdown_open = False
level_button_options = ["1", "2", "3"]
selected_level = None
dropdown = pygame.Rect(450, 10, 150, 40)
dropdown_open = False
dropdown_options = ["BFS", "DFS", "A*"]
selected_algorithm = None

# Maze Variables
lines = []
stones_weight = []
STONES_DRAWED = []
SWITCHES_DRAWED = []
ARES_DRAWED = []

# Ares Path
ares_path = []
current_step = 0
paused = False

# Maze Drawing Offset
maze_offset_x = 0
maze_offset_y = 0

# Global variables for BFS/DFS
stones = []
switches = []
# ares_pos = None
weights = []
matrix = None
height = 0
width = 0
ares = None

class Stone:
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight


def takeInputFile(filename):
    global weights, matrix, height, width
    try:
        with open(filename, "r") as f:
            lines = [line.rstrip("\n") for line in f]  
            if not lines:
                print("File {filename} is empty!")
                return None, 0, 0
            
            weights = list(map(int, lines[0].split()))
            height = len(lines)-1
            width = max(len(line) for line in lines)
            matrix = np.full((height, width), FREE_SPACE, dtype=str)
            for i in range(height):
                for j in range(len(lines[i+1])):
                    matrix[i, j] = lines[i+1][j]
    except FileNotFoundError:
        print("File {filename} not found!")
    
def drawMainScreen(screen):
    screen.fill(WHITE)
    pygame.display.flip()

def calculateMazeOffset():

    """Calculate the offset to center the maze on the screen."""
    global maze_offset_x, maze_offset_y, height, width, screen_width, screen_height
    maze_offset_x = (screen_width - width * 50) // 2
    maze_offset_y = (screen_height - height * 50) // 2

def find_obj_pos(matrix, height, width): # position: [x,y]
    global stones, switches, ares
    cnt =0
    for i in range(height):
        for j in range(width):
            if matrix[i, j] == STONE:
                stones.append((i, j))
                # cnt+=1
            elif matrix[i, j] == SWITCH:
                switches.append((i, j))
            elif matrix[i, j] == STONE_PLACED_ON_SWITCH:
                stones.append((i, j))
                switches.append((i, j))
            elif matrix[i, j] == ARES:
                ares = (i, j)
            elif matrix[i, j] == ARES_ON_SWITCH:
                ares = (i, j)
                switches.append((i, j))
    print(stones)
    print(switches)
    print(ares)


def drawMaze(screen):
   global maze_offset_x, maze_offset_y, lines, stones_weight, STONES_DRAWED, SWITCHES_DRAWED, ARES_DRAWED,matrix, height, width
   calculateMazeOffset()
   find_obj_pos(matrix, height, width)
   for i in range(height):
       for j in range(width):
            if matrix[i, j] == WALL:
               pygame.draw.rect(screen, BROWN, pygame.Rect(maze_offset_x + j * 50, maze_offset_y + i * 50, 50, 50))
            elif matrix[i, j] == STONE:
                pygame.draw.rect(screen, RED, pygame.Rect(maze_offset_x + j * 50, maze_offset_y + i * 50, 50, 50))
                STONES_DRAWED.append((i, j))
            elif matrix[i, j] == SWITCH:
                pygame.draw.rect(screen, YELLOW, pygame.Rect(maze_offset_x + j * 50, maze_offset_y + i * 50, 50, 50))
                SWITCHES_DRAWED.append((i, j))
            elif matrix[i, j] == STONE_PLACED_ON_SWITCH:
                pygame.draw.rect(screen, CYAN, pygame.Rect(maze_offset_x + j * 50, maze_offset_y + i * 50, 50, 50))
                STONES_DRAWED.append((i, j))
                SWITCHES_DRAWED.append((i, j))
            elif matrix[i, j] == ARES:
                pygame.draw.rect(screen, GREEN, pygame.Rect(maze_offset_x + j * 50, maze_offset_y + i * 50, 50, 50))
                ARES_DRAWED.append((i, j))
            elif matrix[i, j] == ARES_ON_SWITCH:
                pygame.draw.rect(screen, ORANGE, pygame.Rect(maze_offset_x + j * 50, maze_offset_y + i * 50, 50, 50))
                ARES_DRAWED.append((i, j))
                SWITCHES_DRAWED.append((i, j))
    # find_obj_pos(matrix, height, width)


def drawButtons(screen):
    pygame.draw.rect(screen, GRAY, level_button)
    pygame.draw.rect(screen, GRAY, start_button)
    pygame.draw.rect(screen, GRAY, pause_button)
    pygame.draw.rect(screen, GRAY, reset_button)
    pygame.draw.rect(screen, GRAY, dropdown)

    screen.blit(font.render("Level", True, BLACK), (level_button.x + 10, level_button.y + 10))
    screen.blit(font.render("Start", True, BLACK), (start_button.x + 10, start_button.y + 10))
    screen.blit(font.render("Pause", True, BLACK), (pause_button.x + 10, pause_button.y + 10))
    screen.blit(font.render("Reset", True, BLACK), (reset_button.x + 10, reset_button.y + 10))
    screen.blit(font.render("Algorithm", True, BLACK), (dropdown.x + 10, dropdown.y + 10))

    if level_button_dropdown_open:
        for i, option in enumerate(level_button_options):
            option_rect = pygame.Rect(level_button.x, level_button.y + (i + 1) * 40, level_button.width, 40)
            pygame.draw.rect(screen, GRAY, option_rect)
            screen.blit(font.render(option, True, BLACK), (option_rect.x + 10, option_rect.y + 10))

    if dropdown_open:
        for i, option in enumerate(dropdown_options):
            option_rect = pygame.Rect(dropdown.x, dropdown.y + (i + 1) * 40, dropdown.width, 40)
            pygame.draw.rect(screen, GRAY, option_rect)
            screen.blit(font.render(option, True, BLACK), (option_rect.x + 10, option_rect.y + 10))

def handleEvents():
    global running, dropdown_open, selected_algorithm, paused, current_step, lines, ares_path, level_button_dropdown_open, selected_level
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if level_button.collidepoint(event.pos):
                level_button_dropdown_open = not level_button_dropdown_open
            elif level_button_dropdown_open:
                for i, option in enumerate(level_button_options):
                    option_rect = pygame.Rect(level_button.x, level_button.y + (i + 1) * 40, level_button.width, 40)
                    if option_rect.collidepoint(event.pos):
                        selected_level = option
                        level_button_dropdown_open = False
                        takeInputFile("Level/" + selected_level + ".txt")
                        drawMainScreen(screen)
                        drawMaze(screen)
            elif start_button.collidepoint(event.pos):
                paused = False
            elif pause_button.collidepoint(event.pos):
                paused = True
            elif reset_button.collidepoint(event.pos):
                current_step = 0
                paused = True
            elif dropdown.collidepoint(event.pos):
                dropdown_open = not dropdown_open
            elif dropdown_open:
                for i, option in enumerate(dropdown_options):
                    option_rect = pygame.Rect(dropdown.x, dropdown.y + (i + 1) * 40, dropdown.width, 40)
                    if option_rect.collidepoint(event.pos):
                        selected_algorithm = option
                        dropdown_open = False
                        HandleAlgorithm()

def HandleAlgorithm():
    global ares_path,matrix
    if selected_algorithm == "BFS":
        ares_path = BFS(matrix, height, width, ares)
    elif selected_algorithm == "DFS":
        ares_path = DFS(matrix, ARES_DRAWED[0], SWITCHES_DRAWED)
    # elif selected_algorithm == "A*":
    #     ares_path = AStar(lines, ARES_DRAWED[0], SWITCHES_DRAWED)

def updateAresPath():
    global current_step, paused
    if not paused and ares_path and current_step < len(ares_path):
        current_step += 1
        pygame.time.delay(200)  # Delay for visualization

def drawAresPath():
    global ares_path, current_step
    if ares_path and current_step > 0:
        ares_path=ares_path.lower()
        moves = {'l': (0, -1), 'r': (0, 1), 'd': (1, 0), 'u': (-1, 0)}
        for i in range(current_step):
            x, y = moves[ares_path[i]]
            pygame.draw.rect(screen, ORANGE, pygame.Rect(maze_offset_x + y * 50, maze_offset_y + x * 50, 50, 50))

# BFS Algorithm
def BFS(matrix, height, width, player_pos):
    # global switches
    print('Breadth-First Search')
    initial_state = matrix.copy()
    seen = set()
    cost =0
    q = deque([(initial_state, player_pos, 0, '',cost)])
    moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]

    while q:
        state, pos, depth, path,cost = q.popleft()
        state_hash = hash(state.tobytes())
        if state_hash in seen:
            continue
        seen.add(state_hash)
        # check if the game is solved
        if is_solved(state):
            print(state)
            print(f'[BFS] Solution found!\n\n{path}\n Cost: {cost}\n')
            return path
        
        for move in moves:
            temp_state = state.copy()
            new_state, new_pos, stoneMoved = can_move(temp_state, height, width, pos, move)
            if new_state is None:
                continue
            q.append((new_state, new_pos, depth + 1, path + (direction[move].upper() if stoneMoved else direction[move]),cost +1))

    print(f'[BFS] Solution not found!\n')
    return None
# DFS Algorithm
# def DFS(matrix, player_pos, switches):
    
#     stack = [(matrix.copy(), player_pos, [player_pos])]  # Store the path as a list of (x, y) positions
#     seen = set()
#     moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]
#     while stack:
#         state, pos, path = stack.pop()
#         state_hash = hash(state.tobytes())
#         if state_hash in seen:
#             continue
#         seen.add(state_hash)
#         if is_solved(state):
#             return path  # Return the path as a list of (x, y) positions
#         for move in moves:
#             temp_state = state.copy()
#             new_state, new_pos, stoneMoved = can_move(temp_state,maze_height,maze_width, pos, move)
#             if new_state is None:
#                 continue
#             q.append((new_state, new_pos, path + (direction[move].upper() if stoneMoved else direction[move]),cost +1))
#         return None

def is_solved(matrix):
    global switches
    print(switches)
    for switch_x, switch_y in switches:
        print(switch_x, switch_y)
        print(matrix[switch_x, switch_y])
        if matrix[switch_x, switch_y] != STONE_PLACED_ON_SWITCH:
            return False
    return True
    # print(matrix)
    return all(matrix[x, y] == STONE_PLACED_ON_SWITCH for x, y in switches)

def can_move(matrix, height, width, pos, move):
    new_pos = (pos[0] + move[0], pos[1] + move[1])
    if new_pos[0] < 0 or new_pos[0] >= height or new_pos[1] < 0 or new_pos[1] >= width:
        return None, pos, False
    if matrix[new_pos] == WALL:
        return None, pos, False
    if matrix[new_pos] == STONE:
        new_stone_pos = (new_pos[0] + move[0], new_pos[1] + move[1])
        if new_stone_pos[0] < 0 or new_stone_pos[0] >= height or new_stone_pos[1] < 0 or new_stone_pos[1] >= width:
            return None, pos, False
        if matrix[new_stone_pos] == WALL or matrix[new_stone_pos] == STONE:
            return None, pos, False
        if matrix[new_stone_pos] == SWITCH:
            matrix[new_stone_pos] = STONE_PLACED_ON_SWITCH
        else:
            matrix[new_stone_pos] = STONE
    matrix[new_pos] = ARES
    matrix[pos] = FREE_SPACE
    return matrix, new_pos, True

# Main game loop
running = True
while running:
    screen.fill(WHITE)
    handleEvents()
    drawButtons(screen)
    drawMaze(screen)
    drawAresPath()
    updateAresPath()
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
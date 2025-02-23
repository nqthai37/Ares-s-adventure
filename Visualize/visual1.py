import pygame
import numpy as np
import time
from collections import deque

# Constants
WALL = "#"
FREE_SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_PLACED_ON_SWITCH = "*"

# Kích thước ô vuông
TILE_SIZE = 50

# Màu sắc
COLORS = {
    "#": (100, 100, 100),  # Wall - xám
    " ": (200, 200, 200),  # Free space - trắng
    "$": (139, 69, 19),    # Stone - nâu
    "@": (0, 0, 255),      # Ares - xanh dương
    ".": (255, 255, 0),    # Switch - vàng
    "*": (255, 165, 0)     # Stone on switch - cam
}

def read_map (filename):
    try:
        with open(filename, "r") as f:
            lines = [line.rstrip("\n") for line in f]  
            if not lines:
                print("File {filename} is empty!")
                return None, 0, 0
            height = len(lines)
            width = max(len(line) for line in lines)  
            
            matrix = np.full((height, width), FREE_SPACE, dtype=str) 
            for i in range(height):
                for j in range(len(lines[i])):
                    matrix[i, j] = lines[i][j]
            
            return matrix, height, width
    except FileNotFoundError:
        print("File {filename} not found!")
        return None, 0, 0

def find_obj_pos(matrix, height, width):
    ares, stones, stones_on_switches, switches = None, [], [], []
    for i in range(height):
        for j in range(width):
            if matrix[i, j] == STONE:
                stones.append((i, j))
            elif matrix[i, j] == SWITCH:
                switches.append((i, j))
            elif matrix[i, j] == STONE_PLACED_ON_SWITCH:
                stones_on_switches.append((i, j))
            elif matrix[i, j] == ARES:
                ares = (i, j)
    return stones, switches, stones_on_switches, ares

def can_move(matrix, height, width, pos, move):
    stoneMoved = False
    new_pos = (pos[0] + move[0], pos[1] + move[1])
    if new_pos[0] < 0 or new_pos[0] >= height or new_pos[1] < 0 or new_pos[1] >= width:
        return matrix, pos, stoneMoved
    if matrix[new_pos] == WALL:
        return matrix, pos, stoneMoved
    if matrix[new_pos] == STONE:
        new_stone_pos = (new_pos[0] + move[0], new_pos[1] + move[1]) 
        if new_stone_pos[0] < 0 or new_stone_pos[0] >= height or new_stone_pos[1] < 0 or new_stone_pos[1] >= width:
            return matrix, pos, stoneMoved
        if matrix[new_stone_pos] == WALL or matrix[new_stone_pos] == STONE:
            return matrix, pos, stoneMoved
        stoneMoved = True
        if matrix[new_stone_pos] == SWITCH:
            matrix[new_stone_pos] = STONE_PLACED_ON_SWITCH
        else:
            matrix[new_stone_pos] = STONE
    matrix[new_pos] = ARES
    matrix[pos] = FREE_SPACE
    return matrix, new_pos, stoneMoved

def draw_board(screen, matrix, height, width):
    screen.fill((255, 255, 255))
    for i in range(height):
        for j in range(width):
            rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLORS.get(matrix[i, j], (255, 255, 255)), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
    pygame.display.flip()

def animate_solution(screen, matrix, height, width, solution):
    moves = {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)}
    stones, switches, stones_on_switches, ares = find_obj_pos(matrix, height, width)
    for move in solution:
        dx, dy = moves[move.lower()]
        matrix, ares, _ = can_move(matrix, height, width, ares, (dx, dy))
        draw_board(screen, matrix, height, width)
        time.sleep(0.2)
    print("[pygame] Solution animation completed!")
    
def draw_buttons(screen):
    font = pygame.font.Font(None, 36)
    buttons = ["BFS", "DFS", "A*", "UCS", "GBFS"]
    button_rects = []

    for i, text in enumerate(buttons):
        rect = pygame.Rect(10 + i * 88, 10, 80, 40)
        pygame.draw.rect(screen, (4, 178, 217), rect) 
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  
        label = font.render(text, True, (0, 0, 0)) 
        label_rect = label.get_rect(center=rect.center)  
        screen.blit(label, label_rect)

        button_rects.append((rect, text))

    return button_rects


def main():
    filename = "input.txt"
    matrix, height, width = read_map(filename)
    if matrix is None:
        return
    
    solution = "rrdllluuRlllldrdldRRRRllllurulurrrrdrrdlDrdLrullllllurulurrrrdrruLrdllldrrrdllllllurulurrrurDrrdlLrrdllldlllurulurrrDrrrdlldllllurulurrrdDrrrdllLrrrulllurrrulllllldrdldrRRRllllurulurrrrrrdllldrrrddlUruLrdllllllurulurrrrrrdllldRldrrruLrdllldRlurrrulLrrdllllllurulurrrrrrdlllDrrrdllLrrrdLrulllLrrrrulllurrrulllllldrdldRRRdRluR"
    
    pygame.init()
    screen = pygame.display.set_mode((width * TILE_SIZE, height * TILE_SIZE))
    pygame.display.set_caption("Sokoban Solver")
    
    running = True
    selected_algorithm = None
    state = 'menu' 
    while running:
        screen.fill((255, 255, 255))
        button_rects = draw_buttons(screen)

        if state == 'menu':
            button_rects = draw_buttons(screen)
        elif state == 'running':
            draw_board(screen, matrix, height, width)
            if selected_algorithm == "DFS":
                animate_solution(screen, matrix, height, width, solution)
                state = 'menu'  
            if selected_algorithm == "BFS":
                draw_board(screen, matrix, height, width)
                time.sleep(2)
                state = 'menu'
            if selected_algorithm == "A*":
                draw_board(screen, matrix, height, width)
                time.sleep(2)
                state = 'menu'
            if selected_algorithm == "UCS":
                draw_board(screen, matrix, height, width)
                time.sleep(2)
                state = 'menu'
            if selected_algorithm == "GBFS":
                draw_board(screen, matrix, height, width)
                time.sleep(2)
                state = 'menu'
        
        pygame.display.flip() # Update the full display Surface to the screen
    

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and state == 'menu':
                x, y = event.pos
                for rect, algo in button_rects:
                    if rect.collidepoint(x, y):
                        selected_algorithm = algo
                        print(f"Selected Algorithm: {selected_algorithm}")
                        state = 'running' 

    pygame.quit()
if __name__ == "__main__":
    main()

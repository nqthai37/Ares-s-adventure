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
TILE_SIZE = 60

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
                print(f"File {filename} is empty!")
                return None, 0, 0
            height = len(lines)
            width = max(len(line) for line in lines)  
            
            matrix = np.full((height, width), FREE_SPACE, dtype=str) 
            for i in range(height):
                for j in range(len(lines[i])):
                    matrix[i, j] = lines[i][j]
            
            return matrix, height, width
    except FileNotFoundError:
        print(f"File {filename} not found!")
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

def draw_board(screen, matrix, height, width):
    screen.fill((255, 255, 255))
    draw_title(screen, TILE_SIZE)
    draw_level(screen)
    button_rects = draw_buttons(screen)
    for i in range(height):
        for j in range(width):
            offset_y = (700 - height * TILE_SIZE) // 2  # Canh giữa theo chiều dọc
            rect = pygame.Rect(0 + j * TILE_SIZE, offset_y + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLORS.get(matrix[i, j], (255, 255, 255)), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
    pygame.display.flip()
    return button_rects

def animate_solution(screen, matrix, height, width, solution):
    moves = {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)}
    stones, switches, stones_on_switches, ares = find_obj_pos(matrix, height, width)
    pause = False  # Trạng thái Pause
    button_rects = draw_buttons(screen)

    index = 0  # Biến đếm để chạy từng bước trong solution
    while index < len(solution):
        # Xử lý sự kiện trước khi di chuyển
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                for rect, algo in button_rects:
                    if rect.collidepoint(x, y):
                        if algo == "Pause":
                            pause = not pause  # Đảo trạng thái Pause
                        elif algo == "Reset":
                            return True

        # Nếu đang Pause, không chạy animation
        if pause:
            pygame.time.delay(100)
            continue

        # Xử lý di chuyển Ares
        move = solution[index]
        dx, dy = moves[move.lower()]
        new_pos = (ares[0] + dx, ares[1] + dy)

        if 0 <= new_pos[0] < height and 0 <= new_pos[1] < width:
            if matrix[new_pos[0], new_pos[1]] in [STONE, STONE_PLACED_ON_SWITCH]:
                new_stone_pos = (new_pos[0] + dx, new_pos[1] + dy)
                if 0 <= new_stone_pos[0] < height and 0 <= new_stone_pos[1] < width:
                    
                    # ⚠️ Sửa lỗi: Xử lý đúng switch sau khi đẩy đá đi
                    if matrix[new_pos[0], new_pos[1]] == STONE_PLACED_ON_SWITCH:
                        matrix[new_pos[0], new_pos[1]] = SWITCH  # Chuyển lại thành switch (.)

                    else:
                        matrix[new_pos[0], new_pos[1]] = FREE_SPACE  # Nếu không thì trở lại khoảng trống (' ')

                    # Cập nhật vị trí mới của đá
                    if matrix[new_stone_pos[0], new_stone_pos[1]] == SWITCH:
                        matrix[new_stone_pos[0], new_stone_pos[1]] = STONE_PLACED_ON_SWITCH
                    else:
                        matrix[new_stone_pos[0], new_stone_pos[1]] = STONE

            # Cập nhật vị trí của Ares
            prev_ares_pos = ares  # Lưu vị trí cũ để cập nhật lại màu

            matrix[new_pos[0], new_pos[1]] = ARES
            ares = new_pos

            # ⚠️ Sửa lỗi: Nếu vị trí cũ của Ares là switch (`.`), khôi phục lại
            if prev_ares_pos in switches:
                matrix[prev_ares_pos[0], prev_ares_pos[1]] = SWITCH
            else:
                matrix[prev_ares_pos[0], prev_ares_pos[1]] = FREE_SPACE

        draw_board(screen, matrix, height, width)
        pygame.display.flip()
        time.sleep(0.1)  

        index += 1 

    print("[pygame] Solution animation completed!")
    return False


def draw_buttons(screen):
    font = pygame.font.Font(None, 36)
    buttons = ["BFS", "DFS", "A*", "UCS", "GBFS", "Reset", "Pause"]
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



def draw_title(screen, tile_size):
    font = pygame.font.Font(None, tile_size // 2)  # Giảm kích thước chữ để cân đối hơn
    title = "SOKOBAN"
    start_x = 10  # Điểm bắt đầu của chữ
    start_y = 50  # Điều chỉnh để tiêu đề không quá cao hoặc thấp

    for i, char in enumerate(title):
        title_surface = font.render(char, True, (0, 0, 0)) 
        title_rect = title_surface.get_rect(topleft=(start_x + i * (tile_size // 2), start_y)) 
        screen.blit(title_surface, title_rect)

def draw_level(screen):
    font = pygame.font.Font(None, 36)
    buttons = [f"Level {i+1}" for i in range(10)]  # Tạo danh sách 10 level
    button_rects = []

    screen_width = screen.get_width()
    start_x = screen_width - 180  # Căn lề phải
    start_y = 100
    button_width, button_height = 160, 40
    spacing = 10

    for i, text in enumerate(buttons):
        col = i // 5  # Cột (0 hoặc 1)
        row = i % 5   # Hàng (0 đến 4)
        x = start_x + col * (button_width + spacing) 
        y = start_y + row * (button_height + spacing)

        rect = pygame.Rect(x, y, button_width, button_height)
        pygame.draw.rect(screen, (0, 128, 255), rect)  # Màu xanh dương
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Viền đen

        label = font.render(text, True, (255, 255, 255))
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
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Sokoban Solver")
    reset_flat = False
    running = True
    selected_algorithm = None
    state = 'menu' 
    while running:
        screen.fill((255, 255, 255))
        button_rects = draw_buttons(screen)
        draw_board(screen, matrix, height, width)
        
        if state == 'menu':
            button_rects = draw_buttons(screen) 
        elif state == 'running':
            draw_board(screen, matrix, height, width)
            if selected_algorithm == "DFS":
                reset_flat = animate_solution(screen, matrix, height, width, solution)
                state = 'menu'  
            if selected_algorithm == "BFS":
                draw_board(screen, matrix, height, width)
                state = 'menu'
            if selected_algorithm == "A*":
                draw_board(screen, matrix, height, width)
                state = 'menu'
            if selected_algorithm == "UCS":
                draw_board(screen, matrix, height, width)
                state = 'menu'
            if selected_algorithm == "GBFS":
                state = 'menu'
            if selected_algorithm == "Reset":
                reset_flat = True
                state = 'menu'
            if selected_algorithm == "Pause":
                state = 'menu'
            if reset_flat == True:
                matrix, height, width = read_map(filename)  
                draw_board(screen, matrix, height, width)  
                state = 'menu' 
                selected_algorithm = None
                reset_flat = False
                
        pygame.display.flip()
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
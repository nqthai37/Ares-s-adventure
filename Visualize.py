import pygame
import numpy as np
import time
from collections import deque
import heapq
from queue import Queue
import time
import psutil

# Constants
WALL = "#"
FREE_SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"

UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

direction = [UP, DOWN, LEFT, RIGHT]

matrix = []
stones_weight = []
player = None
stones = []
switches = set()
paths = []
walls = set()
distances = dict()
dead_locks = set()

class Stone:
    def __init__(self, point, weight):
        self.point = point
        self.weight = weight

    def __lt__(self, other):
        return self.weight < other.weight
    
def remove_stone(stone_list, point):
    for s in stone_list:
        if s.point == point:
            stone_list.remove(s)
            break

def find_stone(stone_list, point):
    for s in stone_list:
        if s.point == point:
            return s
    return None

# Kích thước ô vuông
TILE_SIZE = 60
HEIGHT_BOARD = 650
WIDTH_BOARD = 800
# Màu sắc
COLORS = {
    "#": (100, 100, 100),  # Wall - xám
    " ": (200, 200, 200),  # Free space - trắng
    "$": (139, 69, 19),    # Stone - nâu
    "@": (0, 0, 255),      # Ares - xanh dương
    ".": (255, 255, 0),    # Switch - vàng
    "*": (255, 165, 0)     # Stone on switch - cam
}

def reset_value():
    global matrix, stones_weight, player, stones, switches, paths, walls, distances, dead_locks
    
    matrix = []
    stones_weight = []
    player = None
    stones = []
    switches = set()
    paths = []
    walls = set()
    distances = {}
    dead_locks = set()

def set_value(file):
    global matrix, stones_weight, player, stones, switches, paths, walls
    with open(file, "r") as f:
        stones_weight = list(map(int, f.readline().strip().split()))
        for line in f:
            matrix.append(list(line.strip()))
    cnt = 0  
    for i in range(len(matrix)): 
        for j in range(len(matrix[i])):
            if matrix[i][j] != WALL:
                paths.append((i, j))
            if matrix[i][j] == ARES:
                player = (i, j)
            elif matrix[i][j] == ARES_ON_SWITCH:
                player = (i, j)
                switches.add((i, j))
            elif matrix[i][j] == STONE:
                stones.append(Stone((i, j), stones_weight[cnt]))
                cnt += 1
            elif matrix[i][j] == STONE_ON_SWITCH:
                stones.append(Stone((i, j), stones_weight[cnt]))
                cnt += 1
                switches.add((i, j))
            elif matrix[i][j] == SWITCH:
                switches.add((i, j))
            elif matrix[i][j] == WALL:
                walls.add((i, j))    
    set_distance()


def set_distance():
    global distances, switches, dead_locks
    for switch in switches:
        distances[switch] = dict()
        for path in paths:
            distances[switch][path] = 1e9
    
    q = Queue()
    for switch in switches:
        distances[switch][switch] = 0
        q.put(switch)
        while not q.empty():
            x, y = q.get()
            for dx, dy in direction:
                nx, ny = x + dx, y + dy # stone position
                px, py = nx + dx, ny + dy # player position
                if (nx, ny) in paths and distances[switch][(nx, ny)] == 1e9:
                    if (px, py) in paths:
                        distances[switch][(nx, ny)] = distances[switch][(x, y)] + 1
                        q.put((nx, ny))
          
    for path in paths:
        check = 1
        for switch in switches:
            if distances[switch][path] != 1e9:
                check = 0
                break
        if check:
            dead_locks.add(path)

def set_valid_move(player, stones):
    x, y = player
    valid_moves = []
    stone_positions = {s.point for s in stones}

    for dx, dy in direction:
        nx, ny = x + dx, y + dy
        if (nx, ny) in walls:
            continue
        if (nx, ny) in stone_positions:
            px, py = nx + dx, ny + dy
            if (px, py) not in walls and (px, py) not in stone_positions:
                valid_moves.append((dx, dy))
        else:
            valid_moves.append((dx, dy))
    return valid_moves    

def is_win(stones):
    return all(s.point in switches for s in stones)

def heuristic(stones):
    return sum(min(distances[switch][s.point] for switch in switches) for s in stones)   

def move(player, stones, direction):
    x, y = player
    dx, dy = direction
    nx, ny = x + dx, y + dy
    is_pushed = False
    is_dead_lock = False
    stones = set(stones)
    temp = 0 # weight of stone
    if find_stone(stones, (nx, ny)):
        is_pushed = True
        temp = find_stone(stones, (nx, ny)).weight
        remove_stone(stones, (nx, ny))
        stones.add(Stone((nx + dx, ny + dy), temp))
        if (nx + dx, ny + dy) in dead_locks:
            is_dead_lock = True
    stones = tuple(stones)
    player = (nx, ny)
    return player, stones, is_pushed, is_dead_lock, temp

def ucs(cur_player, cur_stones):
    node_generated = 0
    q = []
    heapq.heappush(q, (0, cur_player, cur_stones, 0, 0, [])) 
                      #cost, player, stones, steps, weight, path
    visited = set()
    best_cost = {}
    process = psutil.Process()
    mem_before = process.memory_info().rss
    
    while q:
        now_cost, now_player, now_stones, steps, weight, path = heapq.heappop(q)
        state_key = (now_player, tuple(s.point for s in now_stones))
                                # use tuple to store stones so that it can be hashable -> can be used in set and dict
        if is_win(now_stones):
            mem_after = process.memory_info().rss
            mem_usage = max(0, (mem_after - mem_before) / (1024 * 1024))
            return "UCS", steps, weight, node_generated, path, mem_usage

        visited.add(state_key)
        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, stone_weight = move(now_player, now_stones, m)

            if is_dead_lock:
                continue
            
            new_cost = now_cost + stone_weight + (1 if not is_pushed else 0)
                                # stone weight = 0 if no stone is pushed
            new_state_key = (new_player, tuple(s.point for s in new_stones))
            
            if new_state_key not in visited and new_state_key not in best_cost \
                    or new_cost < best_cost.get(new_state_key, float("inf")):
                best_cost[new_state_key] = new_cost
                heapq.heappush(q, (new_cost, new_player, new_stones, steps + 1, weight + stone_weight, path + convert_path(m, is_pushed)))    
            node_generated += 1

    print("No solution found.")
    return "UCS", 0, 0, 0, [], 0

def gbfs(cur_player, cur_stones):
    node_generated = 0
    q = []
    heapq.heappush(q, (heuristic(cur_stones), cur_player, cur_stones, 0, 0, []))  
    visited = set()
    best_cost = {}
    process = psutil.Process()
    mem_before = process.memory_info().rss
    
    while q:
        _, now_player, now_stones, steps, weight, path = heapq.heappop(q)
        state_key = (now_player, tuple(s.point for s in now_stones))
        
        if is_win(now_stones):
            mem_after = process.memory_info().rss
            mem_usage = max(0, (mem_after - mem_before) / (1024 * 1024))
            return "GBFS", steps, weight, node_generated, path, mem_usage

        visited.add(state_key)

        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, stone_weight = move(now_player, now_stones, m)
            
            if is_dead_lock:
                continue
            
            new_state_key = (new_player, tuple(s.point for s in new_stones))
            new_cost = heuristic(new_stones) + stone_weight
                       # the heuristic highlights the importance of the stone weight
            if new_state_key not in visited and new_state_key not in best_cost\
                    or new_cost < best_cost.get(new_state_key, float("inf")):    
                best_cost[new_state_key] = new_cost
                heapq.heappush(q, (new_cost, new_player, new_stones, steps + 1, weight + stone_weight, path + convert_path(m, is_pushed)))
                
            node_generated += 1

    return "GBFS", 0, 0, 0, [], 0

def Astar(cur_player, cur_stones):
    node_generated = 0
    q = []
    heapq.heappush(q, (0, cur_player, cur_stones, 0, 0, [])) 
                      # fn, player, stones, steps, weight, path
    visited = set()
    best_cost = {}
    process = psutil.Process()
    mem_before = process.memory_info().rss

    while q:
        now_cost, now_player, now_stones, steps, weight, path = heapq.heappop(q)
        state_key = (now_player, tuple(s.point for s in now_stones))
                                # use tuple to store stones so that it can be hashable -> can be used in set and dict
        if is_win(now_stones):
            mem_after = process.memory_info().rss
            mem_usage = max(0, (mem_after - mem_before) / (1024 * 1024))
            return "A*", steps, weight, node_generated, path, mem_usage

        visited.add(state_key)
        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, stone_weight = move(now_player, now_stones, m)

            if is_dead_lock:
                continue
            
            fn = now_cost + heuristic(new_stones) + stone_weight + (1 if not is_pushed else 0)
                                                    #stone weight = 0 if no stone is pushed 
            new_state_key = (new_player, tuple(s.point for s in new_stones))

            if new_state_key not in visited and new_state_key not in best_cost \
                    or fn < best_cost.get(new_state_key, float("inf")):    
                best_cost[new_state_key] = fn
                heapq.heappush(q, (fn, new_player, new_stones, steps + 1, weight + stone_weight, path + convert_path(m, is_pushed)))

            node_generated += 1
            

    print("No solution found.")
    return "A*", 0, 0, 0, [], 0

def bfs(cur_player, cur_stones):
    node_generated = 0
    q = deque([(cur_player, cur_stones, 0, 0, [])])
    visited = set()
    process = psutil.Process()
    mem_before = process.memory_info().rss

    while q:
        now_player, now_stones, steps, weight, path = q.popleft()
        state_key = (now_player, tuple(s.point for s in now_stones))
                                # use tuple to store stones so that it can be hashable -> can be used in set and dict
        visited.add(state_key)
        moves = set_valid_move(now_player, now_stones)
        # node_generated += 1
        
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, stone_weight = move(now_player, now_stones, m)

            if is_dead_lock:
                continue
            
            new_state_key = (new_player, tuple(s.point for s in new_stones))

            if new_state_key not in visited:
                if is_win(new_stones):
                    mem_after = process.memory_info().rss
                    mem_usage = max(0, (mem_after - mem_before) / (1024 * 1024))
                    return "BFS", steps + 1, weight + stone_weight, node_generated, path + convert_path(m, is_pushed), mem_usage
                q.append ([new_player, new_stones, steps + 1, weight + stone_weight, path + convert_path(m, is_pushed)])
            node_generated += 1

    print("No solution found.")
    return "BFS", 0, 0, 0, [], 0

def dfs(cur_player, cur_stones):
    node_generated = 0
    q = deque([(cur_player, cur_stones, 0, 0, [])])
    visited = set()
    process = psutil.Process()
    mem_before = process.memory_info().rss
    
    while q:
        now_player, now_stones, steps, weight, path = q.pop()
        state_key = (now_player, tuple(s.point for s in now_stones))
                                # use tuple to store stones so that it can be hashable -> can be used in set and dict
        visited.add(state_key)
        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, stone_weight = move(now_player, now_stones, m)

            if is_dead_lock:
                continue
            
            new_state_key = (new_player, tuple(s.point for s in new_stones))

            if new_state_key not in visited:
                if is_win(new_stones):
                    mem_after = process.memory_info().rss
                    mem_usage = max(0, (mem_after - mem_before) / (1024 * 1024))
                    return "DFS", steps + 1, weight + stone_weight, node_generated, path + convert_path(m, is_pushed), mem_usage
                q.append ([new_player, new_stones, steps + 1, weight + stone_weight, path + convert_path(m, is_pushed)])
            node_generated += 1

    print("No solution found.")
    return "DFS", 0, 0, 0, [], 0


def convert_path(direction, is_pushed):
    if direction == UP:
        return ['u'] if not is_pushed else ['U']
    if direction == DOWN:
        return ['d'] if not is_pushed else ['D']
    if direction == LEFT:
        return ['l'] if not is_pushed else ['L']
    if direction == RIGHT:
        return ['r'] if not is_pushed else ['R']

def measure_algorithm(algorithm, player, stones):
    start_time = time.time()
    result = algorithm(player, stones ) 
    end_time = time.time() 
    
    elapsed_time = end_time - start_time
    
    return result, elapsed_time

def draw_board(screen, title):
    screen.fill((255, 255, 255))
    draw_title(screen, 60, title)
    draw_level(screen)
    button_rects = draw_buttons(screen)
    height = len(matrix)
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            offset_y = (WIDTH_BOARD - height * TILE_SIZE) // 2  # Canh giữa theo chiều dọc
            rect = pygame.Rect(0 + j * TILE_SIZE, offset_y + i * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, COLORS.get(matrix[i][j], (255, 255, 255)), rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
    pygame.display.flip()
    return button_rects

def animate_solution(screen, solution, title):
    global player
    moves = {'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)}
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
        new_pos = (player[0] + dx, player[1] + dy)

        if 0 <= new_pos[0] < len(matrix) and 0 <= new_pos[1] < len(matrix[0]):
            if matrix[new_pos[0]][new_pos[1]] in [STONE, STONE_ON_SWITCH]:
                new_stone_pos = (new_pos[0] + dx, new_pos[1] + dy)
                if 0 <= new_stone_pos[0] < len(matrix) and 0 <= new_stone_pos[1] < len(matrix[0]):
                    
                    #  Sửa lỗi: Xử lý đúng switch sau khi đẩy đá đi
                    if matrix[new_pos[0]][new_pos[1]] == STONE_ON_SWITCH:
                        matrix[new_pos[0]][new_pos[1]] = SWITCH  # Chuyển lại thành switch (.)

                    else:
                        matrix[new_pos[0]][new_pos[1]] = FREE_SPACE  # Nếu không thì trở lại khoảng trống (' ')

                    # Cập nhật vị trí mới của đá
                    if matrix[new_stone_pos[0]][new_stone_pos[1]] == SWITCH:
                        matrix[new_stone_pos[0]][new_stone_pos[1]] = STONE_ON_SWITCH
                    else:
                        matrix[new_stone_pos[0]][new_stone_pos[1]] = STONE

            # Cập nhật vị trí của Ares
            prev_player_pos = player  # Lưu vị trí cũ để cập nhật lại màu

            matrix[new_pos[0]][new_pos[1]] = ARES
            player = new_pos

            # Sửa lỗi: Nếu vị trí cũ của Ares là switch (`.`), khôi phục lại
            if prev_player_pos in switches:
                matrix[prev_player_pos[0]][prev_player_pos[1]] = SWITCH
            else:
                matrix[prev_player_pos[0]][prev_player_pos[1]] = FREE_SPACE

        draw_board(screen, title)
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

def draw_title(screen, tile_size, in_title):
    font = pygame.font.Font(None, tile_size)  # Giảm kích thước chữ để cân đối hơn
    title = in_title
    start_x = 10  # Điểm bắt đầu của chữ
    start_y = 50  # Điều chỉnh để tiêu đề không quá cao hoặc thấp

    for i, char in enumerate(title):
        title_surface = font.render(char, True, (0, 0, 0)) 
        title_rect = title_surface.get_rect(topleft=(start_x + i * (tile_size // 2), start_y)) 
        screen.blit(title_surface, title_rect)

def draw_level(screen):
    font = pygame.font.Font(None, 36)
    buttons = [f"Level{i+1}" for i in range(10)]  # Tạo danh sách 10 level
    button_rects = []

    screen_width = screen.get_width()
    start_x = screen_width - 180  # Căn lề phải
    start_y = 100
    button_width, button_height = 160, 40
    spacing = 10

    for i, text in enumerate(buttons):
        x = start_x 
        y = start_y + i * (button_height + spacing)

        rect = pygame.Rect(x, y, button_width, button_height)
        pygame.draw.rect(screen, (0, 128, 255), rect)  # Màu xanh dương
        pygame.draw.rect(screen, (0, 0, 0), rect, 2)  # Viền đen

        label = font.render(text, True, (255, 255, 255))
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

        button_rects.append((rect, text))

    return button_rects


def main():
    global player, stones
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH_BOARD, HEIGHT_BOARD))
    pygame.display.set_caption("Sokoban Solver")
    reset_flat = False
    running = True
    selected_algorithm = None
    state = 'menu' 
    check = 0
    while running:
        screen.fill((255, 255, 255))
        button_rects = draw_buttons(screen)
        draw_board(screen, "")
        if state == 'menu':
            button_rects = draw_buttons(screen) 
            level_rect = draw_level(screen)
        elif state == 'running':
            draw_board(screen, "")
            if selected_algorithm == "DFS":
                (algorithm, steps, weight, node_generated, path, mem_usage), time = measure_algorithm(dfs, player, stones)
                reset_flat = animate_solution(screen, path, "DFS")
                state = 'menu'  
            if selected_algorithm == "BFS":
                (algorithm, steps, weight, node_generated, path, mem_usage), time = measure_algorithm(bfs, player, stones)
                reset_flat = animate_solution(screen, path, "BFS")
                state = 'menu'
            if selected_algorithm == "A*":
                (algorithm, steps, weight, node_generated, path, mem_usage), time = measure_algorithm(Astar, player, stones)
                reset_flat = animate_solution(screen, path, "A*")
                state = 'menu'
            if selected_algorithm == "UCS":
                (algorithm, steps, weight, node_generated, path, mem_usage), time = measure_algorithm(ucs, player, stones)
                reset_flat = animate_solution(screen, path, "UCS")
                state = 'menu'
            if selected_algorithm == "GBFS":
                (algorithm, steps, weight, node_generated, path, mem_usage), time = measure_algorithm(gbfs, player, stones)
                reset_flat = animate_solution(screen, path, "GBFS")
                state = 'menu'
            if selected_algorithm == "Reset":
                reset_flat = True
                state = 'menu'
            if selected_algorithm == "Pause":
                state = 'menu'
            if reset_flat == True:
                reset_value()
                set_value(filename)  
                draw_board(screen)  
                state = 'menu' 
                selected_algorithm = None
                reset_flat = False
                
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and state == 'menu':
                x, y = event.pos
                for rect, level in level_rect:
                    if rect.collidepoint(x, y):
                        reset_value()
                        filename = "Level/" + level + ".txt"
                        set_value(filename)
                        check = 1
                for rect, algo in button_rects:
                    if rect.collidepoint(x, y) and check == 1:
                        selected_algorithm = algo
                        print(f"Selected Algorithm: {selected_algorithm}")
                        state = 'running' 
    pygame.quit()
    
if __name__ == "__main__":
    main()

import heapq
from queue import Queue

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

maze = []
stones_weight = []
player = None
stones = []
switches = set()
paths = []
walls = set()
distances = dict()
dead_locks = set()

direction = [UP, DOWN, LEFT, RIGHT]

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

def set_value(file):
    global maze, stones_weight, player, stones, switches, paths, walls
    with open(file, "r") as f:
        stones_weight = list(map(int, f.readline().strip().split()))
        for line in f:
            maze.append(list(line.strip()))
    cnt = 0  
    for i in range(len(maze)): 
        for j in range(len(maze[0])):
            if maze[i][j] != WALL:
                paths.append((i, j))
            if maze[i][j] == ARES:
                player = (i, j)
            elif maze[i][j] == ARES_ON_SWITCH:
                player = (i, j)
                switches.add((i, j))
            elif maze[i][j] == STONE:
                stones.append(Stone((i, j), stones_weight[cnt]))
                cnt += 1
            elif maze[i][j] == STONE_ON_SWITCH:
                stones.append(Stone((i, j), stones_weight[cnt]))
                cnt += 1
                switches.add((i, j))
            elif maze[i][j] == SWITCH:
                switches.add((i, j))
            elif maze[i][j] == WALL:
                walls.add((i, j))    
    set_distance()  

def set_valid_move(player, stones):
    x, y = player
    valid_moves = []
    for dx, dy in direction:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(maze) and 0 <= ny < len(maze[0]) and (nx, ny) not in walls:
            if (nx, ny) in (s.point for s in stones):
                if (nx + dx, ny + dy) not in walls and \
                    (nx + dx, ny + dy) not in (s.point for s in stones):
                    valid_moves.append((dx, dy))
            else:
                valid_moves.append((dx, dy))
    return valid_moves    

def is_win(stones):
    global switches
    return switches.issubset(set(s.point for s in stones))

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
                    if (nx, ny) in paths and (px, py) in paths:
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
        
def uniform_cost_search(cur_player, cur_stones):
    node_generated = 0
    q = []
    heapq.heappush(q, (0, cur_player, cur_stones, 0, [])) 
    visited = set()
    best_cost = {}

    while q:
        weight, now_player, now_stones, steps, path = heapq.heappop(q)
        state_key = (now_player, tuple(s.point for s in now_stones))
                                # use tuple to store stones so that it can be hashable -> can be used in set and dict
        if is_win(now_stones):
            return "UCS", steps, weight, node_generated, path

        visited.add(state_key)
        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, stone_weight = move(now_player, now_stones, m)

            if is_dead_lock:
                continue
            
            new_cost = weight + stone_weight + 1
            new_state_key = (new_player, tuple(s.point for s in new_stones))

            if new_state_key in visited:
                continue
            
            if new_state_key not in best_cost or new_cost < best_cost[new_state_key]:
                best_cost[new_state_key] = new_cost
                heapq.heappush(q, (new_cost, new_player, new_stones, steps + 1, path + convert_path(m, is_pushed)))

            node_generated += 1

    print("No solution found.")
    return "UCS", 0, 0, 0, 0

def convert_path(direction, is_pushed):
    if direction == UP:
        return ['u'] if not is_pushed else ['U']
    if direction == DOWN:
        return ['d'] if not is_pushed else ['D']
    if direction == LEFT:
        return ['l'] if not is_pushed else ['L']
    if direction == RIGHT:
        return ['r'] if not is_pushed else ['R']

def main():
    global player, stones
    set_value("maze.txt")
    algorithm, steps, weight, node_generated, path = uniform_cost_search(player, stones)
    print("Algorithm:", algorithm)
    print("Steps:", steps)
    print("Weight:", weight)
    print("Node generated:", node_generated)
    print("Path:", path)
    
if __name__ == "__main__":
    main()
    
    
# def update_maze(player, direction):
#     x, y = player
#     dx, dy = direction
#     nx, ny = x + dx, y + dy
    
#     if maze[x][y] == ARES: 
#         maze[x][y] = FREE_SPACE
#     elif maze[x][y] == ARES_ON_SWITCH:
#         maze[x][y] = SWITCH
    
#     if maze[nx][ny] in (FREE_SPACE, STONE):
#         maze[nx][ny] = ARES
#     elif maze[nx][ny] in (SWITCH, STONE_ON_SWITCH):
#         maze[nx][ny] = ARES_ON_SWITCH
    
#     if maze[nx][ny] in (STONE, STONE_ON_SWITCH):
#         if maze[nx + dx][ny + dy] == FREE_SPACE:
#             maze[nx + dx][ny + dy] = STONE
#         elif maze[nx + dx][ny + dy] == SWITCH:
#             maze[nx + dx][ny + dy] = STONE_ON_SWITCH
    
#     return maze
                   
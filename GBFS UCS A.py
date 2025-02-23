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

direction = [UP, DOWN, LEFT, RIGHT]

maze = []
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
    return sum(min(abs(s.point[0] - sw[0]) + abs(s.point[1] - sw[1]) for sw in switches) for s in stones)

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

            if new_state_key not in visited and new_state_key not in best_cost:
                best_cost[new_state_key] = new_cost
                heapq.heappush(q, (new_cost, new_player, new_stones, steps + 1, path + convert_path(m, is_pushed)))
            elif new_cost < best_cost[new_state_key]:
                best_cost[new_state_key] = new_cost
                heapq.heappush(q, (new_cost, new_player, new_stones, steps + 1, path + convert_path(m, is_pushed)))

            node_generated += 1

    print("No solution found.")
    return "UCS", 0, 0, 0, 0

def greedy_best_first_search(cur_player, cur_stones):
    node_generated = 0
    q = []
    heapq.heappush(q, (heuristic(cur_stones), cur_player, cur_stones, 0, 0, []))  
    visited = set()
    best_cost = {}
    
    while q:
        _, now_player, now_stones, steps, total_weight, path = heapq.heappop(q)
        state_key = (now_player, tuple(s.point for s in now_stones))
        
        if is_win(now_stones):
            return "GBFS", steps, total_weight, node_generated, path

        visited.add(state_key)

        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, weight = move(now_player, now_stones, m)
            
            if is_dead_lock:
                continue
            
            new_state_key = (new_player, tuple(s.point for s in new_stones))
            new_cost = heuristic(new_stones)
            new_total_weight = total_weight + weight + 1 
            
            if new_state_key not in visited and new_state_key not in best_cost or new_cost < best_cost.get(new_state_key, float("inf")):
                best_cost[new_state_key] = new_cost
                heapq.heappush(q, (new_cost, new_player, new_stones, steps + 1, new_total_weight, path + convert_path(m, is_pushed)))
            node_generated += 1

    return "GBFS", 0, 0, 0, []

def A_star(cur_player, cur_stones):
    node_generated = 0
    q = []
    heapq.heappush(q, (0, 0, cur_player, cur_stones, 0, [])) 
                      # fn, weight (g(n)), player, stones, steps, path
    visited = set()
    best_cost = {}

    while q:
        _, weight, now_player, now_stones, steps, path = heapq.heappop(q)
        state_key = (now_player, tuple(s.point for s in now_stones))
                                # use tuple to store stones so that it can be hashable -> can be used in set and dict
        if is_win(now_stones):
            return "A*", steps, weight, node_generated, path

        visited.add(state_key)
        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, is_dead_lock, stone_weight = move(now_player, now_stones, m)

            if is_dead_lock:
                continue
            
            new_cost = weight + stone_weight + 1 
            hn = heuristic(new_stones)
            fn = new_cost + hn
            new_state_key = (new_player, tuple(s.point for s in new_stones))

            if new_state_key not in visited and new_state_key not in best_cost or fn < best_cost[new_state_key]:
                best_cost[new_state_key] = fn
                heapq.heappush(q, (fn, new_cost, new_player, new_stones, steps + 1, path + convert_path(m, is_pushed)))


            node_generated += 1

    print("No solution found.")
    return "A*", 0, 0, 0, 0

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
    set_value("input.txt")
    algorithm, steps, total_weight, node_generated, path = A_star(player, stones)
    print("Algorithm:", algorithm)
    print("Steps:", steps)
    print("Total Stone Weight Pushed:", total_weight)
    print("Node generated:", node_generated)
    print("Path:", "".join(path))
    
if __name__ == "__main__":
    main()
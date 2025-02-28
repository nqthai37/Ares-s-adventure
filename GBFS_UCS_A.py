import heapq
from queue import Queue
import time
import psutil
from collections import deque

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
    return "UCS", 0, 0, 0, 0, mem_usage

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
    return "A*", 0, 0, 0, 0, mem_usage

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
    return "BFS", 0, 0, 0, 0

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
    return "DFS", 0, 0, 0, 0


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

def main():
    global player, stones
    # for i in range (1,11):
    #     print ("Level " + str(i))
    #     set_value("Level/" + str(i) + ".txt")
    #     (algorithm, steps, weight, node_generated, path, mem_usage), time = measure_algorithm(ucs, player, stones)
    #     print("Algorithm:", algorithm)
    #     print("Steps:", steps)
    #     print("Total Stone Weight Pushed:", weight)
    #     print("Node generated:", node_generated)
    #     print(f"Time: {time:.2f} secs")
    #     print(f"Memory usage: {mem_usage:.2f} MB")
    #     print("Path:", "".join(path))
    #     print("")
    set_value("Level/11.txt")
    (algorithm, steps, weight, node_generated, path, mem_usage), time = measure_algorithm(bfs, player, stones)
    print("Algorithm:", algorithm)
    print("Steps:", steps)
    print("Total Stone Weight Pushed:", weight)
    print("Node generated:", node_generated)
    print(f"Time: {time:.2f} secs")
    print(f"Memory usage: {mem_usage:.2f} MB")
    print("Path:", "".join(path))
    
if __name__ == "__main__":
    main()
    
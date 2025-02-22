import heapq

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
walls = set()

class Stone:
    def __init__(self, point, weight):
        self.point = point
        self.weight = weight

    def __lt__(self, other):
        return self.weight < other.weight

def set_value(file):
    global maze, stones_weight, player, stones, switches, walls
    with open(file, "r") as f:
        stones_weight = list(map(int, f.readline().strip().split()))
        for i, line in enumerate(f):
            row = list(line.strip())
            maze.append(row)
            for j, cell in enumerate(row):
                if cell == ARES:
                    player = (i, j)
                elif cell == ARES_ON_SWITCH:
                    player = (i, j)
                    switches.add((i, j))
                elif cell == STONE:
                    stones.append(Stone((i, j), stones_weight[len(stones)]))
                elif cell == STONE_ON_SWITCH:
                    stones.append(Stone((i, j), stones_weight[len(stones)]))
                    switches.add((i, j))
                elif cell == SWITCH:
                    switches.add((i, j))
                elif cell == WALL:
                    walls.add((i, j))

def heuristic(stones):
    """Tính toán heuristic: Khoảng cách Manhattan tối thiểu từ mỗi viên đá đến các công tắc"""
    return sum(min(abs(s.point[0] - sw[0]) + abs(s.point[1] - sw[1]) for sw in switches) for s in stones)

def set_valid_move(player, stones):
    """Tìm các nước đi hợp lệ"""
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
    """Kiểm tra xem tất cả viên đá có nằm trên công tắc không"""
    return all(s.point in switches for s in stones)

def move(player, stones, direction):
    """Di chuyển nhân vật và cập nhật vị trí viên đá nếu đẩy"""
    x, y = player
    dx, dy = direction
    nx, ny = x + dx, y + dy
    is_pushed = False
    new_stones = list(stones)  
    temp = 0

    for i, s in enumerate(new_stones):
        if s.point == (nx, ny):
            is_pushed = True
            temp = s.weight
            new_stones[i] = Stone((nx + dx, ny + dy), temp)
            break

    return (nx, ny), tuple(new_stones), is_pushed, temp

def greedy_best_first_search(cur_player, cur_stones):
    """Thuật toán Greedy Best-First Search với tổng trọng số khi đẩy"""
    node_generated = 0
    q = []
    heapq.heappush(q, (heuristic(cur_stones), cur_player, cur_stones, 0, 0, []))  
    visited = set()
    
    while q:
        _, now_player, now_stones, steps, total_weight, path = heapq.heappop(q)
        state_key = (now_player, tuple(s.point for s in now_stones))
        
        if is_win(now_stones):
            return "GBFS", steps, total_weight, node_generated, path

        if state_key in visited:
            continue
        visited.add(state_key)

        moves = set_valid_move(now_player, now_stones)
        for m in moves:
            new_player, new_stones, is_pushed, weight = move(now_player, now_stones, m)
            new_state_key = (new_player, tuple(s.point for s in new_stones))
            if new_state_key in visited:
                continue

            new_total_weight = total_weight + (weight if is_pushed else 0)

            heapq.heappush(q, (heuristic(new_stones), new_player, new_stones, steps + 1, new_total_weight, path + convert_path(m, is_pushed)))
            node_generated += 1

    return "GBFS", 0, 0, 0, []


def convert_path(direction, is_pushed):
    """Chuyển đổi nước đi thành chuỗi"""
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
    algorithm, steps, total_weight, node_generated, path = greedy_best_first_search(player, stones)
    print("Algorithm:", algorithm)
    print("Steps:", steps)
    print("Total Stone Weight Pushed:", total_weight)
    print("Node generated:", node_generated)
    print("Path:", "".join(path))
    
if __name__ == "__main__":
    main()

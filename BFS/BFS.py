from collections import deque
import numpy as np

# Constants
WALL = "#"
FREE_SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_PLACED_ON_SWITCH = "*"

# Direction mapping
direction = {
    (0, 1): 'r',
    (0, -1): 'l',
    (1, 0): 'd',
    (-1, 0): 'u'
}

# Global variables
stones = []
switches = []
stones_on_switches = []
ares = None

def find_obj_pos(matrix, height, width):
    global stones, switches, stones_on_switches, ares
    stones, switches, stones_on_switches = [], [], []
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

def is_corner_deadlock(matrix, x, y):
    if (matrix[x - 1, y] == WALL and matrix[x, y - 1] == WALL) or \
       (matrix[x + 1, y] == WALL and matrix[x, y + 1] == WALL) or \
       (matrix[x - 1, y] == WALL and matrix[x, y + 1] == WALL) or \
       (matrix[x + 1, y] == WALL and matrix[x, y - 1] == WALL):
        return True
    return False

def is_double_stones_deadlock(matrix, x, y, height, width):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < height and 0 <= ny < width and matrix[nx, ny] == STONE:
            if (matrix[x - dx, y - dy] == WALL or matrix[x - dx, y - dy] == STONE) and \
               (matrix[nx + dx, ny + dy] == WALL or matrix[nx + dx, ny + dy] == STONE):
                return True
    return False

def is_blocked(matrix, x, y, height, width):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= height or ny < 0 or ny >= width or matrix[nx, ny] == WALL:
            continue
        if matrix[nx, ny] == STONE or matrix[nx, ny] == STONE_PLACED_ON_SWITCH:
            if not can_stone_move(matrix, nx, ny, height, width):
                return True
    return False

def can_stone_move(matrix, x, y, height, width):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < height and 0 <= ny < width and \
           (matrix[nx, ny] == FREE_SPACE or matrix[nx, ny] == SWITCH):
            return True
    return False

def is_deadlock(matrix, height, width):
    for stone_x, stone_y in stones:
        if is_corner_deadlock(matrix, stone_x, stone_y):
            return True
        if is_double_stones_deadlock(matrix, stone_x, stone_y, height, width):
            return True
        if is_blocked(matrix, stone_x, stone_y, height, width):
            return True
    if len(stones) > len(switches):
        return True
    return False

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

def is_solved(matrix, height, width):
    for switch_x, switch_y in switches:
        if matrix[switch_x, switch_y] != STONE_PLACED_ON_SWITCH:
            return False
    return True

def bfs(matrix, height, width, player_pos):
    print('Breadth-First Search')
    initial_state = matrix.copy()
    seen = set()
    q = deque([(initial_state, player_pos, 0, '')])
    moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]

    while q:
        state, pos, depth, path = q.popleft()
        state_hash = hash(state.tobytes())
        seen.add(state_hash)

        for move in moves:
            new_state, new_pos, stoneMoved = can_move(state.copy(), height, width, pos, move)
            deadlock = is_deadlock(new_state, height, width)
            
            new_state_hash = hash(new_state.tobytes())
            if new_state_hash in seen or deadlock:
                continue
            if stoneMoved:
                nextMove = direction[move].upper()
            else:
                nextMove = direction[move]
            q.append((new_state, new_pos, depth + 1, path + nextMove))
            print(f'[BFS] Depth {depth + 1} - {path + nextMove}')
            
            if is_solved(new_state, height, width):
                print(f'[BFS] Solution found!\n\n{path + nextMove}\nDepth {depth + 1}\n')
                return (path + nextMove, depth + 1)

    print(f'[BFS] Solution not found!\n')
    return (None, -1)

def solve_bfs(puzzle, height, width):
    matrix = puzzle
    stones, switches, stones_on_switches, ares = find_obj_pos(matrix, height, width)
    return bfs(matrix, height, width, ares)

def readInput():
    try:
        with open("input.txt", "r") as opentxt:
            lines = opentxt.readlines()
            height = len(lines)
            width = len(lines[0]) - 1 if height > 0 else 0
            matrix = np.zeros((height, width), dtype=str)

            for i in range(height):
                for j in range(width):
                    matrix[i][j] = lines[i][j]
            return matrix, height, width
    except FileNotFoundError:
        print("File 'input.txt' not found!")
        return None, 0, 0

def main():
    matrix, height, width = readInput()
    if matrix is not None:
        solve_bfs(matrix, height, width)

if __name__ == '__main__':
    main()
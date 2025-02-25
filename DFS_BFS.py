from collections import deque
import numpy as np
import time
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

# Global variables
stones = []
switches = []
ares = None
weights = []
class Stone:
    def __init__(self, x, y, weight):
        self.x = x
        self.y = y
        self.weight = weight


def read_map (filename):
    try:
        with open(filename, "r") as f:
            lines = [line.rstrip("\n") for line in f]  
            if not lines:
                print("File {filename} is empty!")
                return None, 0, 0
            global weights
            weights = list(map(int, lines[0].split()))
            height = len(lines)-1
            width = max(len(line) for line in lines)
            matrix = np.full((height, width), FREE_SPACE, dtype=str)
            for i in range(height):
                for j in range(len(lines[i+1])):
                    matrix[i, j] = lines[i+1][j]


            return matrix, height, width
    except FileNotFoundError:
        print("File {filename} not found!")
        return None, 0, 0
    
def find_obj_pos(matrix, height, width): # position: [x,y]
    global stones, switches, ares
    cnt =0
    for i in range(height):
        for j in range(width):
            if matrix[i, j] == STONE:
                stones.append(Stone(i, j,weights[cnt]))
                cnt+=1
            elif matrix[i, j] == SWITCH:
                switches.append((i, j))
            elif matrix[i, j] == STONE_PLACED_ON_SWITCH:
                stones.append(Stone(i, j,weights[cnt]))
                switches.append((i, j))
            elif matrix[i, j] == ARES:
                ares = (i, j)
            elif matrix[i, j] == ARES_ON_SWITCH:
                ares = (i, j)
                switches.append((i, j))

def is_deadlock(matrix, height, width, pos):
    if matrix[pos] == STONE:
        for move in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
            new_pos = (pos[0] + move[0], pos[1] + move[1])
            if new_pos[0] < 0 or new_pos[0] >= height or new_pos[1] < 0 or new_pos[1] >= width:
                continue
            if matrix[new_pos] == WALL:
                continue
            if matrix[new_pos] == STONE:
                new_stone_pos = (new_pos[0] + move[0], new_pos[1] + move[1])
                if new_stone_pos[0] < 0 or new_stone_pos[0] >= height or new_stone_pos[1] < 0 or new_stone_pos[1] >= width:
                    continue
                if matrix[new_stone_pos] == WALL or matrix[new_stone_pos] == STONE:
                    continue
            return False
    return True

def can_move(matrix, height, width, pos, move):
    stoneMoved = False
    new_pos = (pos[0] + move[0], pos[1] + move[1])
    # check if new position is out of the map
    if new_pos[0] < 0 or new_pos[0] >= height or new_pos[1] < 0 or new_pos[1] >= width:
        return matrix, pos, stoneMoved
    # check if new position is wall
    if matrix[new_pos] == WALL:
        return matrix, pos, stoneMoved
    if matrix[new_pos] == STONE_PLACED_ON_SWITCH:
        new_stone_pos = (new_pos[0] + move[0], new_pos[1] + move[1])
        if new_stone_pos[0] < 0 or new_stone_pos[0] >= height or new_stone_pos[1] < 0 or new_stone_pos[1] >= width:
            return matrix, pos, stoneMoved
        if matrix[new_stone_pos] == WALL or matrix[new_stone_pos] == STONE:
            return matrix, pos, stoneMoved
        stoneMoved = True
        matrix[new_stone_pos] = STONE
        matrix[new_pos] = ARES_ON_SWITCH
        matrix[pos] = FREE_SPACE
        return matrix, new_pos, stoneMoved
    if matrix[new_pos] == SWITCH:
        matrix[new_pos] = ARES_ON_SWITCH
        matrix[pos] = FREE_SPACE
        return matrix, new_pos, stoneMoved
    

    # check if new position is stone
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
    if (matrix[pos] == ARES_ON_SWITCH):
        matrix[pos] = SWITCH
    else:
        matrix[pos] = FREE_SPACE
    return matrix, new_pos, stoneMoved

def is_solved(matrix):
    return all(matrix[x, y] == STONE_PLACED_ON_SWITCH for x, y in switches)

def dfs(matrix, height, width, player_pos):
    print('Depth-First Search')
    cost =0
    stack = [(matrix.copy(), player_pos, '',cost)]
    seen = set() # check if the state is visited
    moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]
    
    while stack:
        state, pos, path,cost = stack.pop()
        state_hash = hash(state.tobytes())
        if state_hash in seen:
            continue
        seen.add(state_hash)
        # check if the game is solved
        if is_solved(state):
            print(f'[DFS] Solution found!\n\n{path}\n Cost: {cost}\n ')
            return path
        
        for move in moves:
            temp_state = state.copy() 
            new_state, new_pos, stoneMoved = can_move(temp_state, height, width, pos, move)
            if new_state is None:
                continue

            stack.append((new_state, new_pos, path + (direction[move].upper() if stoneMoved else direction[move]), cost +1))
    
    print('[DFS] Solution not found!')
    return None
def bfs(matrix, height, width, player_pos):
    print('Breadth-First Search')
    initial_state = matrix.copy()
    seen = set()
    cost =0
    q = deque([(initial_state, player_pos, 0, '',cost)])
    moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]

    while q:
        state, pos, depth, path,cost = q.popleft()
        # print(state)
        state_hash = hash(state.tobytes())
        if state_hash in seen:
            continue
        seen.add(state_hash)
        if is_solved(state):
            print(f'[BFS] Solution found!\n\n{path}\n Cost: {cost}\n')
            return path
        for move in moves:
            temp_state = state.copy()
            new_state, new_pos, stoneMoved = can_move(temp_state, height, width, pos, move)
            if new_state is None:
                continue
            q.append((new_state, new_pos, depth + 1, path + (direction[move].upper() if stoneMoved else direction[move]),cost +1))

    print(f'[BFS] Solution not found!\n')
    return (None, -1)

def solve_dfs(puzzle, height, width):
    return dfs(puzzle, height, width, ares)
def solve_bfs(puzzle, height, width):
    return bfs(puzzle, height, width, ares)

def test():
    for i in range (7,8):
        filename = "Level/" + str(i) + ".txt"
        print ("Level " + str(i))
        matrix, height, width = read_map(filename)
        find_obj_pos(matrix, height, width)
        if matrix is not None:
            time_start = time.time()
            solve_dfs(matrix, height, width)
            time_end = time.time()
            print(f"DFS execution time: {time_end - time_start} seconds")
            time_start = time.time()
            solve_bfs(matrix, height, width)
            time_end = time.time()
            print(f"BFS execution time: {time_end - time_start} seconds")

def main():
    filename = "input.txt"
    matrix, height, width = read_map(filename)
    find_obj_pos(matrix, height, width)
    if matrix is not None:
        time_start = time.time()
        solve_dfs(matrix, height, width)
        time_end = time.time()
        print(f"DFS execution time: {time_end - time_start} seconds")
        time_start = time.time()
        solve_bfs(matrix, height, width)
        time_end = time.time()
        print(f"BFS execution time: {time_end - time_start} seconds")

if __name__ == "__main__":
    test()
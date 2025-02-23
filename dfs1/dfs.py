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

def read_map (filename):
    try:
        with open(filename, "r") as f:
            lines = [line.rstrip("\n") for line in f]  
            if not lines:
                print("File {filename} is empty!")
                return None, 0, 0
            #: lines ["#####", "#.@ #", "# $ #", "#####"]
            height = len(lines)
            width = max(len(line) for line in lines)  #
            
            matrix = np.full((height, width), FREE_SPACE, dtype=str) # empty matrix
            for i in range(height):
                for j in range(len(lines[i])):
                    matrix[i, j] = lines[i][j]
            
            return matrix, height, width
    except FileNotFoundError:
        print("File {filename} not found!")
        return None, 0, 0
    
def find_obj_pos(matrix, height, width): # position: [x,y]
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
    # check if new position is out of the map
    if new_pos[0] < 0 or new_pos[0] >= height or new_pos[1] < 0 or new_pos[1] >= width:
        return matrix, pos, stoneMoved
    # check if new position is wall
    if matrix[new_pos] == WALL:
        return matrix, pos, stoneMoved
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
    matrix[pos] = FREE_SPACE
    return matrix, new_pos, stoneMoved

def is_solved(matrix, height, width, switches):
    return all(matrix[x, y] == STONE_PLACED_ON_SWITCH for x, y in switches)

def dfs(matrix, height, width, player_pos, switches):
    print('Depth-First Search')
    stack = [(matrix.copy(), player_pos, '')]
    seen = set() # check if the state is visited
    moves = [(1, 0), (-1, 0), (0, -1), (0, 1)]
    
    while stack:
        state, pos, path = stack.pop()
        state_hash = hash(state.tobytes())
        if state_hash in seen:
            continue
        seen.add(state_hash)
        # check if the game is solved
        if is_solved(state, height, width, switches):
            print(f'[DFS] Solution found!\n\n{path}\n')
            return path
        
        for move in moves:
            temp_state = state.copy() 
            new_state, new_pos, stoneMoved = can_move(temp_state, height, width, pos, move)
            new_hash = hash(new_state.tobytes())

            if new_hash in seen:
                continue
            stack.append((new_state, new_pos, path + (direction[move].upper() if stoneMoved else direction[move])))
    
    print('[DFS] Solution not found!')
    return None
def solve_dfs(puzzle, height, width):
    stones, switches, stones_on_switches, ares = find_obj_pos(puzzle, height, width)
    return dfs(puzzle, height, width, ares, switches)

def main():
    filename = "input.txt"
    matrix, height, width = read_map(filename)
    if matrix is not None:
        solve_dfs(matrix, height, width)

if __name__ == "__main__":
    main()
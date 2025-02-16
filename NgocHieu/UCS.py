import heapq

WALL = "#"
FREE_SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_PLACED_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"
UP = (0,1)
DOWN = (0, -1)
LEFT = (1, 0)
RIGHT = (-1, 0)


maze = []
direction = [UP, DOWN, LEFT, RIGHT]
    
def find_switch():
    cnt = 0
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == SWITCH:
                cnt += 1
    return cnt

def find_position():
    for i in range(len(maze)):
        for j in range(len(maze[0])):
            if maze[i][j] == ARES:
                return (i,j)
    return (0,0)

def is_valid(position, direction):
    x, y = position
    dx, dy = direction
    nx, ny = x + dx, y + dy
    if 0 <= nx < len(maze) and 0 <= ny < len(maze[0]) and maze[nx][ny] != WALL:
        if maze[nx][ny] == STONE:
            return maze[nx + dx][ny + dy] not in (STONE, WALL)
        return True
    return False    

def update_maze(position, direction):
    x, y = position
    dx, dy = direction
    nx, ny = x + dx, y + dy
    
    if maze[x][y] == ARES: 
        maze[x][y] = FREE_SPACE
    elif maze[x][y] == ARES_ON_SWITCH:
        maze[x][y] = SWITCH
    
    if maze[nx][ny] in (FREE_SPACE, STONE):
        maze[nx][ny] = ARES
    elif maze[nx][ny] in (SWITCH, STONE_PLACED_ON_SWITCH):
        maze[nx][ny] = ARES_ON_SWITCH
    
    if maze[nx][ny] in (STONE, STONE_PLACED_ON_SWITCH):
        if maze[nx + dx][ny + dy] == FREE_SPACE:
            maze[nx + dx][ny + dy] == STONE
        elif maze[nx + dx][ny + dy] == SWITCH:
            maze[nx + dx][ny + dy] == STONE_PLACED_ON_SWITCH       
    
def uniform_cost_search():
    nos = find_switch() #number of switch
    cnt = 0
    
    ares = find_position() #Ares position
    solution = []
    visited = {}
    pq = [] #priority queue
    heapq.heappush(pq, (ares, 0))
    
    while len(pq) > 0:
        p = heapq.heappop(pq)
        if maze[p[0]][p[1]] == STONE_PLACED_ON_SWITCH:
            cnt += 1
            if(cnt == nos): return solution
        visited.add(p)
        
        for dx, dy in direction:
            nx = ares[0] + dx, ny = ares[1] + dy
            if not is_valid(ares, (dx, dy)):
                continue
            if(nx, ny) not in visited and (nx, ny) not in pq:
                if(maze[nx][ny] == STONE):
                    heapq.heappush((nx, ny, p[2] + 2))
                else: heapq.heappush((nx, ny, p[2] + 1))
            elif (nx, ny)
    return False

def main():
    with open("maze.txt", "r") as f:
        for line in f:
            maze.append(list(line.strip()))      
    
    
        
if (__name__ == "__main__"):
    main()

WALL = "#"
FREE_SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_PLACED_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"
u = (0,1)
d = (0, -1)
l = (1, 0)
r = (-1, 0)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

directions = [ u, d, l, r]

class Stone:
    def __init__(self, point , weight):
        self.point = point
        self.weight = weight

def readInputFile():
    with open('TestCase/input-1.txt') as f:
        lines = f.readlines()
    return lines


class Matrix: 
    def __init__(self, matrix, agent, stone, switch):
        self.matrix = matrix
        self.agent = agent
        self.stone = stone
        self.switch = switch

    def buildMatrix(self, lines):
        stone = []
        switch = []
        for i in range(len(lines[0].split())):
            stone[i] = Stone(None, int(lines[0].split()[i]))
        matrix = []
        for i in range(1, len(lines)):
            matrix.append(lines[i].split())
            for j in range(len(lines[i].split())):
                if lines[i].split()[j] == '@':
                    self.agent = Point(i, j)
                if lines[i].split()[j] == '.':
                    switch.append(Point(i, j))
                if lines[i].split()[j] == '$':
                    stone[j].point = Point(i, j)
        self.matrix = matrix
        self.stone = stone
        self.switch = switch
    def isValid(self, point, visited):
        if point.x < 0 or point.y < 0 or point.x >= len(self.matrix) or point.y >= len(self.matrix[0]):
            return False
        if visited[point.x][point.y] == True:
            return False
        if self.matrix[point.x][point.y] == WALL:
            return False
        return True

    def BFS(self, start , finish):
        queue = []
        queue.append(self.agent)
        visited = [[False for i in range(len(self.matrix[0]))] for j in range(len(self.matrix))]
        while queue:
            path = ""
            current = queue.pop(0)
            if current == finish:
                return path
            for direction in directions:
                next = Point(current.x + direction[0], current.y + direction[1])
                if self.isValid(next, visited):
                    queue.append(next)
                    visited[next.x][next.y] = True
                    path += direction
        return path
    
                
    
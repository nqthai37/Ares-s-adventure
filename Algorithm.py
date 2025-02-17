
WALL = "#"
FREE_SPACE = " "
STONE = "$"
ARES = "@"
SWITCH = "."
STONE_PLACED_ON_SWITCH = "*"
ARES_ON_SWITCH = "+"


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
u = (0,1)
d = (0, -1)
l = (1, 0)
r = (-1, 0)
directions = [ u, d, l, r]


class Stone:
    def __init__(self, point , weight):
        self.point = point
        self.weight = weight


class Algorithm:
    def __init__(self, matrix,path, agent, stones, switches):
        self.matrix = matrix
        self.agent = agent
        self.path = path
        self.stones = stones
        self.switches = switches

    def readInputFile(self):
        with open('TestCase/input-1.txt') as f:
            lines = f.readlines()
        return lines
    
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
    
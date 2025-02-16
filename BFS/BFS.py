
# r = (1,0)
# l = (-1,0)
# u = (0,-1)
# d = (0,1)
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

directions = {"r" : Point(1,0), "l" : Point(-1,0), "u" : Point(0,-1), "d" : Point(0,1)}

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

    def BFS(self, start , finish):
        queue = []
        queue.append(self.agent)
        while queue:
            current = queue.pop(0)
            for direction in directions:
                next = Point(current.x + directions[direction].x, current.y + directions[direction].y)
                if self.matrix[next.x][next.y] == '#':
                    continue
                if self.matrix[next.x][next.y] == '.':
                    return True
                if self.matrix[next.x][next.y] == '$':
                    for s in self.stone:
                        if s.point == next:
                            s.point = Point(next.x + directions[direction].x, next.y + directions[direction].y)
                            break
                queue.append(next)
        return False
    
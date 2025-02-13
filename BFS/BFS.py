
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Stone:
    def __init__(self, point , weight):
        self.point = point
        self.weight = weight

Agent = Point(0, 0)
Stone = []
Switch = []    

def readInputFile():
    with open('TestCase/input-1.txt') as f:
        lines = f.readlines()
    return lines
def buildMatrix(lines):
    weight = lines[0].strip()

    print(weight)
    matrix = []
    for i in range(1, len(lines)):
        matrix.append(lines[i].strip())
    return matrix
def findPosition(matrix,weight):
    cnt = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == '@':
                Agent = Point(i, j)
            elif matrix[i][j] == '$':
                Stone.append(Stone(Point(i, j), weight[cnt] ))
                cnt += 1
            elif matrix[i][j] == '.':
                Switch.append(Point(i, j))

            

def main():
    lines = readInputFile()
    matrix = buildMatrix(lines)
    print(matrix)
    print(matrix[0][0])

main()
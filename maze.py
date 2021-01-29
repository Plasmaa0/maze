import pygame
from pygame import time
from pygame.draw import line
import threading
import random
import queue


class Tile():
    '''
    tile of a maze
    '''

    def __init__(self, top: bool, bottom: bool, left: bool, right: bool) -> None:
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        res = str()
        if self.top:
            res += 't|'
        if self.bottom:
            res += 'b|'
        if self.left:
            res += 'l|'
        if self.right:
            res += 'r|'
        return res


class Tilemap():
    '''
    maze
    '''

    def __init__(self, size: int) -> None:
        self.tiles = []
        self.size = size
        for i in range(size):
            self.tiles.append([None]*size)
        for x in range(size):
            for y in range(size):
                self.tiles[x][y] = Tile(True, True, True, True)

    def gettile(self, x: int, y: int):
        return self.tiles[x][y]

    def deletewall(self, c1, c2):
        x1, y1 = c1[0], c1[1]
        x2, y2 = c2[0], c2[1]
        if y2 > y1:
            self.tiles[x1][y1].bottom = False
            self.tiles[x2][y2].top = False
            return 0
        elif y2 < y1:
            self.tiles[x1][y1].top = False
            self.tiles[x2][y2].bottom = False
            return 0
        elif x2 > x1:
            self.tiles[x1][y1].right = False
            self.tiles[x2][y2].left = False
            return 0
        else:
            self.tiles[x1][y1].left = False
            self.tiles[x2][y2].right = False
            return 0

    def __repr__(self) -> str:  # повернуто на 90 градусов
        s = '\n'
        for i in range(self.size):
            stemp = str()
            for tile in self.tiles:
                stemp += str(tile[i]) + ', '
            stemp += '\n'
            s += stemp
        return s


class Game():
    '''
    *description*
    '''

    def __init__(self, size: int, doanimate: bool) -> None:
        self.complete = False
        self.doanimate = doanimate
        self.fps = 24
        self.size = size
        self.clock = pygame.time.Clock()
        self.backgroundcolor = [0, 0, 0]
        self.windowsize = 800
        self.wallcolor = [200, 60, 60]
        self.tilesize = int(self.windowsize/self.size)
        self.maze = Tilemap(self.size)
        while True:
            self.thread = threading.Thread(None, self.createmaze())
            self.thread.start()
            time.delay(1000)
            if self.complete:
                break
        # self.createmaze()
        self.thread.join()
        self.screen = pygame.display.set_mode(
            (self.windowsize, self.windowsize))
        start = [0, self.size - 1]
        finish = [self.size - 1, 0]
        self.route = self.astar(start, finish)
        while(True):
            self.draw()
            pygame.display.update()
            pygame.time.delay(100)
            self.route = self.astar(start, finish)
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if(event.key == pygame.K_q):
                        exit(0)
                if event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    finish = [int(x/self.tilesize), int(y/self.tilesize)]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    start = [int(x/self.tilesize), int(y/self.tilesize)]

    def check(self):
        if not self.complete:
            self.thread.sto

    def neighbors(self, node: list) -> list:
        neighborlist = []
        x1, y1 = node
        possible = self.possiblesteps(node)
        for neighbor in possible:
            x2, y2 = neighbor
            if x1 == x2 and y2 > y1:
                if not self.maze.tiles[x1][y1].bottom and not self.maze.tiles[x2][y2].top:
                    neighborlist.append(neighbor)
            if x1 == x2 and y2 < y1:
                if not self.maze.tiles[x1][y1].top and not self.maze.tiles[x2][y2].bottom:
                    neighborlist.append(neighbor)
            if y2 == y1 and x2 > x1:
                if not self.maze.tiles[x1][y1].right and not self.maze.tiles[x2][y2].left:
                    neighborlist.append(neighbor)
            if y2 == y1 and x2 < x1:
                if not self.maze.tiles[x1][y1].left and not self.maze.tiles[x2][y2].right:
                    neighborlist.append(neighbor)
        return neighborlist

    def astar(self, start: list, finish: list) -> list:
        def heuristic(a: list, b: list) -> int:
            x1, y1 = a
            x2, y2 = b
            return abs(x1 - x2) + abs(y1 - y2)

        def readroute(camefrom: dict, start: list, finish: list) -> list:
            route = [finish]
            current = camefrom[tuple(finish)]
            while current != 0:
                route.append(current)
                current = camefrom[tuple(current)]
            return route
        frontier = queue.PriorityQueue()
        frontier.put((0, start))
        camefrom = {}
        costsofar = {}
        camefrom[tuple(start)] = 0
        costsofar[tuple(start)] = 0
        while not frontier.empty():
            current = frontier.get()
            current = current[1]
            if current == finish:
                break
            for next1 in self.neighbors(current):
                newcost = costsofar[tuple(current)]
                if tuple(next1) not in costsofar or newcost < costsofar[tuple(next1)]:
                    costsofar[tuple(next1)] = newcost
                    priority = newcost + heuristic(finish, next1)
                    frontier.put((priority, next1))
                    camefrom[tuple(next1)] = current
        return readroute(camefrom, start, finish)

    def draw(self):
        self.screen.fill(self.backgroundcolor)
        for x in range(self.size):
            for y in range(self.size):
                t = self.maze.gettile(x, y)
                if t.top:
                    pygame.draw.line(self.screen, self.wallcolor, [
                                     x*self.tilesize + self.tilesize*0.1, y*self.tilesize + self.tilesize*0.1], [x*self.tilesize + self.tilesize*0.9, y*self.tilesize + self.tilesize*0.1])
                if t.bottom:
                    pygame.draw.line(self.screen, self.wallcolor, [x*self.tilesize + self.tilesize*0.1, y*self.tilesize + self.tilesize*0.95], [
                                     x*self.tilesize + self.tilesize*0.9, y*self.tilesize + self.tilesize*0.95])
                if t.left:
                    pygame.draw.line(self.screen, self.wallcolor, [
                                     x*self.tilesize + self.tilesize*0.1, y*self.tilesize + self.tilesize*0.1], [x*self.tilesize + self.tilesize*0.1, y*self.tilesize + self.tilesize*0.95])
                if t.right:
                    pygame.draw.line(self.screen, self.wallcolor, [x*self.tilesize + self.tilesize*0.9, y*self.tilesize + self.tilesize*0.1], [
                                     x*self.tilesize + self.tilesize*0.9, y*self.tilesize + self.tilesize*0.95])
        for i in range(1, len(self.route)):
            x1, y1 = self.route[i-1]
            x2, y2 = self.route[i]
            pygame.draw.line(self.screen, (60, 200, 100), (x1*self.tilesize + self.tilesize/2, y1*self.tilesize + self.tilesize/2),
                             (x2*self.tilesize + self.tilesize/2, y2*self.tilesize + self.tilesize/2), int(self.tilesize/10))

    def alltiles(self):
        alltiles = []
        for x in range(self.size):
            for y in range(self.size):
                alltiles.append([x, y])
        return alltiles

    def possiblesteps(self, coords: list) -> list:
        x, y = coords
        # print(coords)
        neighbors = [[x+1, y], [x-1, y], [x, y+1], [x, y-1]]
        for k, neib in enumerate(neighbors):
            if neib not in self.alltiles():
                neighbors.pop(k)
        return neighbors

    def createmaze(self):
        print("started creating")
        def makeroute(route: list):
            for i in range(1, len(route)):
                self.maze.deletewall(route[i - 1], route[i])

        def allvisited() -> bool:
            for layer in self.maze.tiles:
                for i in layer:
                    if i.top and i.bottom and i.left and i.right:
                        return False
            return True
        alltiles = self.alltiles()
        visited = []
        finish = [random.randrange(0, self.size, 1),
                  random.randrange(0, self.size, 1)]
        visited.append(finish)
        start = [random.randrange(0, self.size, 1),
                 random.randrange(0, self.size, 1)]
        while(start == finish):
            start = [random.randrange(0, self.size, 1),
                     random.randrange(0, self.size, 1)]
        route = []
        route.append(start)
        while(not allvisited()):
            current = random.choice(self.possiblesteps(route[-1]))
            if current in route:
                route.clear()
                route.append(start)
            else:
                route.append(current)
                if current in visited:
                    makeroute(route)
                    print(f'{int(100*len(visited)/len(alltiles))}%')
                    for i in route:
                        visited.append(i)
                    visited.pop()
                    notvisited = [i for i in alltiles if i not in visited]
                    try:
                        start = random.choice(notvisited)
                    except IndexError:
                        break
                    route.clear()
                    route.append(start)
        self.complete = True


if __name__ == '__main__':
    Game(int(input()), True)

import pygame
import random
import queue
import time
from functools import lru_cache
import queue


LOG = False


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

    def reset(self):
        for x in range(self.size):
            for y in range(self.size):
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
    Main game class
    '''

    def __init__(self, size: int) -> None:
        print('Play or watch (1/2)?')
        self.a_star = True
        if int(input()) == 1:
            self.playerposition = [0, size - 1]
            self.a_star = False
        if size < 15 and self.a_star:
            print(
                "do you want to visualize distance from start to different maze nodes?(0/1) (time expensive)")
            self.visualise = int(input()) == 1
        else:
            self.visualise = False
        t1 = time.time()
        self.size = size
        self.backgroundcolor = [46, 44, 47]
        self.windowsize = 800
        self.wallcolor = [114, 155, 121]
        self.tilesize = int(self.windowsize/self.size)
        self.maze = Tilemap(self.size)
        self.createmaze()
        self.start = [0, self.size - 1]
        self.finish = [self.size - 1, 0]
        if self.a_star:
            self.route = self.astar(tuple(self.start), tuple(self.finish))
        else:
            self.route = []
        pygame.font.init()
        self.myfont = pygame.font.SysFont('arial', 30 - self.size)
        if self.visualise:
            self.longestdist = self.longestroute()
        t2 = time.time()
        if LOG:
            print(f'finished initializing in: {t2-t1}')
        self.screen = pygame.display.set_mode(
            (self.windowsize, self.windowsize))
        self.prevfinish = None
        self.prevstart = None
        if self.a_star:
            self.route = self.astar(tuple(self.start), tuple(self.finish))
        self.draw(self.visualise)
        pygame.display.update()
        print("Opening the window. Press Q to exit.")
        while(True):
            self.update()

    def update(self):
        t1 = time.time()
        if not self.a_star:
            if self.playerposition == self.finish:
                self.playerposition = self.start
                self.restart()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                new = []
                if(event.key == pygame.K_q):
                    pygame.quit()
                    exit(0)
                elif(event.key == pygame.K_r):
                    self.restart()
                elif(event.key == pygame.K_w and self.canstep('UP') and not self.a_star):
                    new = [self.playerposition[0], self.playerposition[1] - 1]
                elif(event.key == pygame.K_a and self.canstep('LEFT') and not self.a_star):
                    new = [self.playerposition[0] - 1, self.playerposition[1]]
                elif(event.key == pygame.K_s and self.canstep('DOWN') and not self.a_star):
                    new = [self.playerposition[0], self.playerposition[1] + 1]
                elif(event.key == pygame.K_d and self.canstep('RIGHT') and not self.a_star):
                    new = [self.playerposition[0] + 1, self.playerposition[1]]
                if new in self.alltiles() and not self.a_star:
                    self.playerposition = new
                self.draw(False)
                pygame.display.update()
            if event.type == pygame.MOUSEMOTION and self.a_star:
                x, y = event.pos
                self.finish = [int(x/self.tilesize) if int(x/self.tilesize) < self.size else self.size - 1, int(
                    y/self.tilesize) if int(y/self.tilesize) < self.size else self.size - 1]
                if self.finish != self.prevfinish:
                    self.prevfinish = self.finish
                    self.route = self.astar(
                        tuple(self.start), tuple(self.finish))
                    self.draw(False if self.size > 10 else True)
                    if not LOG:
                        pygame.display.set_caption(
                            f'distance: {len(self.astar(tuple(self.start), tuple(self.finish))) - 1}')
                    pygame.display.update()
            if event.type == pygame.MOUSEBUTTONDOWN and self.a_star:
                x, y = event.pos
                self.start = [int(x/self.tilesize) if int(x/self.tilesize) < self.size else self.size - 1, int(
                    y/self.tilesize) if int(y/self.tilesize) < self.size else self.size - 1]
                if self.start != self.prevstart:
                    self.prevstart = self.start
                    self.route = self.astar(
                        tuple(self.start), tuple(self.finish))
                    self.draw(True)
                    pygame.display.update()
        t2 = time.time()
        if LOG:
            try:
                pygame.display.set_caption(f'{round(1/(t2-t1))} FPS')
            except ZeroDivisionError:
                pass

    def restart(self):
        self.maze = Tilemap(self.size)
        self.createmaze()
        self.prevfinish = None
        self.prevstart = None
        self.start = [0, self.size - 1]
        self.finish = [self.size - 1, 0]
        if self.a_star:
            self.route = self.astar(tuple(self.start), tuple(self.finish))
        self.playerposition = self.start
        self.draw(self.visualise)
        pygame.display.update()

    def draw(self, visualisecells: bool):
        self.screen.fill(self.backgroundcolor)
        for x in range(self.size):
            for y in range(self.size):
                t = self.maze.gettile(x, y)
                if self.visualise and visualisecells:
                    dist = len(self.astar(tuple([x, y]), tuple(self.start)))
                    if self.longestdist != None:
                        r = 255 - dist/self.longestdist*255
                    else:
                        r = abs((255 - dist/(self.size*2*(2**(1/2)))*255)/2)
                    try:
                        pygame.draw.rect(self.screen, (r, r, r), [
                            x*self.tilesize, y*self.tilesize, (x + 1)*self.tilesize, (y + 1)*self.tilesize])
                    except ValueError:
                        print(r, dist, self.longestdist)
                    txt = str(dist - 1)
                    textsurface = self.myfont.render(txt, False, (255, 0, 0))
                    self.screen.blit(textsurface, [
                                    (x+0.6)*self.tilesize, (y+0.6)*self.tilesize, (x+0.9)*self.tilesize, (y+0.9)*self.tilesize])
                w = int(self.tilesize/5)
                if t.top:
                    pygame.draw.line(self.screen, self.wallcolor, [x*self.tilesize, y*self.tilesize], [
                                     x*self.tilesize + self.tilesize, y*self.tilesize], w)
                if t.bottom:
                    pygame.draw.line(self.screen, self.wallcolor, [x*self.tilesize, y*self.tilesize + self.tilesize], [
                                     x*self.tilesize + self.tilesize, y*self.tilesize + self.tilesize], w)
                if t.left:
                    pygame.draw.line(self.screen, self.wallcolor, [x*self.tilesize, y*self.tilesize], [
                                     x*self.tilesize, y*self.tilesize + self.tilesize], w)
                if t.right:
                    pygame.draw.line(self.screen, self.wallcolor, [x*self.tilesize + self.tilesize, y*self.tilesize], [
                                     x*self.tilesize + self.tilesize, y*self.tilesize + self.tilesize], w)
        pygame.draw.rect(self.screen, (120, 200, 100), [self.start[0]*self.tilesize+0.3*self.tilesize,
                                                        self.start[1]*self.tilesize + 0.3*self.tilesize, 0.3*self.tilesize, 0.3*self.tilesize])
        pygame.draw.rect(self.screen, (120, 0, 100), [self.finish[0]*self.tilesize+0.3*self.tilesize,
                                                      self.finish[1]*self.tilesize + 0.3*self.tilesize, 0.3*self.tilesize, 0.3*self.tilesize])
        if not self.a_star:
            pygame.draw.rect(self.screen, (0, 100, 250), [self.playerposition[0]*self.tilesize+0.3*self.tilesize,
                                                          self.playerposition[1]*self.tilesize + 0.3*self.tilesize, 0.3*self.tilesize, 0.3*self.tilesize])
        for i in range(1, len(self.route)):
            x1, y1 = self.route[i-1]
            x2, y2 = self.route[i]
            percent = 1 - i/len(self.route)
            pygame.draw.line(self.screen, (120*percent, 200*(1-percent), 100), (x1*self.tilesize + self.tilesize/2, y1*self.tilesize + self.tilesize/2),
                             (x2*self.tilesize + self.tilesize/2, y2*self.tilesize + self.tilesize/2), int(self.tilesize/10))

    def longestroute(self):
        if self.size > 12:
            return None
        print('use accurate alogithm for better vizualization? (time expensive!!!) (0/1)')
        if int(input()) != 1:
            return None
        else:
            tt = time.time()
            m = 0
            t1 = None
            t2 = None
            a = self.alltiles()
            for i in range(0, len(a)):
                for j in range(i, len(a)):
                    d = len(self.astar(tuple(a[i]), tuple(a[j])))
                    if d > m:
                        m = d
                        t1 = a[i]
                        t2 = a[j]
            if LOG:
                print(
                    f'the longest route length is {m} between {t1} and {t2}. calculated in {time.time() - tt}')
            return m

    def canstep(self, direction: str):
        if direction == 'UP':
            return not self.maze.tiles[self.playerposition[0]][self.playerposition[1]].top
        if direction == 'DOWN':
            return not self.maze.tiles[self.playerposition[0]][self.playerposition[1]].bottom
        if direction == 'LEFT':
            return not self.maze.tiles[self.playerposition[0]][self.playerposition[1]].left
        if direction == 'RIGHT':
            return not self.maze.tiles[self.playerposition[0]][self.playerposition[1]].right

    # @lru_cache(typed=True)
    def neighbors(self, node: tuple) -> list:
        neighborlist = []
        x1, y1 = node
        possible = self.possiblesteps(tuple(node))
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

    # @lru_cache(typed=True)
    def astar(self, start: tuple, finish: tuple) -> list:
        @lru_cache(typed=True)
        def heuristic(a: tuple, b: tuple) -> int:
            x1, y1 = a
            x2, y2 = b
            return abs(x1 - x2) + abs(y1 - y2)

        def readroute(camefrom: dict, finish: list) -> list:
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
            for next1 in self.neighbors(tuple(current)):
                newcost = costsofar[tuple(current)]
                if tuple(next1) not in costsofar or newcost < costsofar[tuple(next1)]:
                    costsofar[tuple(next1)] = newcost
                    priority = newcost + heuristic(tuple(finish), tuple(next1))
                    frontier.put((priority, next1))
                    camefrom[tuple(next1)] = current
        return readroute(camefrom, finish)

    def alltiles(self):
        alltiles = []
        for x in range(self.size):
            for y in range(self.size):
                alltiles.append([x, y])
        return alltiles

    @lru_cache(typed=True)
    def possiblesteps(self, coords: tuple) -> list:
        x, y = coords
        neighbors = [[x+1, y], [x-1, y], [x, y+1], [x, y-1]]
        if x > 0 and x < self.size-1 and y > 0 and y < self.size-1:
            return neighbors
        for k, neib in enumerate(neighbors):
            if neib not in self.alltiles():
                neighbors.pop(k)
        return neighbors

    def createmaze(self):
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
        attempts = 0
        maxattempts = 100*(self.size**2)
        maxroute = (2*self.size)**2
        prev = None
        if not LOG:
            prev = -1
        while(not allvisited()):
            current = random.choice(self.possiblesteps(tuple(route[-1])))
            if current in route:
                attempts += 1
                route.clear()
                route.append(start)
            elif attempts > maxattempts or len(route) > maxroute:
                if LOG:
                    print("generation failure. new attempt.")
                route.clear()
                start = [random.randrange(
                    0, self.size, 1), random.randrange(0, self.size, 1)]
                while(start == finish):
                    start = [random.randrange(0, self.size, 1),
                             random.randrange(0, self.size, 1)]
                route.append(start)
                attempts = 0
                self.maze.reset()
                visited.clear()
                visited.append(finish)
                if LOG:
                    prev = 0
            else:
                route.append(current)
                if current in visited:
                    makeroute(route)
                    percent = int(100*len(visited)/len(alltiles))
                    percent = round(percent/10)*10
                    if (percent != prev and LOG) or (percent > prev):
                        prev = percent
                        print(f"{percent}%")
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
        if LOG:
            print(f'{attempts} attempts of {maxattempts} max attemps')


if __name__ == '__main__':
    try:
        print("Log? (1/0)")
        LOG = int(input()) == 1
        print("type in size of maze:")
        Game(int(input()))
    except KeyboardInterrupt:
        print("keyboard interrupt. exiting.")
        pass

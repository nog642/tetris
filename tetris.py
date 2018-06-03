#!/usr/bin/env python
import copy
import numpy as np
import profile
import pygame
import random
import threading
import time
pygame.init()


TEXT_COLOR = (204, 204, 204)
BG_COLOR = (28, 28, 28)
COLOR = {
    0: BG_COLOR,
    1: (255, 204, 0),
    2: (0, 153, 153),
    3: (153, 51, 102),
    4: (255, 102, 0),
    5: (0, 102, 153),
    6: (51, 153, 102),
    7: (255, 80, 80)
}
KEY = {
    'O': 1,
    'I': 2,
    'T': 3,
    'L': 4,
    'J': 5,
    'S': 6,
    'Z': 7
}
PIECES = {
    'O': {
        'N': np.array([[0, 0, 1, 1],
                       [0, 0, 1, 1],
                       [0, 0, 0, 0],
                       [0, 0, 0, 0]]),
        'E': np.array([[0, 0, 1, 1],
                       [0, 0, 1, 1],
                       [0, 0, 0, 0],
                       [0, 0, 0, 0]]),
        'S': np.array([[0, 0, 1, 1],
                       [0, 0, 1, 1],
                       [0, 0, 0, 0],
                       [0, 0, 0, 0]]),
        'W': np.array([[0, 0, 1, 1],
                       [0, 0, 1, 1],
                       [0, 0, 0, 0],
                       [0, 0, 0, 0]])
    },
    'I': {
        'N': np.array([[0, 0, 0, 0],
                       [2, 2, 2, 2],
                       [0, 0, 0, 0],
                       [0, 0, 0, 0]]),
        'E': np.array([[0, 0, 2, 0],
                       [0, 0, 2, 0],
                       [0, 0, 2, 0],
                       [0, 0, 2, 0]]),
        'S': np.array([[0, 0, 0, 0],
                       [0, 0, 0, 0],
                       [2, 2, 2, 2],
                       [0, 0, 0, 0]]),
        'W': np.array([[0, 2, 0, 0],
                       [0, 2, 0, 0],
                       [0, 2, 0, 0],
                       [0, 2, 0, 0]])
    },
    'T': {
        'N': np.array([[0, 3, 0],
                       [3, 3, 3],
                       [0, 0, 0]]),
        'E': np.array([[0, 3, 0],
                       [0, 3, 3],
                       [0, 3, 0]]),
        'S': np.array([[0, 0, 0],
                       [3, 3, 3],
                       [0, 3, 0]]),
        'W': np.array([[0, 3, 0],
                       [3, 3, 0],
                       [0, 3, 0]])
    },
    'L': {
        'N': np.array([[0, 0, 4],
                       [4, 4, 4],
                       [0, 0, 0]]),
        'E': np.array([[0, 4, 0],
                       [0, 4, 0],
                       [0, 4, 4]]),
        'S': np.array([[0, 0, 0],
                       [4, 4, 4],
                       [4, 0, 0]]),
        'W': np.array([[4, 4, 0],
                       [0, 4, 0],
                       [0, 4, 0]])
    },
    'J': {
        'N': np.array([[5, 0, 0],
                       [5, 5, 5],
                       [0, 0, 0]]),
        'E': np.array([[0, 5, 5],
                       [0, 5, 0],
                       [0, 5, 0]]),
        'S': np.array([[0, 0, 0],
                       [5, 5, 5],
                       [0, 0, 5]]),
        'W': np.array([[0, 5, 0],
                       [0, 5, 0],
                       [5, 5, 0]])
    },
    'S': {
        'N': np.array([[0, 6, 6],
                       [6, 6, 0],
                       [0, 0, 0]]),
        'E': np.array([[0, 6, 0],
                       [0, 6, 6],
                       [0, 0, 6]]),
        'S': np.array([[0, 0, 0],
                       [0, 6, 6],
                       [6, 6, 0]]),
        'W': np.array([[6, 0, 0],
                       [6, 6, 0],
                       [0, 6, 0]])
    },
    'Z': {
        'N': np.array([[7, 7, 0],
                       [0, 7, 7],
                       [0, 0, 0]]),
        'E': np.array([[0, 0, 7],
                       [0, 7, 7],
                       [0, 7, 0]]),
        'S': np.array([[0, 0, 0],
                       [7, 7, 0],
                       [0, 7, 7]]),
        'W': np.array([[0, 7, 0],
                       [7, 7, 0],
                       [7, 0, 0]])
    },
}
WIDTH, HEIGHT = 1152, 648
ROTATION_ORDER = ['N', 'E', 'S', 'W']


def tetrimino_gen():
    bag = KEY.keys()
    while True:
        random.shuffle(bag)
        for tetrimino in bag:
            yield tetrimino


class Overlap(Exception):
    pass


def draw_rect_outline(surface, fill_color, outline_color, rect, border=1):
    surface.fill(outline_color, rect)
    surface.fill(fill_color, rect.inflate(-border*2, -border*2))


class Display(object):

    def __init__(self, screen):

        self.screen = screen
        self.screen.fill((28, 28, 28))
        self.grid = pygame.Rect(
            600,
            (HEIGHT - (30 * 20 + 21 + 2)) // 2,
            30 * 10 + 11 + 2,
            30 * 20 + 21 + 2
        )
        self.next_box = pygame.Rect(
            400,
            (HEIGHT - (30 * 20 + 21 + 2)) // 2,
            180,
            180
        )
        draw_rect_outline(
            self.screen,
            BG_COLOR,
            TEXT_COLOR,
            self.grid
        )
        draw_rect_outline(
            self.screen,
            BG_COLOR,
            TEXT_COLOR,
            self.next_box
        )
        self.update()

    def draw_next(self, grid):
        h, w = grid.shape
        x0 = self.next_box.topleft[0]
        x1 = self.next_box.topright[0]
        y0 = self.next_box.topleft[1]
        y1 = self.next_box.bottomleft[1]
        self.screen.fill(BG_COLOR, pygame.Rect(
            x0 + 1,
            y0 + 1,
            self.next_box.width - 2,
            self.next_box.height - 2
        ))
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell:
                    self.screen.fill(COLOR[cell], pygame.Rect(
                        x0 + (x1 - x0 - (w * 30 + w - 1)) // 2 + 31 * x,
                        y0 + (y1 - y0 - (h * 30 + h - 1)) // 2 + 31 * y,
                        30,
                        30
                    ))

    def draw_cell(self, (x, y), filled, color):
        rect = pygame.Rect(
            602 + 31 * x,
            self.grid.topleft[1] + 2 + 31 * y,
            30,
            30
        )
        if filled:
            self.screen.fill(color, rect)
        else:
            draw_rect_outline(self.screen, BG_COLOR, color, rect)

    @staticmethod
    def update():
        pygame.display.update()


class Tetris(object):

    def __init__(self, display):
        self.current_location = None
        self.current_type = None
        self.current_orientation = 'N'
        self.placed = np.zeros((40, 10), dtype=int)
        self.display = display
        self.level = 1
        self.gen = tetrimino_gen()
        self.next_piece = next(self.gen)
        self.saved = self.compute_grid()
        self.game_over = False
        self.ghost = []
        self.ghost_location = None
        self.previous_ghost = []
        self.to_lock = False
        self.fall_wait = (.8 - ((self.level - 1) * .007))**(self.level - 1)

    def location_to_sparse(self, location):
        sparse = []
        for y, row in enumerate(PIECES[self.current_type][self.current_orientation]):
            for x, cell in enumerate(row):
                if cell:
                    sparse.append((y + location[0], x + location[1], cell))
        return sparse

    def compute_grid(self):
        grid = self.placed.copy()
        if self.current_type is None:
            return grid
        for y, x, cell in self.location_to_sparse(self.current_location):
            if cell:
                if grid[y, x] != 0:
                    raise Overlap
                if y >= 20:
                    raise Overlap
                    print 'OVERLAP RAISED'
                if not 0 <= x <= 9:
                    raise Overlap
                grid[y, x] = cell
        return grid

    def falling(self):
        while True:
            start = time.time()
            while True:
                time.sleep(.005)
                if self.to_lock:
                    return
                if time.time() - start > self.fall_wait:
                    break
            self.fall()
            print 'time between falls: {}'.format(time.time() - start)

    def fall(self):
        self.current_location[0] += 1
        self.update()

    def right(self):
        current = copy.copy(self.current_location)
        new = copy.copy(self.current_location)
        new[1] += 1
        for _, x, _ in self.location_to_sparse(new):
            if not 0 <= x <= 9:
                return
        self.current_location = new
        try:
            self.update()
        except Overlap:
            self.current_location = current

    def left(self):
        current = copy.copy(self.current_location)
        new = copy.copy(self.current_location)
        new[1] -= 1
        for _, x, _ in self.location_to_sparse(new):
            if not 0 <= x <= 9:
                return
        self.current_location = new
        try:
            self.update()
        except Overlap:
            self.current_location = current

    def rotate(self):
        prev_orientation = self.current_orientation
        self.current_orientation = ROTATION_ORDER[(ROTATION_ORDER.index(self.current_orientation) + 1) % 4]
        try:
            self.update()
        except Overlap:
            self.current_orientation = prev_orientation

    def spawn(self):
        piece = self.next_piece
        self.next_piece = next(self.gen)
        self.display.draw_next(PIECES[self.next_piece]['N'])
        self.current_type = piece
        self.current_location = [0, 0]
        self.current_orientation = 'N'
        self.update()
        threading.Thread(target=self.falling).start()

    def update(self):
        grid = self.compute_grid()
        changed = []
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if self.saved[y, x] != grid[y, x]:
                    changed.append((y, x, grid[y, x]))
        for y, x, color in changed:
            self.display.draw_cell((x, y), True, COLOR[color])
        self.saved = grid
        self.calculate_ghost()
        for y, x in self.previous_ghost:
            if not grid[y, x]:
                self.display.draw_cell((x, y), True, BG_COLOR)
        self.previous_ghost = []
        for y, x in self.ghost:
            if not grid[y, x]:
                self.display.draw_cell((x, y), False, COLOR[KEY[self.current_type]])
                self.previous_ghost.append((y, x))
        self.display.update()
        if self.current_location == self.ghost_location:
            threading.Thread(target=self.lock).start()
        else:
            self.to_lock = False

    def lock(self):
        self.to_lock = True
        time.sleep(.5)
        if self.to_lock:
            self.placed = self.saved
            self.current = []
            self.spawn()
            # todo detect row completion
            for i, row in enumerate(self.placed):
                if all(row):
                    print self.placed
                    self.placed[1:i + 1] = self.placed[:1]
                    self.update()

    def calculate_ghost(self):
        current = copy.copy(self.current_location)
        new = current
        collision = False
        while not collision:
            current = copy.copy(new)
            new[0] += 1
            for y, x, _ in self.location_to_sparse(new):
                if y >= 20:
                    collision = True
                    break
                if self.placed[y, x] != 0:
                    collision = True
                    break
        self.ghost_location = current
        self.ghost = [(y, x) for y, x, _ in self.location_to_sparse(current)]


def interface(game):
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.KEYUP])
    while not game.game_over:
        event = pygame.event.poll()
        if event.type != pygame.NOEVENT:
            print event
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                game.left()
            elif event.key == pygame.K_RIGHT:
                game.right()
            elif event.key == pygame.K_DOWN:
                game.fall_wait /= 20
            elif event.key == pygame.K_UP:
                game.rotate()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                game.fall_wait = (.8 - ((game.level - 1) * .007))**(game.level - 1)


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    display = Display(screen)
    game = Tetris(display)
    threading.Thread(target=interface, args=(game,)).start()
    game.spawn()


if __name__ == '__main__':
    main()
    # profile.run('main()')

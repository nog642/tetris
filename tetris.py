#!/usr/bin/env python
import profile
import random
import threading
import time
import numpy as np
import pygame
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
        self.current = []
        self.current_type = None
        self.placed = np.zeros((40, 10), dtype=int)
        self.display = display
        self.level = 1
        self.gen = tetrimino_gen()
        self.next_piece = next(self.gen)
        self.saved = self.compute_grid()
        self.game_over = False
        self.ghost = []
        self.previous_ghost = []
        self.to_lock = False
        self.fall_wait = (.8 - ((self.level - 1) * .007))**(self.level - 1)
        # self.current_box = None

    def compute_grid(self):
        grid = self.placed.copy()
        for y, x in self.current:
            if grid[y, x] != 0:
                raise Overlap
            grid[y, x] = KEY[self.current_type]
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
        new = []
        for y, x in self.current:
            new.append((y + 1, x))
        self.current = new
        self.update()

    def right(self):
        new = []
        current = self.current
        for y, x in current:
            new_x = x + 1
            if new_x < 0 or new_x > 9:
                return
            new.append((y, new_x))
        self.current = new
        try:
            self.update()
        except Overlap:
            self.current = current

    def left(self):
        new = []
        current = self.current
        for y, x in current:
            new_x = x - 1
            if new_x < 0 or new_x > 9:
                return
            new.append((y, new_x))
        self.current = new
        try:
            self.update()
        except Overlap:
            self.current = current

    def rotate(self):
        pass

    def spawn(self):
        piece = self.next_piece
        self.next_piece = next(self.gen)
        self.display.draw_next(PIECES[self.next_piece]['N'])
        self.current_type = piece
        if self.current:
            raise Exception("'current' attribute must be empty before spawning")
        piece_arr = PIECES[piece]['N']
        for y, row in enumerate(piece_arr):
            for x, cell in enumerate(row):
                if cell:
                    self.current.append((y - 2, x + 5 - piece_arr.shape[1] // 2))
        # self.current_box = (-2, 5 - piece_arr.shape[1] // 2)
        # self.display.draw_cell(self.current_box[::-1], True, TEXT_COLOR)
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
        if self.current == self.ghost:
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
        current = self.current
        new = current
        collision = False
        while not collision:
            current = new
            new = []
            for y, x in current:
                new.append((y + 1, x))
                if y + 1 > 19:
                    collision = True
            for y, x in new:
                if self.placed[y, x]:
                    collision = True
        self.ghost = current


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
                pass
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

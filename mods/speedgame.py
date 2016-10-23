import tkinter

from pysweep import Timer

import random

game_mode_name = "Speed Game"
class SpeedGame:
    hooks = {}
    required_events = [
        ("pysweep", "<F2>"),
        ("pysweep", "<F3>"),
    ]
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("gamedisplaymanager", "TileOpen"): [self.tile_open],
            ("gamedisplaymanager", "FaceClicked"): [self.new_game],
            ("gamedisplaymanager", "TileDepress"):   [self.tile_depress],
            ("gamedisplaymanager", "TileUndepress"): [self.tile_undepress],

            ("pysweep", "<F2>"): [self.new_game],
            ("pysweep", "<F3>"): [(lambda hn,e:self.reset_game())],

            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }
        self.temporarily_down = []
        self.speed_game_squares = []
        self.num_squares = 5

    def modsloaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.gamemodeselector.register_game_mode(game_mode_name)

        self.gamedisplay = self.pysweep.gamedisplay

        self.timer = Timer(self.master, self.timercallback, period=0.001, resolution=0.001)

    def timercallback(self, elapsed, sincelasttick):
        self.gamedisplay.set_timer(int(elapsed*1000))

    def new_game(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplay.size
        area = width*height
        if not 0 <= self.num_squares < area:
            self.num_squares = 0
        squares = []
        i = 0
        while i < self.num_squares:
            rand = random.randint(0, area-1)
            if rand not in squares:
                squares.append(rand)
                i += 1
        self.speed_game_original = squares[:]
        self.reset_game()

    def reset_game(self):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        width, height = self.gamedisplay.size
        area = width*height
        squares = self.speed_game_original[:]
        self.speed_game_squares = squares[:]
        for i in range(area):
            row = i//width
            col = i%width
            if i in squares:
                self.gamedisplay.set_tile_unopened(row, col)
            else:
                self.gamedisplay.set_tile_number(row, col, 0)
        self.gamedisplay.set_face_happy()
        self.timer.start_timer()

    def tile_open(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return

        row, col = e.row, e.col

        width, height = self.gamedisplay.size
        if (0 <= col < width and 0 <= row < height):
            self.gamedisplay.set_tile_number(row, col, 0)
            i = row*width + col
            if i in self.speed_game_squares:
                self.speed_game_squares.remove(i)
            if len(self.speed_game_squares) == 0:
                self.timer.stop_timer()
                self.gamedisplay.set_face_cool()

    def tile_depress(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_tile_number(e.row, e.col, 0)
    def tile_undepress(self, hn, e):
        if not self.gamemodeselector.is_enabled(game_mode_name):
            return
        self.gamedisplay.set_tile_unopened(e.row, e.col)

mods = {"SpeedGame": SpeedGame}

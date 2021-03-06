import tkinter

import sys
import bisect

from pysweep import Menu

class GameModeSelector:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.modsloaded],
        }

        self.gamemodes = []
        self.default = None
        self.currentgamemode = None
        self.menu = None

    def modsloaded(self, hn, e):
        if not self.menu:
            self.menu = tkinter.Menu(Menu.menubar, tearoff=0)

            self.menuvar = tkinter.StringVar()
            self.menu.add_separator()
            self.menu.add_radiobutton(label="None", variable=self.menuvar, command=self.cancel)
            self.menu.invoke(1)
            Menu.add_menu("Game", self.menu)

        self.master.after(0, self.set_default)

    def cancel(self):
        if (self.currentgamemode != None):
            self.pysweep.handle_event(("gamemode", "DisableGameMode"), self.currentgamemode)
        self.currentgamemode = None

    def register_game_mode(self, gamemodename, priority=sys.maxsize/2, default=False):
        # Priority: Higher numbers are lower on the list
        # Default: True if it should be the starting game mode when the game starts
        if not self.menu:
            self.modsloaded(("pysweep", "AllModsLoaded"), None)

        i = 0
        while i < len(self.gamemodes) and (priority, gamemodename) > self.gamemodes[i]:
            i += 1
        self.gamemodes.insert(i, (priority, gamemodename))
        self.menu.insert_radiobutton(i, label=gamemodename, variable=self.menuvar, command=lambda gamemodename=gamemodename: self.set_game_mode(gamemodename))

        if default:
            if not self.default or self.default > (priority, gamemodename):
                self.default = (priority, gamemodename)

    def set_default(self):
        if self.default:
            self.menu.invoke(self.gamemodes.index(self.default))

    def set_game_mode(self, gamemodename):
        if (self.currentgamemode != gamemodename):
            if (self.currentgamemode != None):
                self.pysweep.handle_event(("gamemode", "DisableGameMode"), self.currentgamemode)
            self.currentgamemode = gamemodename
            self.pysweep.handle_event(("gamemode", "EnableGameMode"), gamemodename)

    def is_enabled(self, gamemodename):
        return self.currentgamemode == gamemodename

mods = {"GameModeSelector": GameModeSelector}

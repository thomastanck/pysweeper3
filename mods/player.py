from PIL import Image, ImageTk

import tkinter
import tkinter.filedialog

import sys

import json

from pysweep.util import gamemode
from pysweep import Timer
import pysweep
from pysweep.gamedisplay import image_dir

game_mode_name = "Video Player"

class Player:
    hooks = {}
    required_events = []
    required_protocols = []

    def __init__(self, master, pysweep):
        self.master = master
        self.pysweep = pysweep
        self.hooks = {
            ("pysweep", "AllModsLoaded"): [self.mods_loaded],
            ("gamemode", "EnableGameMode"): [self.on_enable],
            ("gamemode", "DisableGameMode"): [self.on_disable],
        }

        self.gamedisplay = self.pysweep.gamedisplay


        self.display_events = {
            "TILENUMBER" ,
            "TILEOTHER"  ,
            "COUNTER"    ,
            "FACE"       ,
            "TIMER"      ,
        }
        self.events = {
            "TILENUMBER" : self.num,
            "TILEOTHER"  : self.oth,
            "COUNTER"    : self.coun,
            "FACE"       : self.fac,
            "TIMER"      : self.tim,
            "MOVE"       : self.mov,
        }

        self.timer = Timer(self.master, self.tick, period=0.001, resolution=0.001)
        self.vid = None
        self.vid_start = 0
        self.vid_pos = 0

        self.boardx = 0
        self.boardy = 0
        self.boardwidth = 0
        self.boardheight = 0

        print("{}/cursor.png".format(image_dir))
        self.cursorimg = Image.open("{}/cursor.png".format(image_dir))
        self.cursortk = ImageTk.PhotoImage(self.cursorimg)
        self.cursoritem = self.gamedisplay.board.canvas.create_image((0, 0), anchor="nw", image=self.cursortk)
        self.gamedisplay.board.canvas.itemconfig(self.cursoritem, state="hidden")
        # self.cursorcanvas = tkinter.Canvas(self.gamedisplay.board, width=newsize[0], height=newsize[1])

    def mods_loaded(self, hn, e):
        self.gamemodeselector = self.pysweep.mods["GameModeSelector"]
        self.vidmod = self.pysweep.mods["VideoFile"]
        self.gamemodeselector.register_game_mode(game_mode_name)

    def num(self, n, r, c):
        self.gamedisplay.set_tile_number(r, c, n)

    def oth(self, t, r, c):
        self.gamedisplay.set_tile_other(r, c, t)

    def coun(self, n):
        self.gamedisplay.set_mine_counter(n)

    def fac(self, t):
        self.gamedisplay.set_face(t)

    def tim(self, n):
        self.gamedisplay.set_timer(n)

    def mov(self, x, y):
        x -= self.boardx
        y -= self.boardy
        if self.boardwidth != 0:
            x *= self.gamedisplay.board.winfo_width() / self.boardwidth
        if self.boardheight != 0:
            y *= self.gamedisplay.board.winfo_height() / self.boardheight
        self.gamedisplay.board.canvas.coords(self.cursoritem, x, y)

    def meta(self, widget, x, y, width, height):
        if widget == "BOARD":
            self.boardx = x
            self.boardy = y
            self.boardwidth = width
            self.boardheight = height

    def tick(self, elapsed, sincelasttick):
        if self.vid:
            if self.vid_start == 0:
                # find vid_start time
                for event in self.vid.vid:
                     if event[0] in self.display_events:
                         self.vid_start = event[1]
                         self.vid_pos = self.vid_start
                         break
            end = self.vid_start + elapsed
            start = self.vid_pos
            for event in self.vid.vid:
                if event[0] == "DISPLAYMETA" and event[1] == "BOARD":
                    args = event[1:]
                    self.meta(*args)
                if event[0] in self.events.keys() and start <= event[1] < end:
                    args = event[2:]
                    print(event)
                    self.events[event[0]](*args)
            self.vid_pos = end

    @gamemode(game_mode_name)
    def on_enable(self, hn, e):
        print("enabled!")
        self.window = tkinter.Toplevel(self.master)
        self.rewindbutton = tkinter.Button(self.window, text="Bekku", command=self.rewind)
        self.playbutton = tkinter.Button(self.window, text="Purei", command=self.play)
        self.forwardbutton = tkinter.Button(self.window, text="Foowaado", command=self.forward)
        self.loadbutton = tkinter.Button(self.window, text="Roodo", command=self.load)
        # step forward backward, other images and stuff, etc
        # You'll probably want Frames and Canvases in here.
        self.rewindbutton.pack()
        self.playbutton.pack()
        self.forwardbutton.pack()
        self.loadbutton.pack()
        self.gamedisplay.board.canvas.itemconfig(self.cursoritem, state="normal")

    @gamemode(game_mode_name)
    def on_disable(self, hn, e):
        print("disabled!")
        self.rewind()
        self.window.destroy()
        del self.window
        self.gamedisplay.board.canvas.itemconfig(self.cursoritem, state="hidden")

    def rewind(self):
        print("rewind pressed")
        self.timer.stop_timer()
        self.timer = Timer(self.master, self.tick, period=0.001, resolution=0.001)
        self.vid_start = 0
        self.vid_pos = 0
        self.gamedisplay.reset_board()
        self.gamedisplay.set_face_happy()
        self.gamedisplay.set_timer(0)
        self.gamedisplay.set_mine_counter(0)
        self.boardx = 0
        self.boardy = 0
        self.boardwidth = 0
        self.boardheight = 0

    def play(self):
        print("play pressed")
        self.timer.stop_timer()
        self.timer = Timer(self.master, self.tick, period=0.001, resolution=0.001)
        self.vid_start = 0
        self.vid_pos = 0
        self.gamedisplay.reset_board()
        self.gamedisplay.set_face_happy()
        self.gamedisplay.set_timer(0)
        self.gamedisplay.set_mine_counter(0)
        self.timer.start_timer()
    def forward(self):
        print("forward pressed")
        self.timer.stop_timer()
        self.timer = Timer(self.master, self.tick, period=0.001, resolution=0.001)
        self.tick(sys.maxsize,sys.maxsize)
    def load(self):
        print("load pressed")
        filename = tkinter.filedialog.askopenfilename()
        print("filename: {}".format(filename))
        f = open(filename, 'rb')
        contents = f.read()
        self.rewind()
        self.vid = self.vidmod.new_video_file(self.pysweep.gamedisplay, "","")
        try:
            self.vid.vidbytes = contents
        except:
            try:
                self.vid.vidstr = contents.decode('utf-8')
            except:
                raise ValueError('Failed to read video file')


mods = {"Player": Player}

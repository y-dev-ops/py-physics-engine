import tkinter as tk
from models.shape import *
import time


class Screen:
    def __init__(self, title="My App", width=400, height=300, fps=60):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.shapes = []  # keep track of shapes
        self.fps = fps
        self.dt = 1/fps
        self.last_time = time.time()
        self.accumulator = 0

        self.update_callbacks = []
        self.fixed_update_callbacks = []

    def add_circle(self, x, y, radius, color="red", mass=1000, isStatic=True):
        circle = Circle(x, y, radius, color, mass=mass, myscreen=self, isStatic=isStatic)
        circle.canvas_id = self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius, fill=color
        )
        self.shapes.append(circle)
        return circle

    def add_rectangle(self, x, y, width, height, color="blue", mass=1000, isStatic=True):
        rect = Rectangle(x, y, width, height, color, mass=mass, myscreen=self, isStatic=isStatic)
        rect.canvas_id = self.canvas.create_rectangle(
            x, y, x + width, y + height, fill=color
        )
        self.shapes.append(rect)
        return rect

    def add_button(self, text, command):
        button = tk.Button(self.root, text=text, command=command, background='red', width=2, height=2)
        button.place(relx=1.0, rely=0.0, anchor='ne')
        return button


    def show(self):
        self._run_loop()   # start the custom loop
        self.root.mainloop()


    def register_update(self, func):
        self.update_callbacks.append(func)

    def register_fixed_update(self, func):
        self.fixed_update_callbacks.append(func)

    
    def _run_loop(self):
        now = time.time()
        delta = now - self.last_time
        self.last_time = now

        # Call Update callbacks (variable delta)
        for func in self.update_callbacks:
            func(delta)

        # Call Fixed_Update callbacks (fixed delta)
        for func in self.fixed_update_callbacks:
            self.accumulator += delta
            while self.accumulator >= self.dt:
                func(self.dt)
                self.accumulator -= self.dt



        # Schedule next frame
        self.root.after(int(1000 / self.fps), self._run_loop)

from models.rigidbody import *

class Shape:
    """Base class for all shapes"""
    def __init__(self, x, y, color="black", myscreen=None, isStatic=True):
        self.x = x
        self.y = y
        self.color = color
        self.screen = myscreen
        self.scripts = []
        self.scripts_update = []
        self.scripts_fixed_update = []
        self.type = "shape"


    def add_script(self, script):
        if (script.hasUpdate):
            self.scripts_update.append(script)
        if (script.hasFUpdate):
            self.scripts_fixed_update.append(script)

        self.scripts.append(script)
        
    def Update(self, delta):
        for script in self.scripts_update:
                script.update(delta)

    def FUpdate(self, delta):
        for script in self.scripts_fixed_update:
                script.fixed_update(delta)


    def remove_script(script):
        self.scripts.remove(script)



    def position(self, x, y):
        self.x = x
        self.y = y

    def get_aabb(self):
        if hasattr(self, "radius"):  # circle
            return (
                self.x - self.radius,
                self.y - self.radius,
                self.x + self.radius,
                self.y + self.radius
            )
        else:  # rectangle
            return (
                self.x,
                self.y,
                self.x + self.width,
                self.y + self.height
            )

    
# you can add your own shapes here
class Circle(Shape):
    def __init__(self, x, y, radius, color="red", mass = 0, myscreen=None, isStatic=True):
        super().__init__(x, y, color)
        self.radius = radius
        self.rb = rigidbody(mass=mass, isStatic=isStatic)  # custom properties dictionary
        self.canvas_id = None  # ID of the drawn object on the canvas
        self.screen = myscreen
        self.type = "circle"
    
    def position(self, x, y):
        self.x = x
        self.y = y
        self.screen.canvas.coords(
            self.canvas_id,
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )

class Rectangle(Shape):
    def __init__(self, x, y, width, height, color="blue", mass = 0, myscreen=None, isStatic=True):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
        self.rb = rigidbody(mass=mass, isStatic=isStatic)
        self.canvas_id = None
        self.screen = myscreen
        self.type = "rectangle"

    def position(self, x, y):
        self.x = x
        self.y = y
        self.screen.canvas.coords(
            self.canvas_id,
            self.x,
            self.y,
            self.x + self.width,
            self.y + self.height
        )
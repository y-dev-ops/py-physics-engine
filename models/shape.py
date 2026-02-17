from models.rigidbody import *
import math
class Shape:
    """Base class for all shapes"""
    def __init__(self, x, y, color="black", myscreen=None, isStatic=True, gravity=True, bounciness=0.6, friction=0.4, static_friction=0.6):
        self.x = x
        self.y = y
        self.color = color
        self.screen = myscreen
        self.scripts = []
        self.scripts_update = []
        self.scripts_fixed_update = []
        self.type = "shape"
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        self.rb = rigidbody(isStatic=isStatic)
        self.rb.position = [x, y]


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

    def rotate_points(points, angle_deg, pivot):
        cx, cy = pivot
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        out = []
        for i in range(0, len(points), 2):
            x, y = points[i] - cx, points[i+1] - cy
            xr, yr = x*c - y*s + cx, x*s + y*c + cy
            out.extend([xr, yr])
        return out

    def rotation(self, z):
        self.rotation_z = z
        points = [self.x,
                self.y,
                self.x + self.width,
                self.y + self.height]
        pivot = [(self.x + self.width)/2, (self.y + self.height)/2]


        
        angle_deg = self.rotation_z
        cx, cy = pivot
        a = math.radians(angle_deg)
        c, s = math.cos(a), math.sin(a)
        out = []
        for i in range(0, len(points), 2):
            x, y = points[i] - cx, points[i+1] - cy
            xr, yr = x*c - y*s + cx, x*s + y*c + cy
            out.extend([xr, yr])
        return out




    # usage: canvas.coords(poly_id, *rotate_points(orig_points, angle, (cx, cy)))

    def get_aabb(self):
        if hasattr(self, "radius"):  # circle
            return (
                self.x - self.radius,
                self.y - self.radius,
                self.x + self.radius,
                self.y + self.radius
            )
        else:  # rectangle or square
            return (
                self.x,
                self.y,
                self.x + self.width,
                self.y + self.height
            )

    
# you can add your own shapes here
class Circle(Shape):
    def __init__(self, x, y, radius, color="red", mass = 0, myscreen=None, isStatic=True, gravity=True, bounciness=0.6, friction=0.4, static_friction=0.6):
        super().__init__(x, y, color) #x,y of circle is center
        self.radius = radius
        self.rb = rigidbody(mass=mass, isStatic=isStatic, gravity=gravity, bounciness=bounciness, friction=friction, static_friction=static_friction)  # custom properties dictionary
        self.canvas_id = None  # ID of the drawn object on the canvas
        self.screen = myscreen
        self.type = "circle"
        self.width = radius * 2 #to avoid any possible errors
        self.height = radius * 2 #to avoid any possible errors
        self.angle = 0
        self.base_points = [
            self.x - self.radius, self.y,
            self.y - self.radius, self.x,
            self.x + self.radius, self.y,
            self.y + self.radius, self.x
        ]
        self.points = self.base_points.copy()

    def rotation(self, angle_deg):
        self.angle = angle_deg

        cx, cy = self.x, self.y
        a = math.radians(self.angle)
        c, s = math.cos(a), math.sin(a)

        out = []

        for i in range(0, len(self.base_points), 2):
            x = self.base_points[i] - cx
            y = self.base_points[i+1] - cy

            xr = x * c - y * s + cx
            yr = x * s + y * c + cy

            out.extend([xr, yr])

        self.points = out
        self.screen.canvas.coords(self.canvas_id, *self.points[0::2])
    
    def position(self, x, y):
        self.x = x
        self.y = y
        self.base_points = [
            self.x - self.radius, self.y,
            self.y - self.radius, self.x,
            self.x + self.radius, self.y,
            self.y + self.radius, self.x
        ]

        self.rotation(self.angle)





class Rectangle(Shape):
    def __init__(self, x, y, width, height, color="blue", mass = 0, myscreen=None, isStatic=True, gravity=True, bounciness=0.6, friction=0.4, static_friction=0.6):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
        self.rb = rigidbody(mass=mass, isStatic=isStatic, gravity=gravity, bounciness=bounciness, friction=friction, static_friction=static_friction)
        self.canvas_id = None
        self.screen = myscreen
        self.type = "rectangle"
        #self.rb.position = [x, y]  # center
        self.angle = 0
        hw, hh = width / 2, height / 2
        #self.center_x = x + hw
        #self.center_y = y + hh
        self.x = x + hw
        self.y = y + hh
        self.base_points = [
            self.x - hw, self.y - hh,
            self.x + hw, self.y - hh,
            self.x + hw, self.y + hh,
            self.x - hw, self.y + hh
        ]

        self.points = self.base_points.copy()

    def get_aabb(self):
        xs = self.points[0::2]
        ys = self.points[1::2]
        return min(xs), min(ys), max(xs), max(ys)

    def rotation(self, angle_deg):
        self.angle = angle_deg

        cx, cy = self.x, self.y
        a = math.radians(self.angle)
        c, s = math.cos(a), math.sin(a)

        out = []

        for i in range(0, len(self.base_points), 2):
            x = self.base_points[i] - cx
            y = self.base_points[i+1] - cy

            xr = x * c - y * s + cx
            yr = x * s + y * c + cy

            out.extend([xr, yr])

        self.points = out
        self.screen.canvas.coords(self.canvas_id, *self.points)

    def position(self, cx, cy):
        self.x = cx
        self.y = cy

        hw = self.width / 2
        hh = self.height / 2

        self.base_points = [
            self.x - hw, self.y - hh,
            self.x + hw, self.y - hh,
            self.x + hw, self.y + hh,
            self.x - hw, self.y + hh
        ]

        self.rotation(self.angle)


    










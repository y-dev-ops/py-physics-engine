from models.rigidbody import *
import math


class Shape:
    #main dict shape, this is what you can feed the Shape with:
    def_dict = {
        'x': 0,
        'y': 0,
        'width': 0,
        'height': 0,
        'angle': 0,
        'color': 'pink',
        'rb': {
            'gravity': True,
            'isStatic': False,
            'ingore_static': False,
            'bounciness': 0.6,
            'friction': 0.4,
            'static_friction': 0.6,
            'mass': 1000,
        },
        'scripts': [],
        'scripts_update': [],
        'scripts_fixed_update': [],
        'canvas_id': None,
    }
    def unpack(self, _dict):
        for key, value in _dict.items():
            if (key == 'rb'):
                self.rb = rigidbody(**value)
            else:
                setattr(self, key, value)


    def __init__(self, _dict):
        #print(_dict)
        data = self.def_dict.copy()  # make a copy of default dict
        data.update(_dict) 
        #print(data)
        self.unpack(data)


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

        return out


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
        return (
                self.x,
                self.y,
                self.x + self.width,
                self.y + self.height
                )

    
# you can add your own shapes here
class Circle(Shape):
    def __init__(self, _dict):
        super().__init__(_dict)
        self.type = "circle"
        self.base_points = [
            self.x - self.radius, self.y,
            self.y - self.radius, self.x,
            self.x + self.radius, self.y,
            self.y + self.radius, self.x
        ]
        self.points = self.base_points.copy()

    def get_aabb(self):
        return(
                self.x - self.radius,
                self.y - self.radius,
                self.x + self.radius,
                self.y + self.radius
        )

    def position(self, x, y):
        self.x = x
        self.y = y
        self.base_points = [
            self.x - self.radius, self.y,
            self.y - self.radius, self.x,
            self.x + self.radius, self.y,
            self.y + self.radius, self.x
        ]
        self.points = self.rotation(self.angle)
        self.screen.canvas.coords(self.canvas_id, *self.points[0::2])

class Rectangle(Shape):
    def __init__(self, _dict):
        super().__init__(_dict)
        self.type = "rectangle"
        hw, hh = self.width / 2, self.height / 2
        self.x += hw
        self.y += hh
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

        
        self.points = self.rotation(self.angle)
        self.screen.canvas.coords(self.canvas_id, *self.points)


    










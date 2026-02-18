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
        'type': '',
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

        if (len(self.scripts) > 0):
            for script in self.scripts:
                script.parent(self)
                if (script.hasUpdate):
                    self.scripts_update.append(script)
                if (script.hasFUpdate):
                    self.scripts_fixed_update.append(script)

    def calculate_inertia(self, shape):
        if shape.rb.isStatic:
            shape.rb.inertia = 0
            shape.rb.inv_inertia = 0
            return

        m = shape.rb.mass
        
        # Formula for Box Inertia: (1/12) * m * (w^2 + h^2)
        if shape.type == "rectangle":
            shape.rb.inertia = (1.0 / 12.0) * m * (shape.width**2 + shape.height**2)
        
        # Formula for Circle Inertia: (1/2) * m * r^2
        elif shape.type == "circle":
            shape.rb.inertia = 0.5 * m * (shape.radius**2)

        # Cache the inverse for faster math later
        print('passed iner for :', shape.type, shape, shape.rb.mass, shape.rb.inertia)
        shape.rb.inv_inertia = 1.0 / shape.rb.inertia if shape.rb.inertia > 0 else 0
    

    def __init__(self, _dict):
        #print(_dict)
        data = self.def_dict.copy()  # make a copy of default dict
        data.update(_dict) 
        #print(data)
        self.unpack(data)
        self.calculate_inertia(self)


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

    def update_world_points(self):
        # Base shapes might not need this, but polygons do.
        # This prevents crashes if called on a shape without a custom implementation (like Circle).
        pass

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
        _dict['type'] = 'circle'
        super().__init__(_dict)
        # Circles don't need points for drawing with create_oval, but the attribute should exist.
        self.points = []

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
        # For a circle, position update is just moving the oval's bounding box.
        if self.canvas_id is not None:
            self.screen.canvas.coords(self.canvas_id, self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius)
        

class Rectangle(Shape):
    def __init__(self, _dict):
        _dict['type'] = 'rectangle'
        super().__init__(_dict)

        hw, hh = self.width / 2.0, self.height / 2.0

        # local_points are fixed in local (centered) coordinates
        self.local_points = [
            -hw, -hh,
             hw, -hh,
             hw,  hh,
            -hw,  hh
        ]

        # world points will be computed each frame
        self.points = [0.0]*8
        # ensure x,y are centers; your constructor previously did x += hw etc.
        # assume self.x,self.y already are center from unpack
        self.angle = getattr(self, "angle", 0.0)  # degrees
        self.update_world_points()

    def update_world_points(self):
        cx, cy = self.x, self.y
        a = math.radians(self.angle)  # keep angular arithmetic in radians internally
        c, s = math.cos(a), math.sin(a)

        out = []
        lp = self.local_points
        for i in range(0, len(lp), 2):
            lx, ly = lp[i], lp[i+1]
            rx = lx * c - ly * s
            ry = lx * s + ly * c
            out.append(rx + cx)
            out.append(ry + cy)

        self.points = out
        if self.canvas_id is not None:
            self.screen.canvas.coords(self.canvas_id, *self.points)

    def position(self, cx, cy):
        # move center only, do NOT rebuild local_points
        self.x = cx
        self.y = cy
        self.update_world_points()

    def rotate_to(self, angle_deg):
        # set absolute angle in degrees
        self.angle = angle_deg
        self.update_world_points()

    def rotate_by(self, d_angle_deg):
        self.angle += d_angle_deg
        self.update_world_points()

    def get_aabb(self):
        xs = self.points[0::2]
        ys = self.points[1::2]
        return min(xs), min(ys), max(xs), max(ys)

from models.rigidbody import *
import math
import pygame


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
            'bounciness': 0.2,
            'friction': 0.4,
            'static_friction': 0.6,
            'mass': 1000,
        },
        'type': '',
        'outline': {},
        'scripts': [],
        'scripts_update': [],
        'scripts_fixed_update': [],
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

    def calculate_inertia_poly(self, local_points, mass):
        # 1. Convert flat list [x1, y1, x2, y2...] to [(x1, y1), (x2, y2)...]
        vertices = []
        for i in range(0, len(local_points), 2):
            vertices.append((local_points[i], local_points[i+1]))

        num = 0.0
        den = 0.0

        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]

            # Signed area of the triangle formed by the origin and the edge
            cross_product = x1 * y2 - x2 * y1
            
            # Second moment of area contribution
            sum_squares = (x1**2 + x1*x2 + x2**2 + y1**2 + y1*y2 + y2**2)
            
            num += cross_product * sum_squares
            den += cross_product

        # Final Moment of Inertia
        return (mass / 6.0) * (num / den)

    def calculate_inertia(self, shape):
        if shape.rb.isStatic:
            shape.rb.inertia = 0
            shape.rb.inv_inertia = 0
            return

        m = shape.rb.mass
        
        # Formula for Box Inertia: (1/12) * m * (w^2 + h^2)
        if shape.type != "circle":
            shape.rb.inertia = self.calculate_inertia_poly(shape.local_points, m)
        
        # Formula for Circle Inertia: (1/2) * m * r^2
        elif shape.type == "circle":
            shape.rb.inertia = 0.5 * m * (shape.radius**2)

        # Cache the inverse for faster math later
        #print('passed iner for :', shape.type, shape, shape.rb.mass, shape.rb.inertia)
        shape.rb.inv_inertia = 1.0 / shape.rb.inertia if shape.rb.inertia > 0 else 0
    
    def getcomponent(self, component):
        for script in self.scripts:
            if type(script).__name__ == component:
                return script
        print('component not found, check your spelling')
        return None

    def __init__(self, _dict):
        #print(_dict)
        data = self.def_dict.copy()  # make a copy of default dict
        data.update(_dict) 
        #print(data)
        self.unpack(data)

    def destroy(self):
        
        # 2. Tell the screen/manager to forget about us
        # This removes it from the list the physics engine uses
        if self in self.screen.shapes:
            self.screen.shapes.remove(self)
        if (len(self.scripts) > 0):
            for script in self.scripts:
                self.remove_script(script, insideLoop=True)

        self.scripts.clear()
        
        # 3. Optional: Mark as dead for other scripts to check
        self.is_destroyed = True

    def rotation(self, angle_deg):
        self.angle = angle_deg

        cx, cy = self.x, self.y
        out = []
        for i in range(0, len(self.base_points), 2):
            vec = pygame.math.Vector2(self.base_points[i] - cx, self.base_points[i+1] - cy).rotate(self.angle)
            out.append(vec.x + cx)
            out.append(vec.y + cy)

        return out


    def rotate_to(self, angle_deg):
        # set absolute angle in degrees
        self.angle = angle_deg
        self.update_world_points()

    def rotate_by(self, d_angle_deg):
        self.angle += d_angle_deg
        self.update_world_points()

    def add_script(self, script):
        if (script.hasUpdate):
            self.scripts_update.append(script)
        if (script.hasFUpdate):
            self.scripts_fixed_update.append(script)

        self.scripts.append(script)
        
    def remove_script(self, script, insideLoop = False):
        if (script.hasUpdate):
            self.scripts_update.remove(script)
        if (script.hasFUpdate):
            self.scripts_fixed_update.remove(script)
        if (not insideLoop):
            self.scripts.remove(script)

        script.destroyed()

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
        self.points = []
        #always after point
        self.calculate_inertia(self)

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
        

class Rectangle(Shape):
    def __init__(self, _dict):
        _dict['type'] = 'rectangle'
        super().__init__(_dict)
        hw, hh = self.width / 2.0, self.height / 2.0
        self.local_points = [
            -hw, -hh,
             hw, -hh,
             hw,  hh,
            -hw,  hh
        ]
        self.points = [0.0]*8
        #always after point
        self.calculate_inertia(self)


        self.angle = getattr(self, "angle", 0.0)  # degrees
        self.update_world_points()

    def update_world_points(self):
        cx, cy = self.x, self.y

        out = []
        lp = self.local_points
        for i in range(0, len(lp), 2):
            vec = pygame.math.Vector2(lp[i], lp[i+1]).rotate(self.angle)
            out.append(vec.x + cx)
            out.append(vec.y + cy)

        self.points = out

    def position(self, cx, cy):
        # move center only, do NOT rebuild local_points
        self.x = cx
        self.y = cy
        self.update_world_points()

    def get_aabb(self):
        xs = self.points[0::2]
        ys = self.points[1::2]
        return min(xs), min(ys), max(xs), max(ys)



class Triangle(Shape):
    def __init__(self, _dict):
        _dict['type'] = 'triangle'
        super().__init__(_dict)

        b = self.width
        h = self.height
        
        self.local_points = [
             0,      -2 * h / 3.0,
            -b / 2.0, h / 3.0,
             b / 2.0, h / 3.0
        ]

        self.points = [0.0] * 6

        #always after point
        self.calculate_inertia(self)

        self.angle = getattr(self, "angle", 0.0)
        self.update_world_points()

    def update_world_points(self):
        cx, cy = self.x, self.y

        out = []
        lp = self.local_points
        for i in range(0, len(lp), 2):
            vec = pygame.math.Vector2(lp[i], lp[i+1]).rotate(self.angle)
            out.append(vec.x + cx)
            out.append(vec.y + cy)

        self.points = out

    def position(self, cx, cy):
        self.x = cx
        self.y = cy
        self.update_world_points()

    def get_aabb(self):
        xs = self.points[0::2]
        ys = self.points[1::2]
        return min(xs), min(ys), max(xs), max(ys)

class Pentagon(Shape):
    def __init__(self, _dict):
        _dict['type'] = 'pentagon'
        super().__init__(_dict)


        w = self.width
        h = self.height
        self.local_points = [
             0,          -h / 2.0,       # Top vertex
             w / 2.0,    -h * 0.1545,    # Upper right
             w * 0.309,   h / 2.0,       # Lower right
            -w * 0.309,   h / 2.0,       # Lower left
            -w / 2.0,    -h * 0.1545     # Upper left
        ]
        self.points = [0.0] * 10
        #always after point
        self.calculate_inertia(self)


        self.angle = getattr(self, "angle", 0.0)
        self.update_world_points()

    def update_world_points(self):
        cx, cy = self.x, self.y

        out = []
        lp = self.local_points
        for i in range(0, len(lp), 2):
            vec = pygame.math.Vector2(lp[i], lp[i+1]).rotate(self.angle)
            out.append(vec.x + cx)
            out.append(vec.y + cy)

        self.points = out

    def position(self, cx, cy):
        self.x = cx
        self.y = cy
        self.update_world_points()

    def get_aabb(self):
        xs = self.points[0::2]
        ys = self.points[1::2]
        return min(xs), min(ys), max(xs), max(ys)
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
        'color': None,
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
        'texture_data': None,
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

    def load_texture(self, tex_data):
        print('loaded texture ', tex_data, 'color:', self.color)
        if (tex_data == None):
            return
        try:
            # 1. Load and prepare texture
            raw_img = pygame.image.load(tex_data['texture']).convert_alpha()
            raw_img = pygame.transform.flip(raw_img, tex_data['flip_x'], tex_data['flip_y'])
            
            # Calculate texture scale
            if self.type == 'circle':
                target_w = int(self.radius * 2 * tex_data['size'][0])
                target_h = int(self.radius * 2 * tex_data['size'][1])
            else:
                target_w = int(self.width * tex_data['size'][0])
                target_h = int(self.height * tex_data['size'][1])
            scaled_tex = pygame.transform.scale(raw_img, (target_w, target_h))

            # 2. Calculate Surface Size to ensure (0,0) is exactly in the center
            # This prevents the texture from drifting away from the collider
            if self.type == 'circle':
                max_dist_x = self.radius
                max_dist_y = self.radius
            else:
                xs = self.local_points[0::2]
                ys = self.local_points[1::2]
                max_dist_x = max(abs(x) for x in xs)
                max_dist_y = max(abs(y) for y in ys)

            # Make surface double the max extent so (0,0) is center
            surf_w = int(max_dist_x * 2) + 4 # +4 for padding
            surf_h = int(max_dist_y * 2) + 4
            center_x, center_y = surf_w // 2, surf_h // 2

            # 3. Create a blank transparent surface and draw mask
            shape_surface = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
            
            if self.type == 'circle':
                pygame.draw.circle(shape_surface, (255, 255, 255, 255), (center_x, center_y), int(self.radius))
            else:
                # Offset local points by center_x, center_y
                local_points = [(x + center_x, y + center_y) for x, y in zip(xs, ys)]
                pygame.draw.polygon(shape_surface, (255, 255, 255, 255), local_points)

            # 5. Create the tiled/panned texture based on position
            panned_texture = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
            ox, oy = tex_data.get('position', [0,0])
            tw, th = scaled_tex.get_size()

            if tw > 0 and th > 0:
                # Effective offset within the texture dimensions (wraps around)
                sx, sy = ox % tw, oy % th

                # Main part (bottom-right of source texture)
                panned_texture.blit(scaled_tex, (0, 0), (sx, sy, tw - sx, th - sy))

                # Right part (from left of source)
                if sx > 0:
                    panned_texture.blit(scaled_tex, (tw - sx, 0), (0, sy, sx, th - sy))

                # Bottom part (from top of source)
                if sy > 0:
                    panned_texture.blit(scaled_tex, (0, th - sy), (sx, 0, tw - sx, sy))

                # Corner part (from top-left of source)
                if sx > 0 and sy > 0:
                    panned_texture.blit(scaled_tex, (tw - sx, th - sy), (0, 0, sx, sy))
            
            # 6. Stamp the panned texture onto the shape mask
            tex_x, tex_y = center_x - (target_w // 2), center_y - (target_h // 2)
            shape_surface.blit(panned_texture, (tex_x, tex_y), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Apply color tint if it's not white
            if tex_data.get('color', 'white') != 'white':
                tint = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
                tint.fill(tex_data['color'])
                shape_surface.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            
            # Save the cleanly cut shape!
            self.orig_image = shape_surface
            
        except Exception as e:
            print(f"Texture load failed: {e}")
            self.orig_image = None

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
        #self.load_texture(_dict['texture_data'])

    def destroy(self):
        
        # 2. Tell the screen/manager to forget about us
        # This removes it from the list the physics engine uses
        if self in self.screen.app.scene_manager.active_scene.shapes:
            self.screen.app.scene_manager.active_scene.shapes.remove(self)
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
        self.load_texture(_dict.get('texture_data'))

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
        self.load_texture(_dict.get('texture_data'))


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
        self.load_texture(_dict.get('texture_data'))

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
        self.load_texture(_dict.get('texture_data'))


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

class Hexagon(Shape):
    def __init__(self, _dict):
        _dict['type'] = 'hexagon'
        super().__init__(_dict)


        R = self.width / 2.0
        h_offset = R * 0.866 # This is (sqrt(3)/2) * R

        self.local_points = [
            R, 0,                # Right point
            R * 0.5, h_offset,   # Top Right
            -R * 0.5, h_offset,  # Top Left
            -R, 0,               # Left point
            -R * 0.5, -h_offset, # Bottom Left
            R * 0.5, -h_offset   # Bottom Right
        ]
        self.points = [0.0] * 12
        #always after point
        self.calculate_inertia(self)
        self.load_texture(_dict.get('texture_data'))


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

class Custom_Poly(Shape):
    def __init__(self, _dict):
        _dict['type'] = 'poly'
        super().__init__(_dict)
        b = self.width
        h = self.height
        #points = [(1, 2), (2, 5)] # [(x1, y1), (x2, y2)...]
        if (_dict['input_points'] == None):
            raw_points = [(0, -2 * h / 3.0), (-b / 2.0, h / 3.0), (b / 2.0, h / 3.0)]
        else:
            raw_points = _dict.get('input_points')
        

        # 1. Flatten the local points and ensure they are relative to (0,0)
        # If your input is [(x,y), (x,y)], we turn it into [x, y, x, y]
        # Calculate half-dimensions for scaling
        hw = self.width / 2.0
        hh = self.height / 2.0

        # 1. Scale the points based on Width and Height
        self.local_points = []
        for px, py in raw_points:
            # Scale the point and add to local_points list
            self.local_points.append(px * hw)
            self.local_points.append(py * hh)


        # 2. Initialize world points
        self.points = [0.0] * len(self.local_points)
        #always after point
        self.calculate_inertia(self)
        self.load_texture(_dict.get('texture_data'))


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
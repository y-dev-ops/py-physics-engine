# scenes/level_01.py
from models.scene import Scene
from basic.screen import *

#scripts: (here you add your scripts from '/scripts' to import them)
from scripts.follow_the_mouse import *
from scripts.drag import *
from scripts.rotate import *

class debug01(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Main Menu / Level 1"


    def elements(self, screen):

        pack_var = screen.app.pack_var
        pack_ui = screen.app.pack_ui
        # --- phy materials ---
        bouncy_material = {
            'bounciness': 0.6,
            'friction': 0.2,
            'static_friction': 0.4,
        }
        spongy_material = {
            'bounciness': 0.2,
            'friction': 0.7,
            'static_friction': 0.8,
        }

        #--- Outline Settings ---
        outline = {
            'color': 'white',
            'stroke': 1, # 0 for no outline
        }

        # --- texture data ---
        texture_data = {
            'texture':'assets/default/UI/test.jpg', # texture file path
            'flip_x':False, # flip on x axis
            'flip_y':False,# flip on y axis
            'color':  'white',# can be override by color from shape
            'size': [1, 1], #x and y stretch or stuff, def [1,1]
            'position': [10,20], #position on texture space, def [0, 0]
        }

        # --- UI ---
        button = screen.add_button(pack_ui(
            position=[50, 50],
            size=[75, 75],
            text='Quit',
            font_size=24,
            command=lambda: setattr(screen, 'running', False),
            hover_color=(200, 200, 200), # Light grey on hover
            scripts=[
                #rotate()
            ],
            texture='assets/default/UI/circle.png'
        ))

        # --- scene objects ---

        # circle object
        circle = screen.add_circle(pack_var(
            position=[150, 100],
            size=[50],
            material=bouncy_material,
            color='red',
            mass=3,
            isStatic=False,
            scripts=[
                drag()
            ],
            outline=outline,
            texture_data=texture_data
        ))

        # --- Set Camera Target ---
        screen.set_camera_target(circle)

        # rect_3 object
        rect_3 = screen.add_rectangle(pack_var(
            position=[600, 100],
            size=[200, 150],
            material=spongy_material,
            mass=10,
            isStatic=False,
            scripts=[
                drag()
            ],
            outline=outline,
            texture_data=texture_data
        ))

        # tri object
        tri = screen.add_triangle(pack_var(
            position=[400, 100],
            size=[150, 150],
            material=spongy_material,
            color='blue',
            mass=10,
            isStatic=False,
            scripts=[
                drag(),
                rotate()
            ],
            outline=outline,
            texture_data=texture_data
        ))
        pen = screen.add_pentagon(pack_var(
            position=[400, 100],
            size=[150, 150],
            material=bouncy_material,
            color='yellow',
            mass=20,
            isStatic=False,
            scripts=[
                drag()
            ],
            outline=outline,
            texture_data=texture_data
        ))

        hx = screen.add_hexagon(pack_var(
            position=[400, 400],
            size=[150, 150],
            material=bouncy_material,
            color='green',
            mass=3,
            isStatic=False,
            scripts=[
                drag()
            ],
            outline=outline,
        ))

        poly = screen.add_custom_poly(pack_var(
            position=[400, 400],
            size=[150, 150],
            material=bouncy_material,
            color='green',
            mass=3,
            isStatic=False,
            scripts=[
                drag()
            ],
            outline=outline,
            texture_data=texture_data,
            points=[
                # --- The Trunk (Bottom) ---
                (-0.2, 1.0), (-0.2, 0.6),   # Bottom left of trunk to base of leaves
                # --- Left Side Canopy (Jagged) ---
                (-0.5, 0.6), (-0.3, 0.5), (-0.6, 0.4), (-0.4, 0.3),
                (-0.7, 0.2), (-0.5, 0.1), (-0.8, 0.0), (-0.6, -0.1),
                (-0.9, -0.2), (-0.7, -0.3), (-0.8, -0.5), (-0.5, -0.6),
                (-0.3, -0.8), (-0.1, -0.9),
                
                # --- The Top Peak ---
                (0.0, -1.0), 
                
                # --- Right Side Canopy (Jagged) ---
                (0.1, -0.9), (0.3, -0.8), (0.5, -0.6), (0.8, -0.5),
                (0.7, -0.3), (0.9, -0.2), (0.6, -0.1), (0.8, 0.0),
                (0.5, 0.1), (0.7, 0.2), (0.4, 0.3), (0.6, 0.4),
                (0.3, 0.5), (0.5, 0.6),
                
                # --- Back to Trunk ---
                (0.2, 0.6), (0.2, 1.0),
                
                # --- Bottom of Trunk (Closing the shape) ---
                (0.0, 1.0)
            ]
        ))

        # rect_5 object
        rect_5 = screen.add_rectangle(pack_var(
            position=[900, 50],
            size=[50, 50],
            material=bouncy_material,
            mass=3,
            isStatic=False,
            scripts=[
                drag()
            ],
            outline=outline
        ))
        
        # rect_4 object
        rect_4 = screen.add_rectangle(pack_var(
            position=[600, 600],
            size=[700, 50],
            color='green',
            outline=outline
        ))

        # rect object
        rect = screen.add_rectangle(pack_var(
            position=[50, 500],
            size=[120, 80],
            color='white',
            ingore_static=True,
            isStatic=False,
            gravity=False,
            scripts=[
                drag()
            ],
            outline=outline
        ))
        #rect.add_script(follow_the_mouse(rect))

        # rect_2 object
        rect_2 = screen.add_rectangle(pack_var(
            position=[0, 700],
            size=[3000, 80],
            color='pink',
            outline={
                'color': 'blue',
                'stroke': 5,
            }
        ))

        #for i in range(20): #20 kills it # fixed
        i=1
        rect_7 = screen.add_rectangle(pack_var(
            position=[10 *(i +100), 300],
            size=[50, 50],
            color='pink',
            outline={
                'color': 'blue',
                'stroke': 5,
            },
            isStatic=False
            ))
        

        # Note: isStatic is True by def
    def on_load(self):
        # This triggers exactly once when the scene loads
        print("Level 1 has loaded! Spawning objects...")
        
        # Add a floor
        self.elements(self.screen)
        self.screen.camera.set_offset([0,0])
        #self.shapes.append(floor)

        # Add your giant 40-point tree here!
        # tree = Custom_Poly({...})
        # self.shapes.append(tree)

    def update(self, delta):
        super().update(delta)
        # Custom logic for this scene:
        # e.g., If player falls off map -> self.screen.scene_manager.load_scene(0)
# scenes/level_01.py
from models.scene import Scene
from basic.screen import *

class Level01(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.name = "Main Menu / Level 1"



    def elements(self, screen):

        pack_var = screen.app.pack_var

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

        # --- scene objects ---
        # circle object
        circle = screen.add_circle(pack_var(
            position=[150, 100],
            size=[100],
            color='red',
            mass=3,
            isStatic=False,
            outline=outline,
            texture_data=texture_data
        ))

        rect_2 = screen.add_rectangle(pack_var(
            position=[0, 700],
            size=[3000, 80],
            color='pink',
            outline={
                'color': 'blue',
                'stroke': 5,
            }
        ))

    def on_load(self):
        # This triggers exactly once when the scene loads
        print("Level 1 has loaded! Spawning objects...")
        
        # Add a floor
        self.elements(self.screen)
        #self.shapes.append(floor)

        # Add your giant 40-point tree here!
        # tree = Custom_Poly({...})
        # self.shapes.append(tree)

    def update(self, delta):
        super().update(delta)
        # Custom logic for this scene:
        # e.g., If player falls off map -> self.screen.scene_manager.load_scene(0)
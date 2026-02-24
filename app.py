from basic.screen import *
from caculations.kinematics import *
import pygame
from basic.scene_manager import SceneManager

# Import your scenes
from scenes.debug_level import debug01
from scenes.level_0 import Level01

#scripts: (here you add your scripts from '/scripts' to import them)
from scripts.follow_the_mouse import *
from scripts.drag import *
from scripts.rotate import *

class App():

    def pack_var(self, position = [0,0], size=[50, 50], color=None, angle=0, material={}, mass=1, ingore_static = False, gravity=True, isStatic=True, scripts=[], outline={}, texture_data=None, points=None): #here we turn your vars into dict for easy transfer between objects
        def_material = {
            'bounciness': 0.2,
            'friction': 0.4,
            'static_friction': 0.6,
        }
        def_outline = {
            'color': 'black',
            'stroke': 1, # 0 for no outline
        }
        if (texture_data == None and color == None):
            color = 'red'

        elif (texture_data != None and color != None):
            texture_data['color'] = color

        def_texture_data = {
            'texture':'assets/default/UI/sqaure.png', # texture file path
            'flip_x':False, # flip on x axis
            'flip_y':False,# flip on y axis
            'color':  'white',# gets applied on top of texture #white for normal
            'size': [1, 1], #x and y stretch or stuff, def [1,1]
            'position': [0,0], #position on texture space, def [0, 0]
        }

        def_material.update(material) 
        def_outline.update(outline)
        if (texture_data != None):
            def_texture_data.update(texture_data)
        
        def_dict = {
            'x': position[0],
            'y': position[1],
            'angle': angle, 
            'color': color, # red or else
            'rb': {
                'gravity': gravity,
                'isStatic': isStatic,
                'ingore_static': ingore_static,
                'bounciness': def_material['bounciness'],
                'friction': def_material['friction'],
                'static_friction': def_material['static_friction'],
                'mass': mass,
            },
            'outline': def_outline,
            'scripts': scripts,
            'input_points': points,
        }
        if len(size) > 1:
            def_dict['width'] = size[0]
            def_dict['height'] = size[1]
        else:
            def_dict['radius'] = size[0]

        if (texture_data != None):
            def_dict['texture_data'] = def_texture_data

        return def_dict

    def pack_ui(self, text="simple ui", command=None, position=[0,0], size=[50, 50], scripts=[], angle=0, color='white',texture = "assets/default/UI/sqaure.png", font_size=16, hover_color=None):
        def_UI = {
                'x': position[0],
                'y': position[1],
                'width': size[0],
                'height': size[1],
                'angle': angle,
                'color': color,
                'text': text,
                'command': command,
                'texture': texture,
                'scripts': scripts,
                'font_size': font_size,
                'hover_color': hover_color,
        }

        return def_UI

        pass

    def inspector(screen): # here you add every Shape you need in your screen
        pass

    def __init__(self): # main, handling everthing on this project
        # Initialize Scene Manager
        
        #--- Settings ---
        self.screen_title = "phy engine"
        self.is_fullscreen = True
        self.fps = 60
        self.screen_color = "black"

        # --- Manage Screen ---
        self.screen = Screen(self, self.screen_title, fps=self.fps, screen_color=self.screen_color, is_fullscreen=self.is_fullscreen)
        self.scene_manager = SceneManager(self) # pass 'self' so scenes can access app features

        # Setup Unity-style "Build Settings"
        self.scene_manager.add_to_build(debug01) # Index 0
        self.scene_manager.add_to_build(Level01) # Index 1

        # Load the first scene!
        self.scene_manager.load_scene(0)

        # --- activate inspector ---
        #inspector(screen) #passing current screen to inspector






        
        self.screen.show() #display screen

if __name__ == "__main__":
    App()
    #main() # calling main func to activate everything

#what i have:
#change type to poly for better control
#position, rotation
#kinematics works : gravity, angular v,
#input system
#centered Shapes, rathar than using TOP-LEFT system
# added triangle
# added outline
#added destroy item when right click: check drag()
#added assets folder, the idea is where you store textures or data, will be there
# switch to pygame for better and fast render
# a way to connect scripts with each other like self.shape.getcomponent or script
# add more natural objects lie hex and stuff like that
# add a texture system for objects and background, and its better to have like unity, were you can chnage texture settings or flip it
# add costume poly shape
# add a scenes 
# add a Camera System
# fixed collistion, make small amount to be zero and grounded, so they stop shaking

# TO DO next:
#idk im too fast

# add a way to add static objects that dont need an rb, like tree in background and stuff, a way to add an image to be clear
# add gizmo mode, which is normal shapes but dont interact with anything
# add Ray cast system
# make a basic doc that cover functions you did
# opt code, see u after 5 years ;)

#high end step:
#add a UI for everything as of its an editor fr

#if you finish all of this shit, create a game without changing a single file from the engine script

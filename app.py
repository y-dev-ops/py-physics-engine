from basic.screen import *
from caculations.kinematics import *


#scripts: (here you add your scripts from '/scripts' to import them)
from scripts.follow_the_mouse import *
from scripts.drag import *
from scripts.rotate import *



#--- Settings ---
screen_title = "phy engine"
is_fullscreen = True
fps = 60
screen_color = "black"

def pack_var(position = [0,0], size=[50, 50], color='red', angle=0, material={}, mass=1, ingore_static = False, gravity=True, isStatic=True, scripts=[], outline={}): #here we turn your vars into dict for easy transfer between objects
    def_material = {
        'bounciness': 0.6,
        'friction': 0.4,
        'static_friction': 0.6,
    }
    def_outline = {
        'color': 'black',
        'stroke': 1, # 0 for no outline
    }

    def_material.update(material) 
    def_outline.update(outline)
    
    def_dict = {
        'x': position[0],
        'y': position[1],
        'angle': angle, 
        'color': color,
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
    }
    if len(size) > 1:
        def_dict['width'] = size[0]
        def_dict['height'] = size[1]
    else:
        def_dict['radius'] = size[0]

    return def_dict

def pack_ui(text="simple ui", command=None, position=[0,0], size=[50, 50], scripts=[], angle=0, color='white',texture = "assets/default/UI/sqaure.png", font_size=16, hover_color=None):
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
    
    # --- phy materials ---
    bouncy_material = {
        'bounciness': 0.8,
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
        mass=3,
        isStatic=False,
        scripts=[
            drag()
        ],
        outline=outline
    ))

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
        outline=outline
    ))

    # tri object
    tri = screen.add_triangle(pack_var(
        position=[400, 100],
        size=[150, 150],
        material=spongy_material,
        color='grey',
        mass=10,
        isStatic=False,
        scripts=[
            drag(),
            rotate()
        ],
        outline=outline
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

def main(): # main, handling everthing on this project

    # --- Manage Screen ---
    screen = Screen(screen_title, fps=fps, screen_color=screen_color, is_fullscreen=is_fullscreen)
    
    # --- activate inspector ---
    inspector(screen) #passing current screen to inspector

    # --- main updates ---
    def update(delta):
        pass

    def fixed_update(delta):
        #pass
        physics_engine(delta, screen.shapes)

    screen.register_update(update) # main update
    screen.register_fixed_update(fixed_update) # main FUpdate

    # --- activate objects update function ---
    for ss in screen.shapes: #foreach shapes update(inside there scripts)

        if (len(ss.scripts_update) > 0):
            screen.register_update(ss.Update)

        if (len(ss.scripts_fixed_update) > 0):
            screen.register_fixed_update(ss.FUpdate)

    for ui in screen.UI: #foreach shapes update(inside there scripts)

        if (len(ui.scripts_update) > 0):
            screen.register_update(ui.Update)

        if (len(ui.scripts_fixed_update) > 0):
            screen.register_fixed_update(ui.FUpdate)

    screen.show() #display screen

main() # calling main func to activate everything

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

# TO DO next:
#idk im too fast


# add a texture system for objects and background, and its better to have like unity, were you can chnage texture settings or flip it
# add more natural objects lie hex and stuff like that
# add costume poly shape
# add a scenes 
# add a way to add static objects that dont need an rb, like tree in background and stuff, a way to add an image to be clear
# fix collistion, make small amount to be zero and grounded, so they stop shaking
# add gizmo mode, which is normal shapes but dont interact with anything
# add Ray cast system
# make a basic doc that cover functions you did
# opt code, see u after 5 years ;)

#high end step:
#add a UI for everything as of its an editor fr

#if you finish all of this shit, create a game without changing a single file from the engine script

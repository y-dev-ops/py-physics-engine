from basic.screen import *
from caculations.kinematics import *


#scripts: (here you add your scripts from '/scripts' to import them)
from scripts.follow_the_mouse import *
from scripts.drag import *



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

def inspector(screen): # here you add every Shape you need in your screen
    
    
    # Exit Button
    button = screen.add_button(text="X", command=screen.root.destroy) # for exit button
    

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
            drag()
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
        position=[0, 300],
        size=[400, 80],
        color='pink',
        outline={
            'color': 'blue',
            'stroke': 5,
        }
    ))

    # Note: isStatic is True by def

def main(): # main, handling everthing on this project

    # --- Manage Screen ---
    screen = Screen(screen_title, fps=fps, screen_color=screen_color)
    screen.root.attributes('-fullscreen', is_fullscreen) # fullscreen mode
    
    # --- activate inspector ---
    inspector(screen) #passing current screen to inspector

    # --- main updates ---
    def update(delta):
        pass

    def fixed_update(delta):
        physics_engine(delta, screen.shapes)

    screen.register_update(update) # main update
    screen.register_fixed_update(fixed_update) # main FUpdate

    # --- activate objects update function ---
    for ss in screen.shapes: #foreach shapes update(inside there scripts)

        if (len(ss.scripts_update) > 0):
            screen.register_update(ss.Update)

        if (len(ss.scripts_fixed_update) > 0):
            screen.register_fixed_update(ss.FUpdate)

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
#add destroy item when right click: check drag()

# TO DO next:
#idk im too fast

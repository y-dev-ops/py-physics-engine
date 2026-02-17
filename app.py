from basic.screen import *
from caculations.kinematics import *


#scripts: (here you add your scripts from '/scripts' to import them)
from scripts.follow_the_mouse import *



#--- Settings ---
screen_title = "phy engine"
is_fullscreen = True
fps = 60

def pack_var(position = [0,0], size=[50, 50], color='red', angle=0, material={}, mass=1, ingore_static = False, gravity=True, isStatic=True): #here we turn your vars into dict for easy transfer between objects
    def_dict = { # to do: next add the scripts here, so they applied directly
        'x': position[0],
        'y': position[1],
        'angle': angle,
        'color': color,
        'rb': {
            'gravity': gravity,
            'isStatic': isStatic,
            'ingore_static': ingore_static,
            'bounciness': 0.6 if material.get('bounciness') == None else material.get('bounciness'),
            'friction': 0.4 if material.get('friction') == None else material.get('friction'),
            'static_friction': 0.6 if material.get('static_friction') == None else material.get('static_friction'),
            'mass': mass,
        },
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

    # --- scene objects ---

    # circle object
    circle = screen.add_circle(pack_var(
        position=[150, 100],
        size=[50],
        material=bouncy_material,
        mass=3,
        isStatic=False
    ))

    # rect_3 object
    rect_3 = screen.add_rectangle(pack_var(
        position=[400, 100],
        size=[200, 150],
        material=spongy_material,
        mass=3,
        isStatic=False
    ))
    
    # rect_4 object
    rect_4 = screen.add_rectangle(pack_var(
        position=[600, 600],
        size=[700, 50],
        color='green',
    ))

    # rect object
    rect = screen.add_rectangle(pack_var(
        position=[50, 500],
        size=[120, 80],
        color='black',
        ingore_static=True,
        isStatic=False,
        gravity=False
    ))
    rect.add_script(follow_the_mouse(rect))

    # rect_2 object
    rect_2 = screen.add_rectangle(pack_var(
        position=[0, 300],
        size=[400, 80],
        color='pink',
    ))



    # Note: isStatic is True by def




def main(): # main, handling everthing on this project

    # --- Manage Screen ---
    screen = Screen(screen_title, fps=fps)
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
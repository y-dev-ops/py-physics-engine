from basic.screen import *
from caculations.kinematics import *


#scripts: (here you add your scripts from '/scripts' to import them)
from scripts.follow_the_mouse import *

#--- Settings ---
screen_title = "phy engine"
is_fullscreen = True
fps = 60

def inspector(screen): # here you add every Shape you need in your screen
    # Exit Button
    button = screen.add_button(text="X", command=screen.root.destroy) # for exit button

    # circle object
    circle = screen.add_circle(150, 100, 50, mass=3, isStatic=False, bounciness=.8, friction=0.3)

    # rect_3 object
    rect_3 = screen.add_rectangle(500, 100, 120, 80,mass=5, isStatic=False, bounciness=.1, friction=0.7, static_friction=0.8)
    
    # rect_4 object
    rect_4 = screen.add_rectangle(400, 400, 600, 120, color='green')

    # rect object
    rect = screen.add_rectangle(50, 500, 120, 80,gravity=False, mass=1, isStatic=False)
    rect.add_script(follow_the_mouse(rect))

    # rect_2 object
    rect_2 = screen.add_rectangle(0, 300, 400, 80)



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
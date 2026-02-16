#here we manage and Load Everything
from basic.screen import *
from caculations.kinematics import *
#scripts:
from scripts.follow_the_mouse import *
#from scripts import follow_the_mouse


screen_title = "title"


        

states_rb = []

def main(): 
    screen = Screen("Physics Test", fps=60)
    circle = screen.add_circle(150, 100, 50, mass=5, isStatic=False)
    rect_3 = screen.add_rectangle(500, 100, 120, 80,mass=5, isStatic=False)
    rect_4 = screen.add_rectangle(400, 400, 600, 120, color='green')
    rect = screen.add_rectangle(50, 300, 120, 80)
    rect_2 = screen.add_rectangle(0, 300, 400, 80)

    #for shape in screen.shapes:
    #    if (shape.rb.mass > 0):
    #        states_rb.append(shape)
            #print(shape)

    #ftm = follow_the_mouse(rect)

    rect.add_script(follow_the_mouse(rect))



    def update(delta):
        #circle.position(circle.x+1, circle.y-1) # we got update, what we need is to start using kinimatics to cal
        
        
        pass


            

    def fixed_update(delta):
        physics_engine(delta, screen.shapes)
        pass


    for ss in screen.shapes:
        screen.register_update(ss.update)



    screen.register_update(update)
    screen.register_fixed_update(fixed_update)


    screen.show()




    
main()

from scripts.template import Template
import pygame

class follow_the_mouse(Template): # i need to imporve the script template copy to be like mono in UNITY
    def __init__(self): #
        self.hasUpdate = True
        self.hasFUpdate = False

    def start(self):
        print(self.obj, 'added script')
        self.obj.rb.ingore_static = True

    def update(self, delta): # to avoid def between update and fixed update, we will make it smooth tracking, and we want it to ingore static objects
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate the distance to the mouse # issue: top-left, fixed to be centered
        dx = mouse_x - (self.obj.x)
        dy = mouse_y - (self.obj.y)
        
        # Instead of teleporting, set a velocity that "pulls" it to the cursor
        # Lower the 0.1 to make it "lazier/smoother", raise it for "snappier"
        smoothing = 0.15 
        self.obj.rb.velocity[0] = dx * (smoothing / delta)
        self.obj.rb.velocity[1] = dy * (smoothing / delta)

        #rotate for testing,
        #self.shape.rotation(self.shape.angle + 1)

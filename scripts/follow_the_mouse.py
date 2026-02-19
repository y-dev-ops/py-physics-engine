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
        
        dx = mouse_x - self.obj.x
        dy = mouse_y - self.obj.y
        
        # Set velocity to move towards the cursor.
        # This is a spring-like force. A larger multiplier makes it "snappier".
        # Avoid dividing by delta, which causes instability with variable frame rates.
        strength = 10
        self.obj.rb.velocity[0] = dx * strength
        self.obj.rb.velocity[1] = dy * strength

from scripts.template import Template
import pygame

class drag(Template): # i need to imporve the script template copy to be like mono in UNITY
    def __init__(self): #
        self.hasUpdate = True
        self.hasFUpdate = False

    def update_pos(self, x, y):
        mouse_x = x
        mouse_y = y
            
        # Calculate the distance to the mouse # issue: top-left, fixed to be centered
        dx = mouse_x - (self.obj.x)
        dy = mouse_y - (self.obj.y)
            
        # Instead of teleporting, set a velocity that "pulls" it to the cursor
        # Lower the 0.1 to make it "lazier/smoother", raise it for "snappier"
        smoothing = 0.15 
        self.obj.rb.velocity[0] = dx * (smoothing) * self.strength
        self.obj.rb.velocity[1] = dy * (smoothing) * self.strength

    def get_shape_at(self, x, y): # fast fillter
        minx, miny, maxx, maxy = self.obj.get_aabb()
        if minx <= x <= maxx and miny <= y <= maxy:
            return self.obj

        return None

    def get_mouse_p(self):
        mx, my = pygame.mouse.get_pos()
        # Convert screen mouse pos to world mouse pos using the camera
        wx, wy = self.obj.screen.camera.screen_to_world(mx, my)
        return wx, wy

    def mouse_down(self, destroy=False):

        x, y = self.get_mouse_p()

        shape = self.get_shape_at(x, y)
        
        if shape:
            if (destroy):
                self.obj.destroy()
                return
            self.dragged_shape = shape
            self.dragged_shape.rb.gravity = not self.prev_gravity

    def mouse_drag(self):
        if not self.dragged_shape:
            return

        x, y = self.get_mouse_p()
        self.update_pos(x,y)

    def mouse_up(self):
        if self.dragged_shape:
            #print("Released:", self.dragged_shape)
            self.dragged_shape.rb.gravity = self.prev_gravity

        self.dragged_shape = None

    def start(self):
        #print(self.shape, 'added script')
        self.dragged_shape = None
        self.strength = 10
        self.prev_gravity = self.obj.rb.gravity

    def called_with_get(self, script):
        print('i got called from :', script)


    def update(self, delta):
        if (self.obj.screen.input.getKeyDown('mouse1')):
            self.mouse_down()
            #print('m1')
        if (self.obj.screen.input.getKeyHold('mouse1')):
            self.mouse_drag()
        if (self.obj.screen.input.getKeyUp('mouse1')):
            self.mouse_up()

        if (self.obj.screen.input.getKeyDown('mouse3')):
            self.mouse_down(destroy=True)
        
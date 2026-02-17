from scripts.template import Template

class follow_the_mouse(Template):
    def __init__(self, shape):
        self.shape = shape
        print(self.shape, 'added script')
        self.hasUpdate = True
        self.hasFUpdate = False
        self.shape.rb.ingore_static = True

    def update(self, delta): # to avoid def between update and fixed update, we will make it smooth tracking, and we want it to ingore static objects
        mouse_x = self.shape.screen.root.winfo_pointerx() - self.shape.screen.root.winfo_rootx()
        mouse_y = self.shape.screen.root.winfo_pointery() - self.shape.screen.root.winfo_rooty()
        
        # Calculate the distance to the mouse # issue: top-left, fixed to be centered
        dx = mouse_x - (self.shape.x)
        dy = mouse_y - (self.shape.y)
        
        # Instead of teleporting, set a velocity that "pulls" it to the cursor
        # Lower the 0.1 to make it "lazier/smoother", raise it for "snappier"
        smoothing = 0.15 
        self.shape.rb.velocity[0] = dx * (smoothing / delta)
        self.shape.rb.velocity[1] = dy * (smoothing / delta)

        #rotate for testing,
        self.shape.rotation(self.shape.angle + 10)

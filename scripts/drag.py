from scripts.template import Template
class drag(Template): # i need to imporve the script template copy to be like mono in UNITY
    def __init__(self): #
        self.hasUpdate = False
        self.hasFUpdate = False

    def update_pos(self, x, y):
        mouse_x = x
        mouse_y = y
            
        # Calculate the distance to the mouse # issue: top-left, fixed to be centered
        dx = mouse_x - (self.shape.x)
        dy = mouse_y - (self.shape.y)
            
        # Instead of teleporting, set a velocity that "pulls" it to the cursor
        # Lower the 0.1 to make it "lazier/smoother", raise it for "snappier"
        smoothing = 0.15 
        self.shape.rb.velocity[0] = dx * (smoothing) * self.strength
        self.shape.rb.velocity[1] = dy * (smoothing) * self.strength

    def get_shape_at(self, x, y): # fast fillter
        minx, miny, maxx, maxy = self.shape.get_aabb()
        if minx <= x <= maxx and miny <= y <= maxy:
            return self.shape

        return None

    def on_mouse_down(self, event):
        x, y = event.x, event.y

        shape = self.get_shape_at(x, y)
        
        if shape:
            self.dragged_shape = shape
            self.dragged_shape.rb.gravity = False

    def on_mouse_drag(self, event):
        if not self.dragged_shape:
            return

        x, y = event.x, event.y
        self.update_pos(x,y)

    def on_mouse_up(self, event):
        if self.dragged_shape:
            #print("Released:", self.dragged_shape)
            self.dragged_shape.rb.gravity = True

        self.dragged_shape = None

    def start(self):
        print(self.shape, 'added script')
        self.dragged_shape = None
        self.strength = 10
from scripts.template import Template

class follow_the_mouse(Template):
    def __init__(self, shape):
        self.shape = shape
        print(self.shape, 'added script')
        self.hasUpdate = True
        self.hasFUpdate = False

    def update(self, delta):
        # 1) Get current mouse position
        mouse_x = self.shape.screen.root.winfo_pointerx() - self.shape.screen.root.winfo_rootx()
        mouse_y = self.shape.screen.root.winfo_pointery() - self.shape.screen.root.winfo_rooty()
        
        # 2) Calculate velocity: (New_Pos - Old_Pos) / Time
        if delta > 0:
            vx = (mouse_x - self.shape.x) / delta
            vy = (mouse_y - self.shape.y) / delta
            self.shape.rb.velocity = [vx, vy]

        # 3) Finally, move the shape
        self.shape.position(mouse_x, mouse_y)

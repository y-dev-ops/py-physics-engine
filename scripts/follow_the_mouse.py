#return the position to change it to poistion mouse place

class follow_the_mouse:
    def __init__(self, shape):
        self.shape = shape
        print(self.shape, 'added script')
        self.hasUpdate = True
        self.hasFUpdate = False

    def update(self, delta):
        # Get current mouse position relative to the canvas
        mouse_x = self.shape.screen.root.winfo_pointerx() - self.shape.screen.root.winfo_rootx()
        mouse_y = self.shape.screen.root.winfo_pointery() - self.shape.screen.root.winfo_rooty()
        
        # Update the shape's position
        self.shape.position(mouse_x, mouse_y)

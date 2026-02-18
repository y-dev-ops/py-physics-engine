class Template: # this is a template, you can make your own scripts by copying this
    def __init__(self):
        self.hasUpdate = True
        self.hasFUpdate = True

    def update(self, delta):
        #add your code here
        pass

    def fixed_update(self, delta):
        #add your code here
        pass

    def on_mouse_down(self, event):
        pass

    def on_mouse_drag(self, event):
        pass

    def on_mouse_up(self, event):
        pass

    def start(self):
        pass

    def parent(self, shape): # here we assign the Shape it self to connect the scripts like a tree
        self.shape = shape
        self.start()

    def destroyed(self):
        print(self, 'got destroyed from: ', self.shape)
        self.shape = None
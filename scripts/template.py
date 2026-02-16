class Template: # this is a template, you can make your own scripts by copying this
    def __init__(self, shape):
        self.shape = shape
        print(self.shape, ' added script')
        self.hasUpdate = True
        self.hasFUpdate = True

    def update(self, delta):
        #add your code here
        pass

    def fixed_update(self, delta):
        #add your code here
        pass
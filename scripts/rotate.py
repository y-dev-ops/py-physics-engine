from scripts.template import Template
import pygame

class rotate(Template): # i need to imporve the script template copy to be like mono in UNITY
    def __init__(self): #
        self.hasUpdate = True
        self.hasFUpdate = False

    def start(self):
        print(self.obj, 'added script')


    def update(self, delta):
        if (self.obj.screen.input.getKeyHold('mouse1')):
            self.obj.rotate_by(10)
            #pygame.transform.rotate(original_btn, self.angle)


        if (self.obj.screen.input.getKeyDown('mouse3')):
            self.obj.destroy()
        
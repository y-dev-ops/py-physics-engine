from scripts.template import Template
import pygame

class rotate(Template): # i need to imporve the script template copy to be like mono in UNITY
    def __init__(self): #
        self.hasUpdate = True
        self.hasFUpdate = False

    def start(self):
        print(self.obj, 'added script')


        # try get a component and call a function from it #drag
        _drag = self.obj.getcomponent('drag')

        _drag.called_with_get(self)



    def update(self, delta):
        if (self.obj.screen.input.getKeyHold('mouse1')):
            self.obj.rotate_by(50*delta)
            #pygame.transform.rotate(original_btn, self.angle)
        
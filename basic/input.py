import pygame

class Input:
    def __init__(self, screen):
        self.screen = screen
        self.down_keys = {}
        self.hold_keys = {}
        self.up_keys = {}

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(pygame.key.name(event.key))
        elif event.type == pygame.KEYUP:
            self.handle_keyup(pygame.key.name(event.key))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_keydown(f'mouse{event.button}')
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_keyup(f'mouse{event.button}')

    # Note: 
    # mouse1 = Left Click
    # mouse2 = Middle Click
    # mouse3 = Right Click

    def handle_keydown(self, key):
        # Ignore auto-repeat
        if self.hold_keys.get(key):
            return 

        #print(f"Key Down: {key}")
        self.down_keys[key] = True
        self.hold_keys[key] = True
        self.up_keys[key] = False
    
    def handle_keyup(self, key):
        #print(f"Key Up: {key}")
        self.down_keys[key] = False
        self.hold_keys[key] = False
        self.up_keys[key] = True

    # ... keep your getKeyDown, getKeyHold, and clear_frame_inputs as they are

    def getKeyDown(self, keycode):
        if self.down_keys.get(keycode):
            #self.down_keys[keycode] = False # Consume the event
            return True
        return False

    def getKeyUp(self, keycode):
        if self.up_keys.get(keycode):
            #self.up_keys[keycode] = False # Consume the event
            return True
        return False

    def getKeyHold(self, keycode):
        return self.hold_keys.get(keycode, False)

    def clear_frame_inputs(self):
        self.down_keys.clear()
        self.up_keys.clear()
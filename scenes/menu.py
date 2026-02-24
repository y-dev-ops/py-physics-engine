# scenes/level_01.py
from models.scene import Scene
from basic.screen import *

class MainMenu(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.name = "Main Menu"
        self.scene_color = 'white'
        self.phy_engine = False #just UI



    def elements(self, screen):

        pack_ui = screen.app.pack_ui
        hover_color = (200, 200, 200)

        #--- Outline Settings ---
        outline = {
            'color': 'black',
            'stroke': 1, # 0 for no outline
        }

        # --- UI objects ---
        play_button = screen.add_button(pack_ui(
            position=[0, 100],
            anchor='center',
            size=[200, 50],
            text='Play',
            color='black',
            font_size=24,
            font_color='white',
            command= screen.app.scene_manager.load_next_scene, #lambda: setattr(screen, 'running', False),
            hover_color=hover_color, # Light grey on hover
        ))
        settings_button = screen.add_button(pack_ui(
            position=[0, 0],
            anchor='center',
            size=[200, 50],
            color='black',
            text='Settings',
            font_size=24,
            font_color='white',
            #command=lambda: setattr(screen, 'running', False),
            hover_color=hover_color, # Light grey on hover
        ))

        quit_button = screen.add_button(pack_ui(
            position=[0, -100],
            anchor='center',
            size=[200, 50],
            color='black',
            text='Quit',
            font_size=24,
            font_color='white',
            command=lambda: setattr(screen, 'running', False),
            hover_color=hover_color, # Light grey on hover
        ))
        text = screen.add_text(pack_ui(
            position=[0, 0],
            anchor='top-left',
            size=[80, 20],
            text='Damn this is a text',
            font_size=24,
            font_color='black',
        ))

    def on_load(self):
        # This triggers exactly once when the scene loads
        print("menu has loaded! Spawning UI...")
        
        # Run elements
        self.elements(self.screen)
        # camera setup
        self.screen.camera.set_offset([0,0])

from caculations.kinematics import *
class Scene:
    def __init__(self, app):
        self.app = app
        self.screen = self.app.screen
        self.shapes = []  # Every scene has its own list of physics objects
        self.UI = []  # Every scene has its own list of UI
        self.name = "Unnamed Scene"
        self.phy_engine = True
        self.scene_color = 'white'

    def on_load(self):
        # Unity's Start() / OnEnable()
        # You will spawn your custom shapes and trees here!
        pass

    def on_unload(self):
        # Unity's OnDisable() / OnDestroy()
        # Clean up anything specific if needed
        
        # Iterate over a COPY of the list ([:]) so we can remove items safely
        for shape in self.shapes[:]:
            shape.destroy()
        for ui in self.UI[:]:
            ui.destroy()
            
        self.shapes.clear()
        self.UI.clear()

    def update(self, delta):
        # Regular update for logic
        for shape in self.shapes:
            shape.Update(delta)

    def fixed_update(self, delta):
        # Physics update
        if (self.phy_engine):
            physics_engine(delta, self.shapes)

        for shape in self.shapes:
            shape.FUpdate(delta)
        for ui in self.UI:
            ui.FUpdate(delta)
        

    def draw(self, surface):
        # Call your drawing logic here
        pass

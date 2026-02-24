from caculations.kinematics import *
class Scene:
    def __init__(self, app):
        self.app = app
        self.screen = self.app.screen
        self.shapes = []  # Every scene has its own list of physics objects
        self.name = "Unnamed Scene"
        self.phy_engine = True

    def on_load(self):
        # Unity's Start() / OnEnable()
        # You will spawn your custom shapes and trees here!
        pass

    def on_unload(self):
        # Unity's OnDisable() / OnDestroy()
        # Clean up anything specific if needed
        self.shapes.clear()

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
        

    def draw(self, surface):
        # Call your drawing logic here
        pass

    def pack_var(self):
        self.app
class SceneManager:
    def __init__(self, app):
        self.app = app
        self.screen = app.screen
        self.build_index = []      # List of Scene Classes
        self.active_scene = None   # The instantiated current scene
        self.current_index = -1

    def add_to_build(self, scene_class):
        """Adds a scene to the ordered list (Like Unity's Build Settings)"""
        self.build_index.append(scene_class)

    def load_scene(self, index):
        """Loads a scene based on its order in the list"""
        if index < 0 or index >= len(self.build_index):
            print(f"Error: Scene index {index} is out of bounds!")
            return

        # 1. Unload current scene if it exists
        if self.active_scene is not None:
            self.active_scene.on_unload()

        # 2. Instantiate the new scene from the class
        self.current_index = index
        scene_class = self.build_index[index]
        # handle update:
        if (self.active_scene != None):
            self.screen.remove_update(self.active_scene.update) # main update
            self.screen.remove_fixed_update(self.active_scene.fixed_update) # main FUpdate

        self.active_scene = scene_class(self.app)

        if (self.active_scene != None):
            self.screen.register_update(self.active_scene.update) # main update
            self.screen.register_fixed_update(self.active_scene.fixed_update) # main FUpdate

        
        # 3. Trigger the OnLoad event
        print(f"Loading Scene: {self.active_scene.name}")
        self.active_scene.on_load()

    def load_next_scene(self):
        """Helper to go to the next level"""
        self.load_scene(self.current_index + 1)
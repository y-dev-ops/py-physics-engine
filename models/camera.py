# models/camera.py
class Camera:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # The World position the camera is currently looking at
        self.x = 0.0
        self.y = 0.0

    def apply_to_point(self, world_x, world_y):
        """Converts a single world coordinate to a screen coordinate."""
        # To find the screen position of an object, we do:
        # screen_pos = world_pos - camera_pos
        # However, this makes the object appear at the top-left of the screen.
        # To center the view on the camera's position, we add half the screen size.
        screen_x = world_x - self.x + (self.width / 2)
        screen_y = world_y - self.y + (self.height / 2)
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Converts a screen coordinate (mouse) to a world coordinate."""
        world_x = screen_x + self.x - (self.width / 2)
        world_y = screen_y + self.y - (self.height / 2)
        return world_x, world_y

    def get_offset(self):
        """
        Returns the raw X and Y offset to apply to world coordinates to get screen coordinates.
        This is more efficient for transforming a list of points, as the offset is calculated once.
        """
        offset_x = (self.width / 2) - self.x
        offset_y = (self.height / 2) - self.y
        return offset_x, offset_y

    
    def set_offset(self, position=[0,0]):
        """
        set x and y, as middled
        """
        self.x = (self.width / 2) - position[0]
        self.y = (self.height / 2) - position[1]


    def follow(self, target_shape, delta, smooth_speed=5.0):
        """
        Unity-style smooth follow using Linear Interpolation (Lerp).
        The camera smoothly moves towards the target's position each frame.
        """
        if target_shape is None:
            return
            
        # The formula for linear interpolation (lerp) is:
        # new_value = current_value + (target_value - current_value) * factor
        # Here, 'factor' is 'smooth_speed * delta' to make it frame-rate independent.
        self.x += (target_shape.x - self.x) * smooth_speed * delta
        self.y += (target_shape.y - self.y) * smooth_speed * delta
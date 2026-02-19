import pygame
import math

class simple_UI:
    # Default values for a UI element
    def_dict = {
        'x': 0,
        'y': 0,
        'width': 50,
        'height': 50,
        'angle': 0,
        'color': 'white',
        'command': None,
        'texture': None,
        'text': '',
        'font': None,
        'font_size': 16,
        'screen': None,
        'hover_color': None,
        'scripts': [],
        'scripts_update': [],
        'scripts_fixed_update': [],
    }
    def unpack(self, _dict):
        """Unpacks a dictionary into instance attributes."""
        for key, value in _dict.items():
            setattr(self, key, value)

        if (len(self.scripts) > 0):
            for script in self.scripts:
                script.parent(self)
                if (script.hasUpdate):
                    self.scripts_update.append(script)
                if (script.hasFUpdate):
                    self.scripts_fixed_update.append(script)

    def __init__(self, _dict, py_img):
        data = self.def_dict.copy()
        data.update(_dict) 
        self.unpack(data)

        # Image and Rect setup
        self.original_ui = py_img
        self.ui = self.original_ui.copy()  # The image to be drawn
        self.ui_rect = self.ui.get_rect(center=(self.x, self.y))

        # Create a tinted hover image if a color is provided
        self.hover_ui = None
        if self.hover_color:
            self.hover_ui = self.original_ui.copy()
            # Create a colorized surface and blend it
            color_surface = pygame.Surface(self.hover_ui.get_size(), pygame.SRCALPHA)
            color_surface.fill(self.hover_color)
            # Using BLEND_RGBA_MULT tints the image with the hover color
            self.hover_ui.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Text setup
        self.hasText = bool(self.text)
        if self.hasText:
            self.render_text()

    def render_text(self):
        """Renders the text onto a surface."""
        if not self.hasText or not self.font:
            return
        # Render text with a black color
        self.text_surf = self.font.render(self.text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(center=self.ui_rect.center)

    def execute_command(self): # add it to any ui element and put ur code
        pass

    def on_render(self):
        """
        Called every frame from the screen's draw loop.
        Handles hover effects and click events.
        """
        if not self.screen:
            return

        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.ui_rect.collidepoint(mouse_pos)

        # 1. Select Base Image (Normal vs Hover)
        if is_hovering and self.hover_ui:
            base_ui = self.hover_ui
        else:
            base_ui = self.original_ui

        # 2. Apply Rotation
        if self.angle != 0:
            self.ui = pygame.transform.rotate(base_ui, self.angle)
            self.ui_rect = self.ui.get_rect(center=(self.x, self.y)) # Re-center to prevent wobble
        else:
            self.ui = base_ui
            self.ui_rect = self.ui.get_rect(center=(self.x, self.y))

        # 3. Check for event
        self.execute_command()

    def add_script(self, script):
        if (script.hasUpdate):
            self.scripts_update.append(script)
        if (script.hasFUpdate):
            self.scripts_fixed_update.append(script)

        self.scripts.append(script)
        
    def remove_script(self, script, insideLoop = False):
        if (script.hasUpdate):
            self.scripts_update.remove(script)
        if (script.hasFUpdate):
            self.scripts_fixed_update.remove(script)
        if (not insideLoop):
            self.scripts.remove(script)

        script.destroyed()

    def Update(self, delta):
        for script in self.scripts_update:
                script.update(delta)

    def FUpdate(self, delta):
        for script in self.scripts_fixed_update:
                script.fixed_update(delta)

    def position(self, x, y):
        """Moves the UI element and updates its rect."""
        self.x = x
        self.y = y
        self.ui_rect.center = (self.x, self.y)
        # Also update text position if it exists
        if self.hasText:
            self.text_rect.center = self.ui_rect.center

    def rotate_to(self, angle_deg):
        # set absolute angle in degrees
        self.angle = angle_deg

    def rotate_by(self, d_angle_deg):
        self.angle += d_angle_deg

    def get_aabb(self):
        """Returns the axis-aligned bounding box."""
        return self.ui_rect

    def destroy(self):
        """Removes the UI element from the screen."""
        if self.screen and self in self.screen.UI:
            self.screen.UI.remove(self)

        if (len(self.scripts) > 0):
            for script in self.scripts:
                self.remove_script(script, insideLoop=True)

        self.scripts.clear()

        self.is_destroyed = True
        # Note: Script handling from original code is omitted for clarity,
        # as it's complex and not used for this button.

    
# you can add your own UI here
class Button(simple_UI):
    def __init__(self, _dict, py_img):
        _dict['type'] = 'button'
        super().__init__(_dict, py_img)
        # The get_aabb from simple_UI is sufficient.
        # No need to override it.

    def execute_command(self):
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = self.ui_rect.collidepoint(mouse_pos)

        # 1. Select Base Image (Normal vs Hover)
        if is_hovering and self.hover_ui:
            base_ui = self.hover_ui
        else:
            base_ui = self.original_ui


        # 2. Check for click event
        if is_hovering and self.screen.input.getKeyDown('mouse1'):
            # Execute the command if it exists
            if self.command:
                self.command()
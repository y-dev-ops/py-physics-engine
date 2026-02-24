import pygame
from models.shape import *
from models.ui_element import *
import basic.input as inp


class Screen:
    def __init__(self, app, title="My App", width=1280, height=720, fps=60, screen_color="white", is_fullscreen=True):
        # pygame setup
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.font = pygame.font.SysFont("Arial", 40)
        
        if (is_fullscreen): 
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.screen_color = screen_color
        self.clock = pygame.time.Clock()
        self.running = True

        #self.shapes = []  # keep track of shapes
        #self.UI = []
        self.fps = fps
        self.dt = 1/fps
        self.accumulator = 0

        self.update_callbacks = []
        self.fixed_update_callbacks = []
        #input manager
        self.input = inp.Input(self)
        self.app = app


    def add_button(self, _dict):
        original_img = pygame.image.load(_dict['texture']).convert_alpha()
        py_img = pygame.transform.scale(original_img, (_dict['width'], _dict['height']))
        _dict['font'] = self.font = pygame.font.SysFont("Arial", _dict['font_size'])
        _dict['screen'] = self
        button = Button(_dict, py_img)
        self.UI.append(button)
        return button

    def add_circle(self,_dict):
        _dict['screen'] = self
        circle = Circle(_dict)
        self.app.scene_manager.active_scene.shapes.append(circle)
        return circle

    def add_rectangle(self, _dict):
        _dict['screen'] = self
        rect = Rectangle(_dict)
        self.app.scene_manager.active_scene.shapes.append(rect)
        return rect

    def add_triangle(self, _dict):
        _dict['screen'] = self
        tri = Triangle(_dict)
        self.app.scene_manager.active_scene.shapes.append(tri)
        return tri

    def add_pentagon(self, _dict):
        _dict['screen'] = self
        pen = Pentagon(_dict)
        self.app.scene_manager.active_scene.shapes.append(pen)
        return pen
    
    def add_hexagon(self, _dict):
        _dict['screen'] = self
        hx = Hexagon(_dict)
        self.app.scene_manager.active_scene.shapes.append(hx)
        return hx

    def add_custom_poly(self, _dict):
        _dict['screen'] = self
        pl = Custom_Poly(_dict)
        self.app.scene_manager.active_scene.shapes.append(pl)
        return pl

    def draw_shape(self, shape):
        
        # 1) TEXTURED SHAPE
        if hasattr(shape, 'orig_image') and shape.orig_image is not None:
            # Rotate the perfectly masked shape
            rotated_image = pygame.transform.rotate(shape.orig_image, -shape.angle)
            
            # Find the new center so it rotates perfectly around the middle
            new_rect = rotated_image.get_rect(center=(shape.x, shape.y))
            
            # Draw it! (No offsets needed here anymore, they are baked into orig_image)
            self.screen.blit(rotated_image, new_rect.topleft)

        # 2) NO TEXTURE / BASIC COLOR FALLBACK
        else:
            if shape.type == 'circle':
                print ('shape: ', shape)
                pygame.draw.circle(self.screen, shape.color, (int(shape.x), int(shape.y)), int(shape.radius))
                
                if hasattr(shape, 'outline') and shape.outline.get('stroke', 0) > 0:
                    pygame.draw.circle(self.screen, shape.outline['color'], (int(shape.x), int(shape.y)), int(shape.radius), shape.outline['stroke'])
            
            elif shape.type != 'circle':
                points_tuples = list(zip(shape.points[0::2], shape.points[1::2]))
                
                pygame.draw.polygon(self.screen, shape.color, points_tuples)
                
                if hasattr(shape, 'outline') and shape.outline.get('stroke', 0) > 0:
                    pygame.draw.polygon(self.screen, shape.outline['color'], points_tuples, shape.outline['stroke'])

    def draw_ui(self, ui_element):
        ui_element.on_render() # Update visual state (rotation/hover) first
        self.screen.blit(ui_element.ui, ui_element.ui_rect)
        if (ui_element.hasText):
            self.screen.blit(ui_element.text_surf, ui_element.text_rect)  # Draw text on top

    def show(self):
        self.run()


    def register_update(self, func): #why are you reading my code >:(   just trust bro aint hacking you
        self.update_callbacks.append(func)

    def register_fixed_update(self, func):
        self.fixed_update_callbacks.append(func)
    
    def remove_update(self, func):
        self.update_callbacks.remove(func)
    def remove_fixed_update(self, func):
        self.fixed_update_callbacks.remove(func)

    def run(self):
        while (self.running):
            dt_ms = self.clock.tick(self.fps) 
            delta = dt_ms / 1000.0
            
            # 1) Event Handling
            self.input.clear_frame_inputs()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.input.handle_event(event)
                
                # Check for scene switch inside the event loop
                if event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                    self.app.scene_manager.load_next_scene()
            
            # 2) Update Logic
            for func in self.update_callbacks:
                func(delta)

            # 3) Fixed Update Logic
            self.accumulator += delta
            while self.accumulator >= self.dt:
                for func in self.fixed_update_callbacks:
                    func(self.dt)
                self.accumulator -= self.dt

            # 4) Render
            self.screen.fill(self.screen_color)
            if self.app.scene_manager.active_scene:
                for shape in self.app.scene_manager.active_scene.shapes:
                    self.draw_shape(shape)
            
            #handle update in scene


            #for ui_element in self.UI:
                #self.draw_ui(ui_element)

                
            pygame.display.flip()

        pygame.quit()
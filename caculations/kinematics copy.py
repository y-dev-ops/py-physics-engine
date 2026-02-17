import math

pixels_to_meter = 100
def integrate(shape, delta):
    if shape.rb.isStatic:
        return

    # a = F / m
    ax = shape.rb.force[0] * pixels_to_meter / shape.rb.mass
    ay = shape.rb.force[1] * pixels_to_meter / shape.rb.mass

    # Semi-implicit Euler (stable)
    shape.rb.velocity[0] += ax * delta
    shape.rb.velocity[1] += ay * delta
    
    #shape.center_x += shape.rb.velocity[0] * delta
    #shape.center_y += shape.rb.velocity[1] * delta


    new_x = shape.x + shape.rb.velocity[0] * delta
    new_y = shape.y + shape.rb.velocity[1] * delta

    shape.position(new_x, new_y)

    # reset force
    shape.rb.force = [0,0]

def cal_gravity(shape, g=9.8):
    if shape.rb.isStatic:
        return
    if (not shape.rb.gravity):
        return
    #F=mg
    shape.rb.apply_force([0, shape.rb.mass * g])

CELL_SIZE = 100  # pixels

def build_spatial_grid(shapes):
    grid = {}

    for shape in shapes:
        x1, y1, x2, y2 = shape.get_aabb()
        # Add shape to every cell it overlaps
        for cx in range(int(x1 // CELL_SIZE), int(x2 // CELL_SIZE) + 1):
            for cy in range(int(y1 // CELL_SIZE), int(y2 // CELL_SIZE) + 1):
                key = (cx, cy)
                grid.setdefault(key, []).append(shape)

    return grid

def rect_rect_collision(a, b):
    ax1, ay1, ax2, ay2 = a.get_aabb()
    bx1, by1, bx2, by2 = b.get_aabb()
    return ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1

def rect_rect_normal(a, b):
    overlap_x, overlap_y = get_overlap(a, b)
    dx = a.x - b.x
    dy = a.y - b.y
    if overlap_x < overlap_y:
        return (1 if dx > 0 else -1, 0)
    else:
        return (0, 1 if dy > 0 else -1)

def circle_rect_collision(circle, rect):
    closest_x = max(rect.x, min(circle.x, rect.x + rect.width))
    closest_y = max(rect.y, min(circle.y, rect.y + rect.height))
    dx = circle.x - closest_x
    dy = circle.y - closest_y
    return dx*dx + dy*dy < circle.radius**2

def circle_rect_normal(circle, rect):
    closest_x = max(rect.x, min(circle.x, rect.x + rect.width))
    closest_y = max(rect.y, min(circle.y, rect.y + rect.height))
    dx = circle.x - closest_x
    dy = circle.y - closest_y
    dist = math.sqrt(dx*dx + dy*dy)
    if dist == 0:
        return 0, -1
    return dx / dist, dy / dist

def circle_circle_collision(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    r = a.radius + b.radius
    return dx*dx + dy*dy < r*r


def get_collision_normal(a, b):
    if a.type == "rectangle" and b.type == "rectangle":
        return rect_rect_normal(a, b)
    elif a.type == "circle" and b.type == "rectangle":
        return circle_rect_normal(a, b)
    elif a.type == "rectangle" and b.type == "circle":
        nx, ny = circle_rect_normal(b, a)
        return -nx, -ny  # invert normal since we swapped
    elif a.type == "circle" and b.type == "circle":
        dx = a.x - b.x
        dy = a.y - b.y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist == 0:
            return 0, -1
        return dx / dist, dy / dist
    else:
        return 0, 0

def aabb_collision(a, b):
    # Type-dispatch collision
    if a.type == "rectangle" and b.type == "rectangle":
        return rect_rect_collision(a, b)
    elif a.type == "circle" and b.type == "rectangle":
        return circle_rect_collision(a, b)
    elif a.type == "rectangle" and b.type == "circle":
        return circle_rect_collision(b, a)  # swap
    elif a.type == "circle" and b.type == "circle":
        return circle_circle_collision(a, b)
    else:
        return False  # unknown types



def get_overlap(a, b):
    ax1, ay1, ax2, ay2 = a.get_aabb()
    bx1, by1, bx2, by2 = b.get_aabb()

    overlap_x = min(ax2, bx2) - max(ax1, bx1)
    overlap_y = min(ay2, by2) - max(ay1, by1)

    return overlap_x, overlap_y


def resolve_collision(a, b):
    if a.rb.isStatic and b.rb.isStatic:
        return

    if a.rb.ingore_static and b.rb.isStatic:
        return

    if b.rb.ingore_static and a.rb.isStatic:
        return



    if not aabb_collision(a, b):
        return

    # 1) get collision normal
    nx, ny = get_collision_normal(a, b)

    # 2) relative velocity along normal
    v_rel = (a.rb.velocity[0] - (b.rb.velocity[0] if b.rb.mass > 0 else 0),
             a.rb.velocity[1] - (b.rb.velocity[1] if b.rb.mass > 0 else 0))
    v_normal = v_rel[0]*nx + v_rel[1]*ny

    # 3) apply impulse only if objects are moving toward each other
    if v_normal < 0:
        restitution = a.rb.bounciness if b.rb.isStatic else b.rb.bounciness # bounciness
        impulse = -(1 + restitution) * v_normal
        impulse /= (1/a.rb.mass + (1/b.rb.mass if b.rb.mass > 0 else 0))

        # friction # code stolen from GPT btw, I aint einstein
        tx = -ny
        ty = nx
        v_rel_t = (a.rb.velocity[0] - b.rb.velocity[0]) * tx + \
                (a.rb.velocity[1] - b.rb.velocity[1]) * ty
        mu = (a.rb.friction + b.rb.friction) / 2  # Average friction
        f_impulse = -v_rel_t / (1/a.rb.mass + 1/b.rb.mass)
        f_impulse = max(-impulse * mu, min(f_impulse, impulse * mu))

        # 4. Apply Friction Impulse
        if not a.rb.isStatic:
            a.rb.velocity[0] += (f_impulse * tx) / a.rb.mass
            a.rb.velocity[1] += (f_impulse * ty) / a.rb.mass

        if not b.rb.isStatic:
            b.rb.velocity[0] -= (f_impulse * tx) / b.rb.mass
            b.rb.velocity[1] -= (f_impulse * ty) / b.rb.mass
        
        static_threshold = 0.5 
        # If the remaining tangent velocity is very small, kill it entirely
        if abs(v_rel_t) < static_threshold:
            # This "locks" the object to the surface
            if not a.rb.isStatic:
                # Subtract the remaining tangent velocity to hit zero
                a.rb.velocity[0] -= (v_rel_t * tx) 
                a.rb.velocity[1] -= (v_rel_t * ty)

        # 4) apply impulse to velocities
        if not a.rb.isStatic:
            a.rb.velocity[0] += (impulse * nx) / a.rb.mass
            a.rb.velocity[1] += (impulse * ny) / a.rb.mass

        if not b.rb.isStatic:
            b.rb.velocity[0] -= (impulse * nx) / b.rb.mass
            b.rb.velocity[1] -= (impulse * ny) / b.rb.mass

    # 5) positional correction to avoid sinking (optional, small fraction)
    percent = 0.2 # 20% of penetration
    overlap_x, overlap_y = get_overlap(a, b)
    if overlap_x < overlap_y:
        if not a.rb.isStatic:
            a.position(a.x + nx * overlap_x * percent, a.y)
        if not b.rb.isStatic:
            b.position(b.x - nx * overlap_x * percent, b.y)
    else:
        if not a.rb.isStatic:
            a.position(a.x, a.y + ny * overlap_y * percent)
        if not b.rb.isStatic:
            b.position(b.x, b.y - ny * overlap_y * percent)



def check_floor(shape, floor_y):
    bottom = shape.y + shape.radius

    if bottom > floor_y:
        shape.y = floor_y - shape.radius
        shape.rb.velocity[1] *= -0.8

def physics_engine(delta, shapes):
    for shape in shapes:
        # 1) Apply gravity
        cal_gravity(shape)

        # 2) Integrate
        integrate(shape, delta)

        # 3) damping
        shape.rb.velocity[0] *= 0.999
        shape.rb.velocity[1] *= 0.999

    # 4) Broad phase
    grid = build_spatial_grid(shapes)

        # 5) Narrow phase
    for (cell_x, cell_y), cell in grid.items():

        # check this cell and 8 neighbors
        for nx in (-1, 0, 1):
            for ny in (-1, 0, 1):
                neighbor_key = (cell_x + nx, cell_y + ny)

                if neighbor_key not in grid:
                    continue

                neighbor_cell = grid[neighbor_key]

                for a in cell:
                    for b in neighbor_cell:
                        if a is b:
                            continue

                        if aabb_collision(a, b):
                            resolve_collision(a, b)



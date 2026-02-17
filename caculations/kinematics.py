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




# --- trying to do SAT ----

def get_axes(points):
    """Get normals for SAT. For Rectangles, we only need 2 axes (width/height)."""
    axes = []
    # Loop only the first 2 edges (enough for a rectangle)
    # If you use non-rect polygons later, change range(2) to range(len(points)//2)
    for i in range(0, 4, 2): 
        x1, y1 = points[i], points[i+1]
        x2, y2 = points[(i+2) % len(points)], points[(i+3) % len(points)]
        dx, dy = x2 - x1, y2 - y1
        # Normal is (-dy, dx)
        length = math.hypot(dx, dy)
        if length > 0:
            axes.append((-dy / length, dx / length))
    return axes

def project(points, axis):
    """Project points onto axis and return (min, max)."""
    dots = [points[i] * axis[0] + points[i+1] * axis[1] for i in range(0, len(points), 2)]
    return min(dots), max(dots)

def sat_collision(a, b):
    # Get axes from both shapes
    axes = get_axes(a.points) + get_axes(b.points)
    
    min_overlap = float('inf')
    smallest_axis = (0, 0)

    for axis in axes:
        min_a, max_a = project(a.points, axis)
        min_b, max_b = project(b.points, axis)

        # Check for gap
        if max_a < min_b or max_b < min_a:
            return False, (0,0), 0

        # Calculate overlap
        overlap = min(max_a, max_b) - max(min_a, min_b)
        
        if overlap < min_overlap:
            min_overlap = overlap
            smallest_axis = axis

    # Ensure normal points from A to B
    dx = b.x - a.x
    dy = b.y - a.y
    if (dx * smallest_axis[0] + dy * smallest_axis[1]) < 0:
        smallest_axis = (-smallest_axis[0], -smallest_axis[1])

    return True, smallest_axis, min_overlap


# --- old code---

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


#Circle-Polygon
def sat_circle_poly(circle, poly):
    # 1. Edge Normals (standard SAT)
    axes = get_axes(poly.points)
    
    # 2. Closest Vertex Axis
    # Find the vertex closest to the circle center
    closest_v = None
    min_dist_sq = float('inf')
    
    for i in range(0, len(poly.points), 2):
        vx, vy = poly.points[i], poly.points[i+1]
        d_sq = (circle.x - vx)**2 + (circle.y - vy)**2
        if d_sq < min_dist_sq:
            min_dist_sq = d_sq
            closest_v = (vx, vy)
            
    # Add axis from Vertex -> Circle
    # Handle the edge case where center is exactly on vertex
    dx, dy = circle.x - closest_v[0], circle.y - closest_v[1]
    dist = math.hypot(dx, dy)
    
    if dist > 0.0001:
        axes.append((dx/dist, dy/dist))
    else:
        # If center is exactly on vertex, pick an arbitrary axis (e.g., vertex normal)
        # or just skip to avoid Div/0 error.
        pass

    # 3. SAT Loop
    min_overlap = float('inf')
    smallest_axis = (0, 0)

    for axis in axes:
        # Project Poly
        min_p, max_p = project(poly.points, axis)
        
        # Project Circle
        # Project the CENTER, then add/sub radius
        proj_c = circle.x * axis[0] + circle.y * axis[1]
        min_c = proj_c - circle.radius
        max_c = proj_c + circle.radius

        # GAP CHECK
        if max_p < min_c or max_c < min_p:
            return False, (0,0), 0
        
        # Calculate Overlap
        overlap = min(max_p, max_c) - max(min_p, min_c)
        
        if overlap < min_overlap:
            min_overlap = overlap
            smallest_axis = axis

    # 4. Enforce Normal Direction: Poly -> Circle
    # We use the vector from Poly Center to Circle Center
    center_dx = circle.x - poly.x
    center_dy = circle.y - poly.y
    
    if (center_dx * smallest_axis[0] + center_dy * smallest_axis[1]) < 0:
        smallest_axis = (-smallest_axis[0], -smallest_axis[1])

    return True, smallest_axis, min_overlap


#others

def circle_circle_collision(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    r = a.radius + b.radius
    return dx*dx + dy*dy < r*r

def check_collision(a, b):
    if a.type == "rectangle" and b.type == "rectangle":
        return sat_collision(a, b)
    
    if a.type == "circle" and b.type == "circle":
        return circle_circle_collision(a, b)
    
    if a.type == "circle" and b.type == "rectangle":
        # SAT returns Normal(Poly -> Circle), which is (B -> A).
        # Resolve expects (A -> B).
        # We MUST FLIP the normal.
        collided, normal, penetration = sat_circle_poly(a, b)
        return collided, (-normal[0], -normal[1]), penetration
        
    if a.type == "rectangle" and b.type == "circle":
        # SAT returns Normal(Poly -> Circle), which is (A -> B).
        # This matches what Resolve expects.
        # DO NOT FLIP.
        return sat_circle_poly(b, a)

    return False, (0,0), 0


def resolve_collision(a, b, normal, penetration):
    nx, ny = normal

    # 1. Positional Correction (The Anti-Sinking Shield)
    # We push them apart INSTANTLY so they don't wait for velocity to update
    percent = 0.5  # Increased from 0.05 to 0.5 (50% correction per frame)
    slop = 0.05    # Tolerance to prevent jitter
    
    correction_mag = max(penetration - slop, 0.0) / (1/a.rb.mass + (1/b.rb.mass if not b.rb.isStatic else 0)) * percent
    
    cx = correction_mag * nx
    cy = correction_mag * ny

    if not a.rb.isStatic:
        a.position(a.x - cx / a.rb.mass, a.y - cy / a.rb.mass)
    if not b.rb.isStatic:
        b.position(b.x + cx / b.rb.mass, b.y + cy / b.rb.mass)

    # 2. Velocity Impulse (The Bounce)
    rel_vel_x = b.rb.velocity[0] - a.rb.velocity[0]
    rel_vel_y = b.rb.velocity[1] - a.rb.velocity[1]
    
    vel_along_normal = rel_vel_x * nx + rel_vel_y * ny

    # Do not resolve if velocities are separating
    if vel_along_normal > 0:
        return

    # Elasticity (Bounciness)
    e = min(a.rb.bounciness, b.rb.bounciness)
    
    j = -(1 + e) * vel_along_normal
    j /= (1/a.rb.mass + (1/b.rb.mass if not b.rb.isStatic else 0))

    impulse_x = j * nx
    impulse_y = j * ny

    if not a.rb.isStatic:
        a.rb.velocity[0] -= impulse_x / a.rb.mass
        a.rb.velocity[1] -= impulse_y / a.rb.mass
    if not b.rb.isStatic:
        b.rb.velocity[0] += impulse_x / b.rb.mass
        b.rb.velocity[1] += impulse_y / b.rb.mass

    # 3. Friction (The Slide)
    # Recalculate relative velocity after bounce
    rel_vel_x = b.rb.velocity[0] - a.rb.velocity[0]
    rel_vel_y = b.rb.velocity[1] - a.rb.velocity[1]
    
    # Tangent vector (perpendicular to normal)
    tx = -ny
    ty = nx
    
    vt = rel_vel_x * tx + rel_vel_y * ty
    
    if abs(vt) > 0.001: # Avoid divide by zero
        # Friction Coefficient
        mu = math.sqrt(a.rb.friction * b.rb.friction)
        
        friction_j = -vt / (1/a.rb.mass + (1/b.rb.mass if not b.rb.isStatic else 0))
        
        # Clamp friction (Coulomb's Law)
        # Cannot be stronger than normal impulse * friction coefficient
        max_friction = abs(j) * mu
        friction_j = max(-max_friction, min(max_friction, friction_j))

        f_imp_x = friction_j * tx
        f_imp_y = friction_j * ty

        if not a.rb.isStatic:
            a.rb.velocity[0] -= f_imp_x / a.rb.mass
            a.rb.velocity[1] -= f_imp_y / a.rb.mass
        if not b.rb.isStatic:
            b.rb.velocity[0] += f_imp_x / b.rb.mass
            b.rb.velocity[1] += f_imp_y / b.rb.mass






def physics_engine(delta, shapes):
    # 1. Apply Forces & Move
    for shape in shapes:
        cal_gravity(shape)
        integrate(shape, delta)
        
        # Damping (Air resistance)
        shape.rb.velocity[0] *= 0.99
        shape.rb.velocity[1] *= 0.99

    # 2. Iterative Collision Solver (Run this 4 to 8 times per frame)
    # More iterations = Stiffer/More solid objects. Less = Mushy.
    solver_iterations = 4 
    
    for _ in range(solver_iterations):
        # Optimization: Re-build grid only once if objects don't move fast, 
        # but for accuracy we iterate the pairs.
        
        # Note: If you have many objects, move build_spatial_grid outside this loop
        # and just iterate the pairs. For < 50 objects, rebuilding is fine.
        grid = build_spatial_grid(shapes)
        
        processed_pairs = set() # To avoid double checking A-B and B-A

        for cell in grid.values():
            # Check objects in same cell
            for i in range(len(cell)):
                for j in range(i + 1, len(cell)):
                    a, b = cell[i], cell[j]
                    
                    # Create unique ID for pair to avoid duplicates in neighbor checks
                    pair_id = tuple(sorted((id(a), id(b))))
                    if pair_id in processed_pairs: continue
                    processed_pairs.add(pair_id)

                    if a.rb.isStatic and b.rb.isStatic: continue

                    collided, normal, penetration = check_collision(a,b)#sat_collision(a, b)
                    if collided:
                        resolve_collision(a, b, normal, penetration)



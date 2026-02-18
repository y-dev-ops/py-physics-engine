import math
# ok im lost here, AI helped a lot in here, i guess phy is non-sense to me when I added rotaion
pixels_to_meter = 100
def integrate(shape, delta):
    if shape.rb.isStatic:
        return

    # 1. Linear Movement (Existing)
    ax = shape.rb.force[0] * pixels_to_meter / shape.rb.mass
    ay = shape.rb.force[1] * pixels_to_meter / shape.rb.mass
    
    shape.rb.velocity[0] += ax * delta
    shape.rb.velocity[1] += ay * delta

    # DAMPING (The "Motor" Fix)
    # 0.98 means it loses 2% of its spin every frame
    shape.rb.velocity[0] *= 0.99
    shape.rb.velocity[1] *= 0.99

    # --- Angular Integration (ONLY ONCE) ---
    if not shape.rb.isStatic and shape.rb.inv_inertia > 0:
        alpha = shape.rb.torque * shape.rb.inv_inertia
        shape.rb.angular_velocity += alpha * delta
        shape.rb.angular_velocity *= 0.95 # Apply angular damping here

        angle_delta_rad = shape.rb.angular_velocity * delta
        shape.angle += math.degrees(angle_delta_rad)

    # --- Update Position and Visuals ---
    # This must happen AFTER angular changes so the rotation is applied correctly.
    new_x = shape.x + shape.rb.velocity[0] * delta
    new_y = shape.y + shape.rb.velocity[1] * delta
    shape.position(new_x, new_y) # This updates center and calls update_world_points()


    # Reset Forces
    shape.rb.force = [0,0]
    shape.rb.torque = 0

def cal_gravity(shape, g=9.8):
    if shape.rb.isStatic:
        return
    if (not shape.rb.gravity):
        return
    #F=mg
    shape.rb.apply_force([0, shape.rb.mass * g])




# --- trying to do SAT ----

def get_axes(points):
    axes = []
    # Check ALL edges, not just the first two
    for i in range(0, len(points), 2): 
        x1, y1 = points[i], points[i+1]
        x2, y2 = points[(i+2) % len(points)], points[(i+3) % len(points)]
        
        dx, dy = x2 - x1, y2 - y1
        # Normal is (-dy, dx)
        length = math.hypot(dx, dy)
        if length > 0:
            axes.append((-dy / length, dx / length))
    return axes

def project(points, axis):
    #Project points onto axis and return (min, max).
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


# fixed, added rotation and some shit, to do next: add ang vel :(

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


#other cond

def circle_circle_collision(a, b):
    dx = a.x - b.x
    dy = a.y - b.y
    r = a.radius + b.radius
    return dx*dx + dy*dy < r*r

def check_collision(a, b):
    if a.type == "circle" and b.type == "circle": #circle with circle
        return circle_circle_collision(a, b)

    if a.type != "circle" and b.type == "circle":# not with circle
        return sat_circle_poly(b, a)

    if a.type == "circle" and b.type != "circle": # circle with not
        # SAT returns Normal(Poly -> Circle), which is (B -> A).
        # Resolve expects (A -> B).
        # We MUST FLIP the normal.
        collided, normal, penetration = sat_circle_poly(a, b)
        return collided, (-normal[0], -normal[1]), penetration
        
    if a.type != "circle" and b.type != "circle": #not circle with not circle
        return sat_collision(a, b)
    
    return False, (0,0), 0 # unkown, i dont know what could get u this


def cross_product_2d(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def is_point_inside(x, y, shape):
    if shape.type == "circle":
        dx = x - shape.x
        dy = y - shape.y
        return dx*dx + dy*dy <= shape.radius**2
    elif shape.type == "rectangle":
        axes = get_axes(shape.points)
        for axis in axes:
            p = x * axis[0] + y * axis[1]
            min_s, max_s = project(shape.points, axis)
            # Allow a tiny bit of error
            if p < min_s - 0.1 or p > max_s + 0.1:
                return False
        return True
    elif shape.type == "triangle":
        axes = get_axes(shape.points)
        for axis in axes:
            p = x * axis[0] + y * axis[1]
            min_s, max_s = project(shape.points, axis)
            # Allow a tiny bit of error
            if p < min_s - 0.1 or p > max_s + 0.1:
                return False
        return True
    return False

def resolve_collision(a, b, normal, penetration):
    if (a.rb.ingore_static and b.rb.isStatic) or (b.rb.ingore_static and a.rb.isStatic):
        return

    nx, ny = normal

    # --- 1. Find Contact Point (Manifold Heuristic) ---
    def get_support_point(shape, nx, ny):
        if shape.type == "circle":
            return shape.x + nx * shape.radius, shape.y + ny * shape.radius
        
        # Find max depth
        max_dist = -float('inf')
        for i in range(0, len(shape.points), 2):
            d = shape.points[i] * nx + shape.points[i+1] * ny
            if d > max_dist: max_dist = d
            
        # Collect close vertices (within 1 pixel) to average them
        # This reduces jitter on flat surfaces
        best_points = []
        epsilon = 1.0
        for i in range(0, len(shape.points), 2):
            px, py = shape.points[i], shape.points[i+1]
            d = px * nx + py * ny
            if d >= max_dist - epsilon:
                best_points.append((px, py))
                
        if not best_points: return shape.x, shape.y
        return sum(p[0] for p in best_points)/len(best_points), \
               sum(p[1] for p in best_points)/len(best_points)

    cp_a = get_support_point(a, nx, ny)
    cp_b = get_support_point(b, -nx, -ny)
    
    # Determine which point is the actual contact (Ledge Fix)
    # We prefer the point that is physically inside the other shape
    a_in_b = is_point_inside(cp_a[0], cp_a[1], b)
    b_in_a = is_point_inside(cp_b[0], cp_b[1], a)
    
    if b_in_a and not a_in_b:
        contact_x, contact_y = cp_b
    elif a_in_b and not b_in_a:
        contact_x, contact_y = cp_a
    else:
        # Both in or both out (flat stacking) -> Average
        contact_x = (cp_a[0] + cp_b[0]) / 2
        contact_y = (cp_a[1] + cp_b[1]) / 2

    # Lever arms
    ra_x, ra_y = contact_x - a.x, contact_y - a.y
    rb_x, rb_y = contact_x - b.x, contact_y - b.y

    # --- 2. Velocity at Contact Point ---
    vap_x = a.rb.velocity[0] - a.rb.angular_velocity * ra_y
    vap_y = a.rb.velocity[1] + a.rb.angular_velocity * ra_x
    vbp_x = b.rb.velocity[0] - b.rb.angular_velocity * rb_y
    vbp_y = b.rb.velocity[1] + b.rb.angular_velocity * rb_x

    rel_vel_x = vbp_x - vap_x
    rel_vel_y = vbp_y - vap_y
    vel_along_normal = rel_vel_x * nx + rel_vel_y * ny

    if vel_along_normal > 0: return # Moving apart

    # --- 3. Impulse Calculation ---
    e = min(a.rb.bounciness, b.rb.bounciness)
    ra_cross_n = ra_x * ny - ra_y * nx
    rb_cross_n = rb_x * ny - rb_y * nx
    
    inv_mass_a = 1/a.rb.mass if not a.rb.isStatic else 0
    inv_mass_b = 1/b.rb.mass if not b.rb.isStatic else 0

    denom = inv_mass_a + inv_mass_b + \
            (ra_cross_n**2 * a.rb.inv_inertia) + \
            (rb_cross_n**2 * b.rb.inv_inertia)

    j = -(1 + e) * vel_along_normal / denom

    # --- 4. Apply Impulse ---
    impulse_x, impulse_y = j * nx, j * ny

    # --- Friction Impulse (Tangential) ---
    tx, ty = -ny, nx
    vt = rel_vel_x * tx + rel_vel_y * ty
    jt = -vt / denom # Friction impulse magnitude
    
    mu = (a.rb.friction + b.rb.friction) * 0.5
    
    # Clamp friction (Coulomb)
    max_j = abs(j) * mu
    jt = max(-max_j, min(jt, max_j))
    
    impulse_tx, impulse_ty = jt * tx, jt * ty

    # Apply Total Impulse (Normal + Friction)
    if not a.rb.isStatic:
        a.rb.velocity[0] -= (impulse_x + impulse_tx) * inv_mass_a
        a.rb.velocity[1] -= (impulse_y + impulse_ty) * inv_mass_a
        a.rb.angular_velocity -= ((ra_x * impulse_y - ra_y * impulse_x) + (ra_x * impulse_ty - ra_y * impulse_tx)) * a.rb.inv_inertia

    if not b.rb.isStatic:
        b.rb.velocity[0] += (impulse_x + impulse_tx) * inv_mass_b
        b.rb.velocity[1] += (impulse_y + impulse_ty) * inv_mass_b
        b.rb.angular_velocity += ((rb_x * impulse_y - rb_y * impulse_x) + (rb_x * impulse_ty - rb_y * impulse_tx)) * b.rb.inv_inertia

    # --- 5. Corrected Positional Correction ---
    percent = 0.2 # Lower this to 0.2 for stability
    slop = 0.01
    total_inv_mass = inv_mass_a + inv_mass_b
    if total_inv_mass == 0: return

    correction_mag = max(penetration - slop, 0.0) / total_inv_mass * percent
    if not a.rb.isStatic:
        a.position(a.x - nx * correction_mag * inv_mass_a, a.y - ny * correction_mag * inv_mass_a)
    if not b.rb.isStatic:
        b.position(b.x + nx * correction_mag * inv_mass_b, b.y + ny * correction_mag * inv_mass_b)







def physics_engine(delta, shapes):
    # 1. Apply Forces & Move
    for shape in shapes:
        cal_gravity(shape)
        integrate(shape, delta)

    # 2. Iterative Collision Solver (Run this 4 to 8 times per frame)
    # More iterations = Stiffer/More solid objects. Less = Mushy.
    solver_iterations = 8
    grid = build_spatial_grid(shapes)
    
    for _ in range(solver_iterations):
        # Optimization: Re-build grid only once if objects don't move fast, 
        # but for accuracy we iterate the pairs.
        
        # Note: If you have many objects, move build_spatial_grid outside this loop
        # and just iterate the pairs. For < 50 objects, rebuilding is fine.
        
        
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

                    collided, normal, penetration = check_collision(a,b)# check type of col
                    if collided:
                        resolve_collision(a, b, normal, penetration)

import math
pixels_to_meter = 100
def integrate(shape, delta):
    if shape.rb.isStatic:
        return

    # 1) Linear Movement
    ax = shape.rb.force[0] * pixels_to_meter / shape.rb.mass
    ay = shape.rb.force[1] * pixels_to_meter / shape.rb.mass
    
    shape.rb.velocity[0] += ax * delta
    shape.rb.velocity[1] += ay * delta

    # 2) DAMPING
    shape.rb.velocity[0] *= 0.99
    shape.rb.velocity[1] *= 0.99

    # 3) Angular Integration
    if not shape.rb.isStatic and shape.rb.inv_inertia > 0:
        alpha = shape.rb.torque * shape.rb.inv_inertia
        shape.rb.angular_velocity += alpha * delta
        shape.rb.angular_velocity *= 0.95 # angular damping

        angle_delta_rad = shape.rb.angular_velocity * delta
        shape.angle += math.degrees(angle_delta_rad)

    # 4) Update Position and Visuals
    new_x = shape.x + shape.rb.velocity[0] * delta
    new_y = shape.y + shape.rb.velocity[1] * delta
    shape.position(new_x, new_y)


    # 5) Reset Forces
    shape.rb.force = [0,0]
    shape.rb.torque = 0

def cal_gravity(shape, g=9.8):
    if shape.rb.isStatic:
        return
    if (not shape.rb.gravity):
        return
    #F=mg
    shape.rb.apply_force([0, shape.rb.mass * g])

# --- SAT ----

def get_axes(points):
    axes = []
    # Check ALL edges
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
    #Project points into axis and return (min, max).
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

CELL_SIZE = 100  # in pixels

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

def sat_circle_poly(circle, poly):
    # 1) Edge Normals (standard SAT)
    axes = get_axes(poly.points)
    
    # 2) Closest Vertex Axis
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
        # If center is exactly on vertex, pick an arbitrary axis
        # or just skip to avoid Div/0 error.
        pass

    # 3) SAT Loop
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

    # 4) Enforce Normal Direction: Poly to Circle
    # We use the vector from Poly Center to Circle Center
    center_dx = circle.x - poly.x
    center_dy = circle.y - poly.y
    
    if (center_dx * smallest_axis[0] + center_dy * smallest_axis[1]) < 0:
        smallest_axis = (-smallest_axis[0], -smallest_axis[1])

    return True, smallest_axis, min_overlap

def circle_circle_collision(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    dist_sq = dx*dx + dy*dy
    r_sum = a.radius + b.radius
    
    collided = dist_sq < r_sum * r_sum
    if not collided:
        return False, (0,0), 0
        
    dist = math.sqrt(dist_sq) if dist_sq > 0 else 0
    penetration = r_sum - dist
    
    if dist > 0:
        normal = (dx / dist, dy / dist)
    else: # circles are exactly on top of each other
        normal = (0, 1) # push up
        
    return True, normal, penetration

def check_collision(a, b):
    # Circle vs Circle
    if a.type == "circle" and b.type == "circle":
        return circle_circle_collision(a, b)

    # Polygon vs Circle (order matters for normal direction)
    if a.type != "circle" and b.type == "circle":
        return sat_circle_poly(b, a) # Normal from Poly(a) to Circle(b) is correct.

    if a.type == "circle" and b.type != "circle":
        collided, normal, penetration = sat_circle_poly(a, b)
        return collided, (-normal[0], -normal[1]), penetration # Must flip normal.
        
    # Polygon vs Polygon
    if a.type != "circle" and b.type != "circle":
        return sat_collision(a, b)
    
    return False, (0,0), 0 # Should not be reached


def cross_product_2d(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def is_point_inside(x, y, shape):
    if shape.type == "circle":
        dx = x - shape.x
        dy = y - shape.y
        return dx*dx + dy*dy <= shape.radius**2
    elif shape.type != "circle":
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

    # 1) Find Contact Point (Manifold Heuristic)
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
    # prefer the point that is physically inside the other shape
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

    # 2) Velocity at Contact Point
    vap_x = a.rb.velocity[0] - a.rb.angular_velocity * ra_y
    vap_y = a.rb.velocity[1] + a.rb.angular_velocity * ra_x
    vbp_x = b.rb.velocity[0] - b.rb.angular_velocity * rb_y
    vbp_y = b.rb.velocity[1] + b.rb.angular_velocity * rb_x

    rel_vel_x = vbp_x - vap_x
    rel_vel_y = vbp_y - vap_y
    vel_along_normal = rel_vel_x * nx + rel_vel_y * ny

    if vel_along_normal > 0: return # Moving apart

    # 3) Impulse Calculation
    e = max(a.rb.bounciness, b.rb.bounciness)
    
    # STABILIZATION: If relative velocity is low (resting contact), don't bounce.
    # Threshold covers roughly 2-3 frames of gravity (approx 40-50 px/s).
    if e < 1.0 and abs(vel_along_normal) < 50:
        e = 0.0

    ra_cross_n = ra_x * ny - ra_y * nx
    rb_cross_n = rb_x * ny - rb_y * nx
    
    inv_mass_a = 1/a.rb.mass if not a.rb.isStatic else 0
    inv_mass_b = 1/b.rb.mass if not b.rb.isStatic else 0

    denom = inv_mass_a + inv_mass_b + \
            (ra_cross_n**2 * a.rb.inv_inertia) + \
            (rb_cross_n**2 * b.rb.inv_inertia)

    j = -(1 + e) * vel_along_normal / denom

    # 4) Apply Impulse
    impulse_x, impulse_y = j * nx, j * ny

    # Friction Impulse (Tangential)
    tx, ty = -ny, nx
    
    ra_cross_t = ra_x * ty - ra_y * tx
    rb_cross_t = rb_x * ty - rb_y * tx
    
    denom_t = inv_mass_a + inv_mass_b + \
            (ra_cross_t**2 * a.rb.inv_inertia) + \
            (rb_cross_t**2 * b.rb.inv_inertia)

    vt = rel_vel_x * tx + rel_vel_y * ty
    jt = -vt / denom_t # Friction impulse magnitude
    
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

    # 5) Corrected Positional Correction
    percent = 0.2 # 0.2 for stability
    slop = 0.01
    total_inv_mass = inv_mass_a + inv_mass_b
    if total_inv_mass == 0: return

    correction_mag = max(penetration - slop, 0.0) / total_inv_mass * percent
    if not a.rb.isStatic:
        a.position(a.x - nx * correction_mag * inv_mass_a, a.y - ny * correction_mag * inv_mass_a)
    if not b.rb.isStatic:
        b.position(b.x + nx * correction_mag * inv_mass_b, b.y + ny * correction_mag * inv_mass_b)







def physics_engine(delta, shapes):
    # 1) Apply forces and integrate positions
    for shape in shapes:
        cal_gravity(shape)
        integrate(shape, delta)

    # 2) Broadphase: Find all potential collision pairs using a spatial grid
    grid = build_spatial_grid(shapes)
    pairs = []
    processed_pairs = set()

    for cell in grid.values():
        for i in range(len(cell)):
            for j in range(i + 1, len(cell)):
                a, b = cell[i], cell[j]
                
                pair_id = tuple(sorted((id(a), id(b))))
                if pair_id in processed_pairs:
                    continue
                
                if a.rb.isStatic and b.rb.isStatic:
                    continue
                
                # AABB check as a cheap pre-filter before adding to pair list
                ax1, ay1, ax2, ay2 = a.get_aabb()
                bx1, by1, bx2, by2 = b.get_aabb()
                if ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1:
                    pairs.append((a, b))
                    processed_pairs.add(pair_id)

    # 3) Narrowphase & Solver: Iterate multiple times to stabilize contacts
    solver_iterations = 8
    for _ in range(solver_iterations):
        for a, b in pairs:
            collided, normal, penetration = check_collision(a, b)
            if collided:
                resolve_collision(a, b, normal, penetration)

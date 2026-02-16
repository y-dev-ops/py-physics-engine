class rigidbody:
    def __init__(self, mass=1.0, velocity=None, isStatic=True):
        self.mass = mass
        self.velocity = velocity if velocity is not None else [0.0, 0.0]
        self.force = [0, 0] #for x and y
        self.isStatic = isStatic

    def apply_force(self, f):
        self.force[0] += f[0]
        self.force[1] += f[1]




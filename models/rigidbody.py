class rigidbody: # here we handle physics
    def __init__(self, mass=1.0, velocity=None, isStatic=True, friction=0.4, static_friction=0.6, gravity=True, bounciness=0.6):
        self.mass = mass
        self.velocity = velocity if velocity is not None else [0.0, 0.0]
        self.force = [0, 0] #for x and y
        self.isStatic = isStatic
        #self.friction = friction
        self.static_friction = static_friction 
        self.friction = friction
        self.gravity = gravity
        self.ingore_static = False
        self.bounciness = bounciness

        if (static_friction < friction):
            self.static_friction = friction+0.1
            print(f'your static friction is less than dynamic friction, \nAUTOFIX:static friction set to: {self.static_friction} \n next time go learn physics kid ;)')


    def apply_force(self, f):
        self.force[0] += f[0]
        self.force[1] += f[1]




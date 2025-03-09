from vpython import *
import random

# Set up the 3D scene
scene = canvas(title='Flocking Birds Simulation')

# Constants
num_birds = 50
max_speed = 0.1
max_force = 0.01
neighborhood_radius = 2.5

# Boid class for flocking behavior
class Boid:
    def __init__(self):
        self.position = vector(random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5))
        self.velocity = norm(vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * max_speed
        self.acceleration = vector(0, 0, 0)
        self.bird_object = cone(pos=self.position, axis=self.velocity * 0.5, radius=0.2, color=color.cyan)

    def apply_force(self, force):
        self.acceleration += force

    def update(self):
        self.velocity += self.acceleration
        # Limit speed
        if mag(self.velocity) > max_speed:
            self.velocity = norm(self.velocity) * max_speed
        self.position += self.velocity
        self.bird_object.pos = self.position
        self.bird_object.axis = norm(self.velocity) * 0.5  # Update axis to match direction
        self.acceleration = vector(0, 0, 0)

    def edges(self):
        # Wrap around edges
        if self.position.x < -5: self.position.x = 5
        if self.position.x > 5: self.position.x = -5
        if self.position.y < -5: self.position.y = 5
        if self.position.y > 5: self.position.y = -5
        if self.position.z < -5: self.position.z = 5
        if self.position.z > 5: self.position.z = -5

    def flock(self, boids):
        separation = self.separate(boids)
        alignment = self.align(boids)
        cohesion = self.cohere(boids)

        self.apply_force(separation)
        self.apply_force(alignment)
        self.apply_force(cohesion)

    def separate(self, boids):
        steering = vector(0, 0, 0)
        total = 0
        for bird in boids:
            distance = mag(self.position - bird.position)
            if neighborhood_radius > distance > 0:
                diff = normalize(self.position - bird.position) / distance
                steering += diff
                total += 1
        if total > 0:
            steering /= total
        if mag(steering) > 0:
            steering = normalize(steering) * max_speed
            steering -= self.velocity
            if mag(steering) > max_force:
                steering = normalize(steering) * max_force
        return steering

    def align(self, boids):
        steering = vector(0, 0, 0)
        total = 0
        for bird in boids:
            distance = mag(self.position - bird.position)
            if distance < neighborhood_radius:
                steering += bird.velocity
                total += 1
        if total > 0:
            steering /= total
            steering = normalize(steering) * max_speed
            steering -= self.velocity
            if mag(steering) > max_force:
                steering = normalize(steering) * max_force
        return steering

    def cohere(self, boids):
        steering = vector(0, 0, 0)
        total = 0
        for bird in boids:
            distance = mag(self.position - bird.position)
            if distance < neighborhood_radius:
                steering += bird.position
                total += 1
        if total > 0:
            steering /= total
            steering -= self.position
            steering = normalize(steering) * max_speed
            steering -= self.velocity
            if mag(steering) > max_force:
                steering = normalize(steering) * max_force
        return steering

# Function to normalize a vector
def normalize(v):
    mag_v = mag(v)
    if mag_v > 0:
        return v / mag_v
    return vector(0, 0, 0)

# Create boids
boids = [Boid() for _ in range(num_birds)]

# Animation loop
while True:
    rate(60)
    for boid in boids:
        boid.flock(boids)
        boid.update()
        boid.edges()

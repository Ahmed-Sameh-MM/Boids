from vpython import *
import random

from constants import *

# Set up the 3D scene
scene = canvas(
    title='Flocking Birds Simulation',
    width=1000,
    height=600,
)

# Boid class for flocking behavior
class Boid:
    def __init__(self):
        self.position = vector(random.uniform(NEGATIVE_LIMIT, POSITIVE_LIMIT), random.uniform(NEGATIVE_LIMIT, POSITIVE_LIMIT), random.uniform(NEGATIVE_LIMIT, POSITIVE_LIMIT))
        self.velocity = norm(vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * MAX_SPEED
        self.acceleration = vector(0, 0, 0)
        self.bird_object = cone(pos=self.position, axis=self.velocity * 0.5, radius=0.2, color=color.cyan)

    def apply_force(self, force):
        self.acceleration += force

    def update(self):
        self.velocity += self.acceleration
        # Limit speed
        if mag(self.velocity) > MAX_SPEED:
            self.velocity = norm(self.velocity) * MAX_SPEED
        self.position += self.velocity
        self.bird_object.pos = self.position
        self.bird_object.axis = norm(self.velocity) * 0.5  # Update axis to match direction
        self.acceleration = vector(0, 0, 0)

    def edges(self):
        # Wrap around edges
        if self.position.x < NEGATIVE_LIMIT: self.position.x = POSITIVE_LIMIT
        if self.position.x > POSITIVE_LIMIT: self.position.x = NEGATIVE_LIMIT

        if self.position.y < NEGATIVE_LIMIT: self.position.y = POSITIVE_LIMIT
        if self.position.y > POSITIVE_LIMIT: self.position.y = NEGATIVE_LIMIT

        if self.position.z < NEGATIVE_LIMIT: self.position.z = POSITIVE_LIMIT
        if self.position.z > POSITIVE_LIMIT: self.position.z = NEGATIVE_LIMIT

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
            if NEIGHBOURHOOD_RADIUS > distance > 0:
                diff = normalize(self.position - bird.position) / distance
                steering += diff
                total += 1

        if total > 0:
            steering /= total

        if mag(steering) > 0:
            steering = normalize(steering) * MAX_SPEED
            steering -= self.velocity

            if mag(steering) > MAX_FORCE:
                steering = normalize(steering) * MAX_FORCE

        return steering

    def align(self, boids):
        steering = vector(0, 0, 0)
        total = 0

        for bird in boids:
            distance = mag(self.position - bird.position)
            if distance < NEIGHBOURHOOD_RADIUS:
                steering += bird.velocity
                total += 1

        if total > 0:
            steering /= total
            steering = normalize(steering) * MAX_SPEED
            steering -= self.velocity

            if mag(steering) > MAX_FORCE:
                steering = normalize(steering) * MAX_FORCE

        return steering

    def cohere(self, boids):
        steering = vector(0, 0, 0)
        total = 0

        for bird in boids:
            distance = mag(self.position - bird.position)
            if distance < NEIGHBOURHOOD_RADIUS:
                steering += bird.position
                total += 1

        if total > 0:
            steering /= total
            steering -= self.position
            steering = normalize(steering) * MAX_SPEED
            steering -= self.velocity

            if mag(steering) > MAX_FORCE:
                steering = normalize(steering) * MAX_FORCE

        return steering

# Function to normalize a vector
def normalize(v):
    mag_v = mag(v)

    if mag_v > 0:
        return v / mag_v

    return vector(0, 0, 0)

# Create boids
boids = [Boid() for _ in range(NUM_BOIDS)]

# Coordinates of the cube's corners
vertices = [
    vector(POSITIVE_LIMIT, POSITIVE_LIMIT, POSITIVE_LIMIT), vector(POSITIVE_LIMIT, POSITIVE_LIMIT, NEGATIVE_LIMIT),
    vector(POSITIVE_LIMIT, NEGATIVE_LIMIT, POSITIVE_LIMIT), vector(POSITIVE_LIMIT, NEGATIVE_LIMIT, NEGATIVE_LIMIT),
    vector(NEGATIVE_LIMIT, POSITIVE_LIMIT, POSITIVE_LIMIT), vector(NEGATIVE_LIMIT, POSITIVE_LIMIT, NEGATIVE_LIMIT),
    vector(NEGATIVE_LIMIT, NEGATIVE_LIMIT, POSITIVE_LIMIT), vector(NEGATIVE_LIMIT, NEGATIVE_LIMIT, NEGATIVE_LIMIT)
]

# Draw lines around the cube by connecting the vertices
edges = [
    (0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6),
    (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)
]

# Create lines with red color
for edge in edges:
    curve(pos=[vertices[edge[0]], vertices[edge[1]]], radius=0.1, color=color.red)

# Animation loop
while True:
    rate(60)
    for boid in boids:
        boid.flock(boids)
        boid.update()
        boid.edges()

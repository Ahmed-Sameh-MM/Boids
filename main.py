from vpython import *
import random

from constants import *
from genetic_algorithm import GeneticAlgorithm, FlockParameters

# Set up the 3D scene
scene = canvas(
    title='Flocking Birds Simulation',
    width=1000,
    height=600,
)

# Boid class for flocking behavior
class Boid:
    def __init__(self, parameters=None):
        self.position = vector(random.uniform(NEGATIVE_LIMIT, POSITIVE_LIMIT), random.uniform(NEGATIVE_LIMIT, POSITIVE_LIMIT), random.uniform(NEGATIVE_LIMIT, POSITIVE_LIMIT))
        self.velocity = norm(vector(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))) * MAX_SPEED
        self.acceleration = vector(0, 0, 0)
        self.bird_object = cone(pos=self.position, axis=self.velocity * 0.5, radius=0.2, color=color.cyan)
        self.parameters = parameters or FlockParameters()

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

        self.apply_force(separation * self.parameters.separation_weight)
        self.apply_force(alignment * self.parameters.alignment_weight)
        self.apply_force(cohesion * self.parameters.cohesion_weight)

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

# Initialize the genetic algorithm
ga = GeneticAlgorithm(population_size=10)

# Create boids with initial parameters
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

# Add text display for generation and best fitness
generation_text = label(pos=vector(0, POSITIVE_LIMIT + 1, 0), text="Generation: 0", height=16, color=color.white)
fitness_text = label(pos=vector(0, POSITIVE_LIMIT + 2, 0), text="Best Fitness: 0", height=16, color=color.white)

# Animation loop
frame_count = 0
while True:
    rate(60)
    
    # Update boids
    for boid in boids:
        boid.flock(boids)
        boid.update()
        boid.edges()
    
    # Evolve every 120 frames
    if frame_count % 120 == 0:
        best_params = ga.evolve(boids)
        # Update all boids with the best parameters
        for boid in boids:
            boid.parameters = best_params
        
        # Update display
        generation_text.text = f"Generation: {ga.generation}"
        fitness_text.text = f"Best Fitness: {ga.best_fitness:.3f}"
        
        # Stop after 150 generations
        if ga.generation >= 150:
            print("Simulation completed after 150 generations!")
            break
    
    frame_count += 1

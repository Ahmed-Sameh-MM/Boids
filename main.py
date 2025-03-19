from vpython import vector, color, canvas, label, curve, rate
from boid import Boid

from constants import *
from genetic_algorithm import GeneticAlgorithm

# Set up the 3D scene
scene = canvas(
    title='Flocking Birds Simulation',
    width=1000,
    height=600,
)

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
            print(f"Best Fitness Gained: {round(ga.best_fitness, 3)}")
            print(f"Best Weights: ({best_params.__str__()})")
            break
    
    frame_count += 1

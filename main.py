from vpython import vector, color, canvas, label, curve, rate
from boid import Boid
import matplotlib.pyplot as plt

from constants import *
from genetic_algorithm import GeneticAlgorithm

# Lists to store history for plotting
fitness_history = []
separation_weights = []
alignment_weights = []
cohesion_weights = []
energy_weights = []

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

# Coordinates of the cuboid's corners
vertices = [
    vector(POSITIVE_LIMIT, POSITIVE_Y_LIMIT, POSITIVE_Z_LIMIT),    # Front top right
    vector(POSITIVE_LIMIT, POSITIVE_Y_LIMIT, NEGATIVE_Z_LIMIT),    # Front top left
    vector(POSITIVE_LIMIT, NEGATIVE_Y_LIMIT, POSITIVE_Z_LIMIT),    # Front bottom right
    vector(POSITIVE_LIMIT, NEGATIVE_Y_LIMIT, NEGATIVE_Z_LIMIT),    # Front bottom left
    vector(NEGATIVE_LIMIT, POSITIVE_Y_LIMIT, POSITIVE_Z_LIMIT),    # Back top right
    vector(NEGATIVE_LIMIT, POSITIVE_Y_LIMIT, NEGATIVE_Z_LIMIT),    # Back top left
    vector(NEGATIVE_LIMIT, NEGATIVE_Y_LIMIT, POSITIVE_Z_LIMIT),    # Back bottom right
    vector(NEGATIVE_LIMIT, NEGATIVE_Y_LIMIT, NEGATIVE_Z_LIMIT)     # Back bottom left
]

# Draw lines around the cuboid by connecting the vertices
edges = [
    # Front face
    (0, 1), (1, 3), (3, 2), (2, 0),
    # Back face
    (4, 5), (5, 7), (7, 6), (6, 4),
    # Connecting edges
    (0, 4), (1, 5), (2, 6), (3, 7)
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
    
    # Evolve every 60 frames
    if frame_count % 60 == 0:
        best_params = ga.evolve(boids)
        # Update all boids with the best parameters
        for boid in boids:
            boid.parameters = best_params
        
        # Store history for plotting
        fitness_history.append(ga.best_fitness)
        separation_weights.append(best_params.separation_weight)
        alignment_weights.append(best_params.alignment_weight)
        cohesion_weights.append(best_params.cohesion_weight)
        energy_weights.append(best_params.energy_weight)
        
        # Update display
        generation_text.text = f"Generation: {ga.generation}"
        fitness_text.text = f"Best Fitness: {ga.best_fitness:.3f}"
        
        # Stop after 150 generations
        if ga.generation == 150:
            print("Simulation completed after 150 generations!")
            print(f"Best Fitness Gained: {round(ga.best_fitness, 3)}")
            print(f"Best Weights: ({best_params.__str__()})")
            
            # Create first plot: Fitness over generations
            plt.figure(figsize=(8, 6))
            plt.plot(fitness_history)
            plt.title('Fitness Over Generations')
            plt.xlabel('Generation')
            plt.ylabel('Fitness')
            plt.grid(True)
            plt.show()
            
            # Create second plot: Weights over generations
            plt.figure(figsize=(8, 6))
            plt.plot(separation_weights, label='Separation')
            plt.plot(alignment_weights, label='Alignment')
            plt.plot(cohesion_weights, label='Cohesion')
            plt.plot(energy_weights, label='Energy')
            plt.title('Parameter Weights Over Generations')
            plt.xlabel('Generation')
            plt.ylabel('Weight Value')
            plt.legend()
            plt.grid(True)
            plt.show()
            break
    
    frame_count += 1

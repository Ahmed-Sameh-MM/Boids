import random
from vpython import vector, mag, norm

class FlockParameters:
    def __init__(self, separation_weight=1.0, alignment_weight=1.0, cohesion_weight=1.0, energy_weight=0.2):
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.cohesion_weight = cohesion_weight
        self.energy_weight = energy_weight

    def mutate(self):
        mutation_rate = 0.1
        
        return FlockParameters(
            separation_weight=self.separation_weight + random.uniform(-mutation_rate, mutation_rate),
            alignment_weight=self.alignment_weight + random.uniform(-mutation_rate, mutation_rate),
            cohesion_weight=self.cohesion_weight + random.uniform(-mutation_rate, mutation_rate),
            energy_weight=self.energy_weight + random.uniform(-mutation_rate, mutation_rate)
        )

    @staticmethod
    def crossover(parent1, parent2):
        return FlockParameters(
            separation_weight=random.choice([parent1.separation_weight, parent2.separation_weight]),
            alignment_weight=random.choice([parent1.alignment_weight, parent2.alignment_weight]),
            cohesion_weight=random.choice([parent1.cohesion_weight, parent2.cohesion_weight]),
            energy_weight=random.choice([parent1.energy_weight, parent2.energy_weight])
        )

    def __str__(self):
        return f"Separation: {round(self.separation_weight, 3)}, Alignment: {round(self.alignment_weight, 3)}, Cohesion: {round(self.cohesion_weight, 3)}, Energy: {round(self.energy_weight, 3)}"

def calculate_fitness(boids, parameters):
    """
    Calculate the fitness of a flock based on four main parameters:
    1. Cohesion: How well the flock stays together
    2. Separation: How well the flock maintains safe distances
    3. Alignment: How well the flock moves in the same direction
    4. Energy: How efficiently the flock moves
    """
    if not boids:
        return 0

    # Calculate cohesion score (how close boids are to the center of mass)
    center_of_mass = vector(0, 0, 0)
    for boid in boids:
        center_of_mass += boid.position
    center_of_mass /= len(boids)
    
    cohesion_score = 0
    for boid in boids:
        cohesion_score += mag(boid.position - center_of_mass)
    cohesion_score = 1 / (1 + cohesion_score / len(boids))  # Normalize and invert

    # Calculate separation score (how well boids maintain safe distances)
    separation_score = 0
    min_safe_distance = 0.5  # Minimum safe distance between boids
    
    for boid in boids:
        min_distance = float('inf')
        for other in boids:
            if other != boid:
                distance = mag(boid.position - other.position)
                min_distance = min(min_distance, distance)
        
        # Penalize if boids are too close
        if min_distance < min_safe_distance:
            separation_score += min_distance / min_safe_distance  # Score between 0 and 1
        else:
            separation_score += 1.0  # Full score for maintaining safe distance
    
    separation_score = separation_score / len(boids)  # Average separation score

    # Calculate alignment score (how well boids move in the same direction)
    average_velocity = vector(0, 0, 0)
    for boid in boids:
        average_velocity += boid.velocity
    average_velocity = norm(average_velocity / len(boids))
    
    alignment_score = 0
    for boid in boids:
        alignment_score += mag(norm(boid.velocity) - average_velocity)
    alignment_score = 1 / (1 + alignment_score / len(boids))  # Normalize and invert

    # Calculate energy efficiency score
    energy_score = 0
    for boid in boids:
        # Less acceleration = higher score
        acc_magnitude = mag(boid.acceleration)
        # Using MAX_FORCE from the boid's parameters to normalize
        max_force = 0.01  # This should match MAX_FORCE from constants.py
        energy_score += 1 - (acc_magnitude / max_force)
    energy_score = max(0, energy_score / len(boids))  # Normalize to 0-1 range and ensure non-negative

    # Combine scores with weights
    total_fitness = (
        parameters.separation_weight * separation_score +
        parameters.alignment_weight * alignment_score +
        parameters.cohesion_weight * cohesion_score +
        parameters.energy_weight * energy_score
    )

    # Apply a gradual penalty based on separation score
    if separation_score < 0.8:  # If average separation is poor
        # Linear interpolation between 1.0 (at 0.8) and 0.7 (at 0.0)
        penalty = 0.7 + (separation_score / 0.8) * 0.4
        total_fitness *= penalty

    return total_fitness

class GeneticAlgorithm:
    def __init__(self, population_size=10):
        self.population_size = population_size
        self.population = [FlockParameters() for _ in range(population_size)]
        self.generation = 0
        self.best_fitness = 0
        self.best_parameters = None

    def evolve(self, boids, num_generations=1):
        for _ in range(num_generations):
            # Evaluate fitness for each set of parameters
            fitness_scores = [(calculate_fitness(boids, params), params) for params in self.population]
            # Sort based on fitness scores only (first element of each tuple)
            fitness_scores.sort(key=lambda x: x[0], reverse=True)
            
            # Update the best parameters if better ones were found
            if fitness_scores[0][0] > self.best_fitness:
                self.best_fitness = fitness_scores[0][0]
                self.best_parameters = fitness_scores[0][1]

            # Select top performers
            top_performers = [params for _, params in fitness_scores[:self.population_size // 2]]
            
            # Create new population through crossover and mutation
            new_population = top_performers.copy()
            while len(new_population) < self.population_size:
                parent1 = random.choice(top_performers)
                parent2 = random.choice(top_performers)
                child = FlockParameters.crossover(parent1, parent2)
                if random.random() < 0.1:  # 10% mutation rate
                    child = child.mutate()
                new_population.append(child)

            self.population = new_population
            self.generation += 1

        return self.best_parameters

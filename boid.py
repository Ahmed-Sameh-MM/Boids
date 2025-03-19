from vpython import vector, norm, cone, color, mag
import random

from genetic_algorithm import FlockParameters
from constants import *

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
                diff = self._normalize(self.position - bird.position) / distance
                steering += diff
                total += 1

        if total > 0:
            steering /= total

        if mag(steering) > 0:
            steering = self._normalize(steering) * MAX_SPEED
            steering -= self.velocity

            if mag(steering) > MAX_FORCE:
                steering = self._normalize(steering) * MAX_FORCE

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
            steering = self._normalize(steering) * MAX_SPEED
            steering -= self.velocity

            if mag(steering) > MAX_FORCE:
                steering = self._normalize(steering) * MAX_FORCE

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
            steering = self._normalize(steering) * MAX_SPEED
            steering -= self.velocity

            if mag(steering) > MAX_FORCE:
                steering = self._normalize(steering) * MAX_FORCE

        return steering

    # Function to normalize a vector
    @staticmethod
    def _normalize(v):
        mag_v = mag(v)

        if mag_v > 0:
            return v / mag_v

        return vector(0, 0, 0)
# Here I will do all the running of solutions
# Defining the problem instance to solve, getting the initial solution, getting the alns solution, ...

from resources.data import Data
from src.initial_solution import savings

problem_instance= Data().get_instance("C1_2_1.txt")
evaluation = "evaluation function for the cost"

initial_solution = savings(problem_instance, evaluation)
print(initial_solution)
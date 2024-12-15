# Here I will do all the running of solutions
# Defining the problem instance to solve, getting the initial solution, getting the alns solution, ...

from resources.data import Data
from src.helpers.plots import draw_routes
from src.initial_solution import savings_vrptw
from src.evaluation import EvaluateRoute

problem_instance= Data().get_instance("C1_2_1.txt")
evaluation = "evaluation function for the cost"

initial_solution = savings_vrptw(problem_instance)
print(initial_solution)

draw_routes(initial_solution)
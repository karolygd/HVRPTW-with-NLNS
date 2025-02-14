# This class dynamically sets the number of customers to remove, depending on the solution stagnation and improvement.
# If the iterations in a given period are leading to better solutions, the algorithm reduces the number of removed requests (intensification).
# If no significant improvement is observed, the algorithm increases the number of removed requests (diversification - exploration).
# This algorithm is based on:
# Qu, Y., & Bard, J. F. (2012). A GRASP with adaptive large neighborhood search for pickup and delivery problems with transshipment.
# Computers & Operations Research, 39(10), 2439–2456. https://doi.org/10.1016/j.cor.2011.11.016

class AdaptiveRemovalManager:
    def __init__(self, total_customers: int, m: int = 5, lambda_1: int = 10, lambda_2: int = 20):
        """
        :param total_customers (int): Total number of customers in the problem.
        :param m (int): Number of levels for removal size.
        :param lambda_1 (int): Threshold for stagnation before increasing mu.
        :param lambda_2 (int): Window size to check stagnation.
        """
        self.removal_sizes = [max(1, int((i / m) * 0.25 * total_customers)) for i in range(1, m + 1)]
        self.mu_a = self.removal_sizes[len(self.removal_sizes) // 2]  # Start at the middle value
        self.mu = self.mu_a
        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.no_improvement_counter = 0
        self.last_best_solution = None

    def update_mu(self, new_solution_cost, best_solution_cost, current_solution_cost):
        """
        Updates the removal size mu based on solution improvement or stagnation.

        Parameters:
        - current_solution_cost (float): The objective value of the current solution.
        - best_solution_cost (float): The objective value of the best-known solution.
        """
        if new_solution_cost < best_solution_cost:
            # ALNS starts with the average number μ=μa and once a better solution is found,
            # μ is reset to μ1 to intensify the local search.
            # If a new best solution is found, reset mu to the smallest value
            self.mu = self.removal_sizes[0]
            self.no_improvement_counter = 0
        elif new_solution_cost < current_solution_cost:
            #  If the solution uncovered at the current iteration is better than the incumbent,
            #  μ is reset to μa so long as μ>μa.
            self.mu = self.mu_a
        else:
            # Diversification mechanism: if the number of times all previous solutions are realized is λ1
            # in a predefined number of iterations (λ2), then μ is set to the next highest value.
            self.no_improvement_counter += 1
            if self.no_improvement_counter >= self.lambda_1 and self.no_improvement_counter % self.lambda_2 == 0:
                # Increase mu to the next level if stagnation occurs
                if self.mu < self.removal_sizes[-1]:  # Avoid exceeding max mu
                    self.mu = self.removal_sizes[self.removal_sizes.index(self.mu) + 1]

    def get_removal_size(self):
        """Returns the current value of mu (number of customers to remove)."""
        return self.mu

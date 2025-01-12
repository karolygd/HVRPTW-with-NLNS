import random

class AdaptiveLayer:
    def __init__(self, remove_operators, insert_operators):
        self.remove_operators = remove_operators
        self.insert_operators = insert_operators
        # initialize all operators with the same weight
        self.remove_weights = [1] * len(remove_operators)
        self.insert_weights = [1] * len(insert_operators)

    # might be useful for each segment in roulette wheel?
    def initialize_weights(self):
        for remove_operator in self.remove_operators:
            remove_operator.initialize()

        for insert_operator in self.insert_operators:
            insert_operator.initialize()

    def adapt_operator_weights(self):
        # need to do 2 loops because zip and zip_longest doesn't work for different sized lists
        # for i, remove_operator in enumerate(self.remove_operators):
        #     remove_operator.update_weight()
        #     self.remove_weights[i] = remove_operator.weight
        self.remove_weights = [op.update_weight() or op.weight for op in self.remove_operators]
        self.insert_weights = [op.update_weight() or op.weight for op in self.insert_operators]

    def random_selection(self):
        """
        Perform random operator selection.
        :return remove_operator, insert_operator: Selected remove and insert operator
        """
        remove_operator = random.choice(self.remove_operators)
        insert_operator = random.choice(self.insert_operators)
        return remove_operator, insert_operator

    def roulete_wheel(self):
        """
        Perform roulette wheel operator selection.
        :return remove_operator, insert_operator: Selected remove and insert operator
        """
        remove_operator = None
        insert_operator = None

        # calculate the cumulative probabilities of each operator
        total_weight_remove = sum(self.remove_weights)
        total_weight_insert = sum(self.insert_weights)
        remove_selection_probabilities = [w_r / total_weight_remove for w_r in self.remove_weights]
        insert_selection_probabilities = [w_i / total_weight_insert for w_i in self.insert_weights]
        print(f"list of remove weights: {self.remove_weights}, list of insert weights: {self.insert_weights}")

        cumulative_probabilities_remove = []
        cumulative_probabilities_insert = []
        cumulative_sum_remove = 0
        cumulative_sum_insert = 0
        for remove_prob in remove_selection_probabilities:
            cumulative_sum_remove += remove_prob
            cumulative_probabilities_remove.append(cumulative_sum_remove)

        for insert_prob in insert_selection_probabilities:
            cumulative_sum_insert += insert_prob
            cumulative_probabilities_insert.append(cumulative_sum_insert)

        # roulette wheel:
        r_remove = random.random()
        r_insert = random.random()
        for i, cumulative_prob_remove in enumerate(cumulative_probabilities_remove):
            if r_remove <= cumulative_prob_remove:
                remove_operator = self.remove_operators[i]
                print(f"i: {i}, r_remove = {r_remove}, cumulative_prob: {cumulative_probabilities_remove},  {remove_operator.name}")
                break

        for i, cumulative_prob_insert in enumerate(cumulative_probabilities_insert):
            if r_insert <= cumulative_prob_insert:
                insert_operator = self.insert_operators[i]
                print(f"i: {i}, r_insert = {r_insert}, cumulative_prob: {cumulative_probabilities_insert},  {insert_operator.name}")
                break

        return remove_operator, insert_operator


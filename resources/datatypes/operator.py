
class Operator:
    def __init__(self, func, name, **kwargs):
        self.func = func
        self.name = name
        self.kwargs = kwargs
        self.score: float = 0.0 # all operators start with the same initial weight
        self.frequency: int = 0
        self.weight: float = 1.0

    def __call__(self, solution):
        # When the operator is called, execute the stored function
        return self.func(solution, **self.kwargs)

    def initialize(self):
        self.score = 0.0
        self.frequency = 0

    def update_score(self, score:float = 0.0):
        self.score += score
        self.frequency += 1

    def update_weight(self, r: float = 0.5):
        """"
        :param r: reaction factor - controls how quickly the weight adjustment procedure reacts to changes in the effectiveness
                    of the heuristic: if r = 0 , the weights remain unchanged, and if r = 1 the weights are determined by the performance in the last segment
        """
        if self.frequency == 0: #not to incur in division by 0 in case operator is not used in the current segment
            self.weight = self.weight#*(1-r)
        else:
            self.weight = self.weight*(1-r) + r*(self.score/self.frequency)
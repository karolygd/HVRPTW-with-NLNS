import math

class SettingTemperature:
    def __init__(self, t_start:float, t_end:float, update_function:str, z:float, iterations:int):
        """
        :param t_start: defines the tolerance for worse solutions at the start of the algorithm, where a larger value leads to a more diversified search
        :param t_end:  sets the tolerance near the end, where a smaller value leads to a more greedy search
        :param update_function: function used to update the temperature value, can be "linear" or "exponential"
        :param z: reference value, in this case we use the initial solution
        """
        # self.h_start = h_start
        # self.h_end = h_end
        self.t_start = t_start
        self.t_end = t_end
        self.update_function = update_function
        self.z = z
        self.t = 0.0
        self.iterations = iterations

    def initial_temperature(self):
        # # accepting a worse solution (as much as h_start) with probability = 0.5
        # self.t_start = (self.z * (1 - self.h_start)) / math.log(0.5)
        self.t = self.t_start
        # #print("initial temperature start: ", self.t_start)
        return self.t_start

    def final_temperature(self):
        # self.t_end = (self.z * (1 - self.h_end)) / math.log(0.5)
        # #print("final temperature end: ", self.t_end)
        return self.t_end

    def update_temperature(self):
        if self.update_function == "linear":
            self.t = self.t - (self.t_start - self.t_end)/self.iterations
        elif self.update_function == "exponential":
            self.t = self.t * ((self.t_end/self.t_start)**(1/self.iterations))
        return round(self.t, 4)



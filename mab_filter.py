import numpy as np

class MultiArmBandits():
    def __init__(self, num_headlines, num_turns, lbound=0.01, ubound=0.15):
        self.num_headlines = num_headlines
        self.num_turns = num_turns
        self.num_conversions = np.zeros(self.num_headlines)
        self.num_fails = np.zeros(self.num_headlines)
        self.num_simul = np.zeros(self.num_headlines)
        self.conversion_rates = np.random.uniform(lbound, ubound, self.num_headlines)
        self.outcomes = np.zeros((self.num_turns, self.num_headlines))
        for turn_idx in range(self.num_turns):
            for headline_idx in range(self.num_headlines):
                if np.random.rand() <= self.conversion_rates[headline_idx]:
                    self.outcomes[turn_idx][headline_idx] = 1
    
    def simulation(self, verbose=False):
        for turn_idx in range(self.num_turns):
            headline_ = -1
            max_beta = -1

            for headline_idx in range(self.num_headlines):
                a = self.num_conversions[headline_idx] + 1
                b = self.num_fails[headline_idx] + 1
                random_beta = np.random.beta(a, b)
                if random_beta > max_beta:
                    max_beta = random_beta
                    headline_ = headline_idx
            if self.outcomes[turn_idx][headline_] == 1:
                self.num_conversions[headline_] += 1
            else:
                self.num_fails[headline_] += 1
        
        self.num_simul = self.num_conversions + self.num_fails
        if verbose:
            for headline_idx in range(self.num_headlines):
                print(f'Headline {headline_idx} was chosen {self.num_simul[headline_idx]} times')
            
            print(f'n\Overall conclusion: best headline is {np.argmax(self.num_simul)}')
class BankersAlgorithm:
    def __init__(self, total_resources, max_demand, allocation):
        self.total_resources = total_resources
        self.max_demand = max_demand
        self.allocation = allocation
        self.num_customers = len(max_demand)
        self.num_resources = len(total_resources)
        self.available = [self.total_resources[i] - sum([allocation[j][i] for j in range(self.num_customers)]) for i in
                          range(self.num_resources)]
        self.need = [[self.max_demand[i][j] - self.allocation[i][j] for j in range(self.num_resources)] for i in
                     range(self.num_customers)]
        self.requests_log = []

    def is_safe(self):
        work = self.available[:]
        finish = [False] * self.num_customers
        safe_sequence = []

        while len(safe_sequence) < self.num_customers:
            found = False
            for i in range(self.num_customers):
                if not finish[i]:
                    if all(self.need[i][j] <= work[j] for j in range(self.num_resources)):
                        for j in range(self.num_resources):
                            work[j] += self.allocation[i][j]
                        safe_sequence.append(i)
                        finish[i] = True
                        found = True
                        break
            if not found:
                return False
        return True

    def request_resources(self, customer_num, request):
        self.requests_log.append((customer_num, request, 'Request made'))

        if all(request[i] <= self.need[customer_num][i] for i in range(self.num_resources)) and all(
                request[i] <= self.available[i] for i in range(self.num_resources)):
            for i in range(self.num_resources):
                self.available[i] -= request[i]
                self.allocation[customer_num][i] += request[i]
                self.need[customer_num][i] -= request[i]

            if self.is_safe():
                self.requests_log.append((customer_num, request, 'Request granted'))
                return True
            else:
                for i in range(self.num_resources):
                    self.available[i] += request[i]
                    self.allocation[customer_num][i] -= request[i]
                    self.need[customer_num][i] += request[i]
                self.requests_log.append((customer_num, request, 'Request denied (unsafe)'))
                return False
        else:
            self.requests_log.append((customer_num, request, 'Request denied (exceeds needs or available)'))
            return False

    def save_log(self, filename):
        with open(filename, 'w') as file:
            for entry in self.requests_log:
                file.write(f'Customer {entry[0]}: Request {entry[1]} - {entry[2]}\n')


# Example usage:
total_resources = [10, 5, 7]
max_demand = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3]
]
allocation = [
    [0, 1, 0],
    [2, 0, 0],
    [3, 0, 2],
    [2, 1, 1],
    [0, 0, 2]
]

bank = BankersAlgorithm(total_resources, max_demand, allocation)

# Example requests
requests = [
    (0, [0, 4, 2]),
    (1, [1, 2, 2]),
    (3, [0, 2, 0]),
]

for customer_num, request in requests:
    bank.request_resources(customer_num, request)

bank.save_log('requests_log.txt')

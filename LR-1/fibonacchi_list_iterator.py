class FibonacchiLst:
    def __init__(self, instance):
        self.instance = instance
        self.idx = 0

        self.fib_numbers = set()

        if len(instance) > 0:
            max_value = max(instance)

            a = 0
            b = 1

            while a <= max_value:
                self.fib_numbers.add(a)
                a, b = b, a + b

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                res = self.instance[self.idx]
            except IndexError:
                raise StopIteration

            self.idx += 1

            if res in self.fib_numbers:
                return res
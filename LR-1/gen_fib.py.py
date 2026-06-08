def _fib_coroutine():
    fib = [0, 1]

    n = yield

    while True:
        if n < 0:
            result = []
        elif n == 0:
            result = []
        elif n == 1:
            result = [0]
        else:
            while len(fib) < n:
                fib.append(fib[-1] + fib[-2])

            result = fib[:n]

        n = yield result


def my_genn():
    gen = _fib_coroutine()
    next(gen)
    return gen
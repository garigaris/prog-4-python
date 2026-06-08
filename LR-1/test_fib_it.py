import unittest
from gen_fib import FibonacchiLst


class TestFibIterator(unittest.TestCase):

    def test_normal(self):
        result = list(FibonacchiLst(list(range(10))))
        self.assertEqual(result, [0, 1, 2, 3, 5, 8])

    def test_example_from_task(self):
        result = list(FibonacchiLst([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1]))
        self.assertEqual(result, [0, 1, 2, 3, 5, 8, 1])

    def test_corner_0(self):
        result = list(FibonacchiLst(list(range(0))))
        self.assertEqual(result, [])

    def test_corner_1(self):
        result = list(FibonacchiLst(list(range(1))))
        self.assertEqual(result, [0])

    def test_corner_2(self):
        result = list(FibonacchiLst(list(range(2))))
        self.assertEqual(result, [0, 1])

    def test_corner_3(self):
        result = list(FibonacchiLst([1, 1]))
        self.assertEqual(result, [1, 1])

    def test_without_fibonacci_numbers(self):
        result = list(FibonacchiLst([4, 6, 7, 9, 10]))
        self.assertEqual(result, [])

    def test_negative_numbers(self):
        result = list(FibonacchiLst([-5, -1, 0, 1, 2, 4]))
        self.assertEqual(result, [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
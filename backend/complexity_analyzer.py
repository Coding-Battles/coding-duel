import numpy as np
import random
import time
from scipy.stats import linregress


### TODO: ADD SAFETY MEASURES AGAINST EXPONENTIAL COMPLEXITY AND INFINITE LOOPS
class ComplexityAnalyzer:
    def __init__(self):
        # Dictionary of complexity functions we check for
        self.complexity_functions = {
            "O(1)": lambda n: np.ones_like(n),
            "O(log n)": lambda n: np.log(n),
            "O(n)": lambda n: n,
            "O(√n)": lambda n: np.sqrt(n),
            "O(n log n)": lambda n: n * np.log(n),
            "O(n²)": lambda n: n**2,
        }

    def analyze_user_solution(self, user_code, problem_type="two_sum"):
        """
        Main method to analyze user's submitted code
        """
        # 1. Generate test cases of increasing sizes
        test_sizes = [
            100,
            200,
            500,
            1000,
            2000,
            5000,
            10000,
        ]

        # 2. Time the user's solution on each test case
        execution_times = []

        for size in test_sizes:
            # Generate appropriate test data for this size
            test_input = self.generate_test_case(size, problem_type)

            # Time the user's solution
            exec_time = self.time_user_solution(user_code, test_input)
            execution_times.append(exec_time)

        # Reject test results with execution time < threshold
        threshold = 1e-4
        filtered_sizes = []
        filtered_times = []
        for s, t in zip(test_sizes, execution_times):
            if t is not None and t >= threshold:
                filtered_sizes.append(s)
                filtered_times.append(t)

        # 3. Analyze the timing pattern
        complexity = self.detect_complexity(filtered_sizes, filtered_times)

        return {
            "detected_complexity": complexity,
            "execution_times": filtered_times,
            "test_sizes": filtered_sizes,
        }

    def generate_test_case(self, size, problem_type):
        """Generate test case of specified size for the problem"""
        if problem_type == "two_sum":
            # Create array of 'size' elements with target sum at the end
            arr = list(range(size - 2))
            # Add two numbers at the end that sum to target
            a, b = 123456, 654321
            arr += [a, b]
            random.shuffle(arr[:-2])  # Shuffle all except last two
            target = a + b  # Ensure solution exists at the end
            return {"nums": arr, "target": target}

        elif problem_type == "contains_duplicate":
            arr = list(range(size - 1))
            arr += [arr[-1]]  # Add duplicate at the end
            random.shuffle(arr[:-1])  # Shuffle all except last one
            return {"nums": arr}

        # Add more problem types as needed

    def time_user_solution(self, user_code, test_input):
        """Safely execute and time user's code"""
        try:
            # Create safe execution environment
            namespace = {
                "__builtins__": {
                    "len": len,
                    "range": range,
                    "enumerate": enumerate,
                    "sorted": sorted,
                    "set": set,
                    "dict": dict,
                    "list": list,
                }
            }

            # Execute user's code in namespace
            exec(user_code, namespace)

            # Get the solution function (assume it's called 'solution' or 'twoSum')
            solution_func = namespace.get("twoSum") or namespace.get("solution")

            if not solution_func:
                raise ValueError("No solution function found")

            # Time multiple runs for accuracy
            times = []
            for _ in range(3):  # 3 runs to reduce noise
                start = time.perf_counter()
                result = solution_func(**test_input)
                end = time.perf_counter()
                times.append(end - start)

            return np.median(times)  # Use median to reduce noise

        except Exception as e:
            # Handle errors gracefully
            return None

    def detect_complexity(self, sizes, times):
        """Log-log regression method with O(1) special handling"""
        if len(times) < 3:
            return "Unable to determine"

        sizes = np.array(sizes, dtype=float)
        times = np.array(times, dtype=float)

        # Remove any None values (should be filtered already)
        mask = np.isfinite(times)
        sizes = sizes[mask]
        times = times[mask]

        if len(times) < 3:
            return "Unable to determine"

        # Log-log regression
        log_sizes = np.log(sizes)
        log_times = np.log(times)
        slope, intercept, r_value, p_value, std_err = linregress(log_sizes, log_times)

        # Map slope to complexity
        # O(1): slope ≈ 0 and all times < epsilon
        epsilon = 2e-4
        if np.all(times < epsilon) and abs(slope) < 0.15:
            return "O(1)"

        # O(log n): slope ≈ 0.1-0.4
        if 0.1 <= slope < 0.5:
            return "O(log n)"
        # O(n): slope ≈ 1
        if 0.7 <= slope < 1.3:
            return "O(n)"
        # O(n log n): slope ≈ 1.3-1.5
        if 1.3 <= slope < 1.7:
            return "O(n log n)"
        # O(n^2): slope ≈ 1.7-2.3
        if 1.7 <= slope < 2.3:
            return "O(n²)"
        # O(√n): slope ≈ 0.5-0.7
        if 0.5 <= slope < 0.7:
            return "O(√n)"

        return "Unable to determine"


if __name__ == "__main__":
    # Example user code for two_sum problem
    user_code = """
def twoSum(nums, target):
    lookup = {}
    for i, num in enumerate(nums):
        if target - num in lookup:
            return [lookup[target - num], i]
        lookup[num] = i
    return []
"""

    analyzer = ComplexityAnalyzer()
    result = analyzer.analyze_user_solution(user_code, problem_type="two_sum")
    print("Detected Complexity:", result["detected_complexity"])
    print("Execution Times:", result["execution_times"])
    print("Test Sizes:", result["test_sizes"])

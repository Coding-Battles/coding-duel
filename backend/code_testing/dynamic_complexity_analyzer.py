import numpy as np
import random
import time
import queue
import threading
from scipy.stats import linregress
from contextlib import contextmanager

try:
    import resource
except ImportError:
    resource = None


class ComplexityAnalyzer:
    def __init__(self):
        self.MAX_EXECUTION_TIME_PER_SIZE = 3.0
        self.MAX_MEMORY_MB = 256
        self.MAX_TOTAL_ANALYSIS_TIME = 20.0

    @contextmanager
    def timeout_context(self, seconds, description="Operation"):
        def timeout_handler():
            raise TimeoutError(f"{description} timed out after {seconds} seconds")

        timer = threading.Timer(seconds, timeout_handler)
        timer.start()
        try:
            yield
        finally:
            timer.cancel()

    def set_memory_limit(self):
        """Sets a memory limit for the current process. Unix only."""
        if resource is None:
            # This handles non-Unix systems like Windows
            return

        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            desired_limit = self.MAX_MEMORY_MB * 1024 * 1024

            # Check if the current hard limit is already set and lower than our desired limit.
            # If hard == -1, it means unlimited.
            if hard != -1 and desired_limit > hard:
                print(
                    f"Warning: Desired memory limit ({self.MAX_MEMORY_MB}MB) exceeds the current hard limit of "
                    f"{hard // 1024 // 1024}MB. Cannot enforce memory limits."
                )
                return

            # Set the soft limit to our desired value.
            # The hard limit is either kept the same or lowered to our desired value if it was unlimited.
            new_hard = hard if hard != -1 else desired_limit
            resource.setrlimit(resource.RLIMIT_AS, (desired_limit, new_hard))

        except (ValueError, OSError) as e:
            # This will now only catch more unusual permission errors.
            print(f"Warning: Could not set memory limit due to a system error: {e}")

    def analyze_user_solution(
        self, user_code: str, problem_type: str = "two_sum"
    ) -> dict:
        try:
            with self.timeout_context(self.MAX_TOTAL_ANALYSIS_TIME, "Full analysis"):
                return self._perform_analysis(user_code, problem_type)
        except TimeoutError as e:
            return {
                "detected_complexity": "Analysis Timed Out",
                "execution_times": [],
                "test_sizes": [],
                "error": str(e),
            }
        except Exception as e:
            return {
                "detected_complexity": "Analysis Failed",
                "execution_times": [],
                "test_sizes": [],
                "error": f"An unexpected error occurred: {e}",
            }

    def _perform_analysis(self, user_code: str, problem_type: str) -> dict:
        base_sizes = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]
        execution_times = []
        test_sizes = []
        self.set_memory_limit()
        warmup_input = self.generate_test_case(10, problem_type)
        self.time_user_solution_safe(user_code, warmup_input, is_warmup=True)
        for size in base_sizes:
            try:
                test_input = self.generate_test_case(size, problem_type)
                exec_time = self.time_user_solution_safe(user_code, test_input)
                if exec_time is None:
                    print(
                        f"Execution failed or timed out for size {size}. Stopping analysis."
                    )
                    break
                execution_times.append(exec_time)
                test_sizes.append(size)
                if exec_time > 1.0:
                    print(
                        f"Execution time {exec_time:.4f}s exceeds 1.0s threshold. Stopping early."
                    )
                    break
            except (MemoryError, TimeoutError) as e:
                print(f"Resource limit hit at size {size}: {e}. Stopping analysis.")
                break
            except Exception as e:
                print(
                    f"An unexpected error occurred at size {size}: {e}. Stopping analysis."
                )
                break
        if len(execution_times) < 3:
            complexity = "Insufficient Data"
        else:
            complexity = self.detect_complexity_improved(test_sizes, execution_times)
        return {
            "detected_complexity": complexity,
            "execution_times": execution_times,
            "test_sizes": test_sizes,
        }

    def generate_test_case(self, size: int, problem_type: str) -> dict:
        if problem_type == "two_sum":
            arr = list(range(size - 2))
            a, b = random.randint(size, size * 2), random.randint(size, size * 2)
            arr.extend([a, b])
            random.shuffle(arr)
            return {"nums": arr, "target": a + b}
        else:
            return {"nums": list(range(size))}

    def time_user_solution_safe(
        self, user_code: str, test_input: dict, is_warmup: bool = False
    ) -> float | None:
        result_queue = queue.Queue()

        def worker():
            try:
                safe_globals = {
                    "__builtins__": {
                        "len": len,
                        "range": range,
                        "enumerate": enumerate,
                        "sorted": sorted,
                        "sum": sum,
                        "min": min,
                        "max": max,
                        "abs": abs,
                        "zip": zip,
                        "list": list,
                        "dict": dict,
                        "set": set,
                        "tuple": tuple,
                        "str": str,
                        "int": int,
                        "float": float,
                        "bool": bool,
                        "print": lambda *args, **kwargs: None,
                    }
                }
                exec(user_code, safe_globals)
                func_to_run = None
                for name, obj in safe_globals.items():
                    if callable(obj) and not name.startswith("__"):
                        func_to_run = obj
                        break
                if not func_to_run:
                    raise ValueError(
                        "Could not find a function to execute in the provided code."
                    )
                num_runs = 1 if is_warmup else 5
                times = []
                for _ in range(num_runs):
                    start = time.perf_counter()
                    func_to_run(**test_input)
                    end = time.perf_counter()
                    times.append(end - start)
                if is_warmup:
                    result_queue.put(0)
                    return
                if len(times) >= 3:
                    times.sort()
                    stable_time = np.mean(times[1:-1])
                else:
                    stable_time = np.median(times)
                result_queue.put(stable_time)
            except Exception as e:
                result_queue.put(e)

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.MAX_EXECUTION_TIME_PER_SIZE)
        if thread.is_alive():
            return None
        try:
            result = result_queue.get_nowait()
            if isinstance(result, Exception):
                print(f"Error in user code execution: {result}")
                return None
            return result
        except queue.Empty:
            return None

    def detect_complexity_improved(self, sizes: list[int], times: list[float]) -> str:
        if len(times) < 3:
            return "Insufficient Data"
        sizes, times = np.array(sizes, dtype=float), np.array(times, dtype=float)
        valid_mask = times > 1e-9
        if np.sum(valid_mask) < 3:
            return "Insufficient Data (or O(1))"
        sizes, times = sizes[valid_mask], times[valid_mask]
        if np.std(times) / np.mean(times) < 0.3 and np.mean(times) < 1e-4:
            return "O(1)"
        size_ratios = sizes[1:] / sizes[:-1]
        time_ratios = times[1:] / times[:-1]
        quadratic_score = np.mean(np.abs(time_ratios - size_ratios**2))
        linear_score = np.mean(np.abs(time_ratios - size_ratios))
        if quadratic_score < linear_score * 0.5 and len(times) > 3:
            return "O(n²)"
        try:
            log_sizes = np.log(sizes)
            log_times = np.log(times)
            slope, _, r_value, _, _ = linregress(log_sizes, log_times)
            if r_value**2 > 0.9:
                if slope < 0.2:
                    return "O(1)"
                if slope < 0.8:
                    return "O(log n)"
                if slope < 1.2:
                    return "O(n)"
                if slope < 1.8:
                    _, _, r_n, _, _ = linregress(sizes, times)
                    _, _, r_nlogn, _, _ = linregress(sizes * np.log(sizes), times)
                    return "O(n log n)" if r_nlogn**2 > r_n**2 else "O(n)"
                if slope < 2.2:
                    return "O(n²)"
                return f"O(n^{slope:.1f})"
        except (ValueError, IndexError):
            pass
        best_fit = "Unknown"
        best_r2 = -1.0
        models = {
            "O(log n)": lambda n: np.log(n),
            "O(n)": lambda n: n,
            "O(n log n)": lambda n: n * np.log(n),
            "O(n²)": lambda n: n**2,
        }
        for name, func in models.items():
            model_x = func(sizes)
            if not np.all(np.isfinite(model_x)):
                continue
            _, _, r_value, _, _ = linregress(model_x, times)
            r2 = r_value**2
            if r2 > best_r2:
                best_r2 = r2
                best_fit = name
        return best_fit if best_r2 > 0.85 else "Complex/Irregular"


# --- Example Usage ---
if __name__ == "__main__":
    test_codes = {
        "O(1)": """
def solution(nums, target):
    return [0, 1]
""",
        # NOTE: A pure log(n) is too fast to measure reliably.
        # We simulate a "heavier" log(n) by putting it in a loop,
        # which effectively makes it O(n log n) in this test harness,
        # but the log-log slope should be closer to 1.
        "O(n log n) [sorting]": """
def solution(nums, target):
    # This is a classic O(n log n) operation
    arr = sorted(nums)
    return arr[0]
""",
        "O(n)": """
def solution(nums, target):
    # A single pass is O(n)
    total = sum(nums)
    return total
""",
        "O(n²)": """
def solution(nums, target):
    total = 0
    # Nested loops are O(n^2)
    for x in nums:
        for y in nums:
            total += x + y
    return total
""",
        "Exponential (Timeout)": """
def solution(nums, target):
    # Classic exponential recursion
    def fib(n):
        if n <= 1: return 1
        return fib(n-1) + fib(n-2)
    # Even a small n will time out
    return fib(len(nums) // 1000)
""",
    }

    analyzer = ComplexityAnalyzer()
    for description, code in test_codes.items():
        print(f"\n{'='*15} Testing: {description} {'='*15}")
        result = analyzer.analyze_user_solution(code, problem_type="two_sum")
        print(f"--> Detected Complexity: {result['detected_complexity']}")
        if result["test_sizes"]:
            print(f"    Test sizes: {result['test_sizes']}")
            print(f"    Times (s) : {[f'{t:.6f}' for t in result['execution_times']]}")
        if result.get("error"):
            print(f"    Error: {result['error']}")

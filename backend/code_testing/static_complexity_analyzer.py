import ast


class ComplexityVisitor(ast.NodeVisitor):
    """
    An AST NodeVisitor that traverses a Python function's syntax tree
    to estimate its Big O complexity.

    It works by tracking the maximum depth of nested loops and identifying
    operations that add logarithmic factors (like sorting).
    """

    def __init__(self):
        # The maximum nesting level of loops found so far.
        self.max_nesting_level = 0
        # The current nesting level as we traverse the tree.
        self.current_nesting_level = 0
        # A flag to indicate if an O(n log n) operation like sorting was found.
        self.has_nlogn_component = False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Entry point for visiting a function definition."""
        # Reset state for each new function
        self.max_nesting_level = 0
        self.current_nesting_level = 0
        self.has_nlogn_component = False
        # Visit all child nodes in the function body
        self.generic_visit(node)

    def _handle_loop(self, node):
        """A helper method to handle loop-like nodes."""
        self.current_nesting_level += 1
        self.max_nesting_level = max(self.max_nesting_level, self.current_nesting_level)
        # Recursively visit the body of the loop
        self.generic_visit(node)
        self.current_nesting_level -= 1

    def visit_For(self, node: ast.For):
        """Called for 'for' loops."""
        self._handle_loop(node)

    def visit_While(self, node: ast.While):
        """
        Called for 'while' loops.
        NOTE: This analyzer cannot determine the condition of the while loop.
        A binary search (O(log n)) will be incorrectly identified as O(n)
        because we only see the loop structure, not the halving of the search space.
        """
        self._handle_loop(node)

    def visit_ListComp(self, node: ast.ListComp):
        """Called for list comprehensions."""
        self._handle_loop(node)

    def visit_DictComp(self, node: ast.DictComp):
        """Called for dict comprehensions."""
        self._handle_loop(node)

    def visit_SetComp(self, node: ast.SetComp):
        """Called for set comprehensions."""
        self._handle_loop(node)

    def visit_Call(self, node: ast.Call):
        """
        Called for function calls.
        We check for common O(n log n) functions like sort().
        """
        # Check for `list.sort()`
        if isinstance(node.func, ast.Attribute) and node.func.attr == "sort":
            self.has_nlogn_component = True
        # Check for `sorted()`
        elif isinstance(node.func, ast.Name) and node.func.id == "sorted":
            self.has_nlogn_component = True

        # Continue visiting child nodes of the call (e.g., arguments)
        self.generic_visit(node)

    def get_complexity(self):
        """
        Determines the Big O complexity based on the gathered information.
        """
        if self.has_nlogn_component:
            # If there's a sort and a loop, it's O(n log n).
            # If there's a sort and nested loops, it's likely higher, but
            # O(n log n) is a common, specific pattern we check for.
            # We prioritize this if the loop level is 1.
            if self.max_nesting_level <= 1:
                return "O(n log n)"

        # Map loop nesting level to complexity
        if self.max_nesting_level == 0:
            return "O(1)"
        elif self.max_nesting_level == 1:
            return "O(n)"
        elif self.max_nesting_level == 2:
            return "O(n²)"
        else:
            # For deeper nesting, we can generalize
            return f"O(n^{self.max_nesting_level})"


def analyze_code_complexity(code_string: str) -> dict:
    """
    Analyzes a string of Python code and returns the Big O complexity for each function.

    This is a static analysis tool and relies on heuristics. It's effective for
    simple, LeetCode-style problems but may be inaccurate for complex algorithms,
    especially those with O(log n) complexity that don't use obvious sorting.

    Args:
        code_string (str): A string containing one or more Python function definitions.

    Returns:
        dict: A dictionary mapping function names to their estimated Big O complexity.
              Returns an error message in the dict if parsing fails.
    """
    results = {}
    try:
        tree = ast.parse(code_string)
    except SyntaxError as e:
        return {"error": f"Failed to parse Python code: {e}"}

    visitor = ComplexityVisitor()
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            visitor.visit(node)
            results[node.name] = visitor.get_complexity()

    return results


# Main execution block for demonstration
if __name__ == "__main__":
    print("--- Static Code Complexity Analyzer ---")
    print(
        "NOTE: This tool uses heuristics and has limitations (e.g., detecting O(log n)).\n"
    )

    # --- Example 1: O(n²) ---
    code_two_sum_brute = """
def two_sum_brute_force(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    print(f"Analyzing 'two_sum_brute_force':")
    complexity = analyze_code_complexity(code_two_sum_brute)
    print(complexity)
    print("-" * 20)

    # --- Example 2: O(n) ---
    code_two_sum_hash = """
def two_sum_hash_map(nums, target):
    hash_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hash_map:
            return [hash_map[complement], i]
        hash_map[num] = i
    return []
"""
    print(f"Analyzing 'two_sum_hash_map':")
    complexity = analyze_code_complexity(code_two_sum_hash)
    print(complexity)
    print("-" * 20)

    # --- Example 3: O(1) ---
    code_constant = """
def get_first_element(nums):
    if not nums:
        return None
    return nums[0]
"""
    print(f"Analyzing 'get_first_element':")
    complexity = analyze_code_complexity(code_constant)
    print(complexity)
    print("-" * 20)

    # --- Example 4: O(n log n) ---
    code_nlogn = """
def contains_duplicate_by_sorting(nums):
    nums.sort() # This is the O(n log n) part
    for i in range(len(nums) - 1):
        if nums[i] == nums[i+1]:
            return True
    return False
"""
    print(f"Analyzing 'contains_duplicate_by_sorting':")
    complexity = analyze_code_complexity(code_nlogn)
    print(complexity)
    print("-" * 20)

    # --- Example 5: O(log n) - KNOWN LIMITATION ---
    code_log_n = """
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high: # This loop is logarithmic, but our tool can't tell
        mid = (low + high) // 2
        if arr[mid] < target:
            low = mid + 1
        elif arr[mid] > target:
            high = mid - 1
        else:
            return mid
    return -1
"""
    print(f"Analyzing 'binary_search' (demonstrates a limitation):")
    complexity = analyze_code_complexity(code_log_n)
    print(f"Expected: O(log n) -> Detected: {complexity['binary_search']}")
    print(
        "This is because the analyzer sees a 'while' loop but cannot analyze its conditional logic."
    )
    print("-" * 20)

    # --- Example 6: Multiple functions in one file ---
    code_multiple_funcs = """
def find_max(numbers):
    # O(n)
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

def check_matrix(matrix):
    # O(n^2)
    rows = len(matrix)
    cols = len(matrix[0])
    for r in range(rows):
        for c in range(cols):
            print(matrix[r][c])
"""
    print(f"Analyzing multiple functions at once:")
    complexity = analyze_code_complexity(code_multiple_funcs)
    print(complexity)
    print("-" * 20)

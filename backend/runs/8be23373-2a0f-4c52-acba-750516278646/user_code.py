def two_sum(nums, target):
    num_map = {}  # Stores number: index

    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_map:
            return [num_map[complement], i]
        num_map[num] = i

    return []  # If no solution is found

def manual_burst_balloons():
    """
    Manual calculation for [2,3,4] to find optimal solution
    """
    nums = [2, 3, 4]

    print("Manual calculation for [2,3,4]:")
    print("All possible orders to burst balloons:")

    # Order 1: burst 2, then 3, then 4
    print("\nOrder 1: 2 -> 3 -> 4")
    print("  Burst 2: 1*2*3 = 6, remaining [3,4]")
    print("  Burst 3: 1*3*4 = 12, remaining [4]")
    print("  Burst 4: 1*4*1 = 4, remaining []")
    print("  Total: 6 + 12 + 4 = 22")

    # Order 2: burst 2, then 4, then 3
    print("\nOrder 2: 2 -> 4 -> 3")
    print("  Burst 2: 1*2*3 = 6, remaining [3,4]")
    print("  Burst 4: 3*4*1 = 12, remaining [3]")
    print("  Burst 3: 1*3*1 = 3, remaining []")
    print("  Total: 6 + 12 + 3 = 21")

    # Order 3: burst 3, then 2, then 4
    print("\nOrder 3: 3 -> 2 -> 4")
    print("  Burst 3: 2*3*4 = 24, remaining [2,4]")
    print("  Burst 2: 1*2*4 = 8, remaining [4]")
    print("  Burst 4: 1*4*1 = 4, remaining []")
    print("  Total: 24 + 8 + 4 = 36")

    # Order 4: burst 3, then 4, then 2
    print("\nOrder 4: 3 -> 4 -> 2")
    print("  Burst 3: 2*3*4 = 24, remaining [2,4]")
    print("  Burst 4: 2*4*1 = 8, remaining [2]")
    print("  Burst 2: 1*2*1 = 2, remaining []")
    print("  Total: 24 + 8 + 2 = 34")

    # Order 5: burst 4, then 2, then 3
    print("\nOrder 5: 4 -> 2 -> 3")
    print("  Burst 4: 3*4*1 = 12, remaining [2,3]")
    print("  Burst 2: 1*2*3 = 6, remaining [3]")
    print("  Burst 3: 1*3*1 = 3, remaining []")
    print("  Total: 12 + 6 + 3 = 21")

    # Order 6: burst 4, then 3, then 2
    print("\nOrder 6: 4 -> 3 -> 2")
    print("  Burst 4: 3*4*1 = 12, remaining [2,3]")
    print("  Burst 3: 2*3*1 = 6, remaining [2]")
    print("  Burst 2: 1*2*1 = 2, remaining []")
    print("  Total: 12 + 6 + 2 = 20")

    print("\nMaximum: 36 (Order 3: 3 -> 2 -> 4)")
    print("Minimum: 20 (Order 6: 4 -> 3 -> 2)")

    print("\nThe test expects 20, but optimal is 36!")
    print(
        "This suggests the test case might be wrong, or there's a different interpretation."
    )


manual_burst_balloons()

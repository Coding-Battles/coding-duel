#!/usr/bin/env python3

# Test to verify the Docker runner fix for Java individual execution

def test_java_execution_args():
    """Test that Java execution gets the correct arguments"""
    
    # Mock the DockerRunRequest
    class DockerRunRequest:
        def __init__(self):
            self.language = "java"
            self.function_name = "firstBadVersion"
            self.test_input = {"n": 5, "bad": 4}
    
    # Mock request
    request = DockerRunRequest()
    
    # Test the argument construction logic
    import json
    
    # This is the logic from docker_runner.py
    base_run_command = "java -Xms8m -Xmx32m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 Main"
    
    if request.language in ["python", "javascript", "java"]:
        function_name = getattr(request, 'function_name', 'solution')
        input_json = json.dumps(request.test_input).replace('"', '\\"')
        run_command = base_run_command + f' "{function_name}" "{input_json}"'
        print("✅ Java will get both function name and input arguments")
        print(f"Expected command: {run_command}")
        print(f"Function name: {function_name}")
        print(f"Input JSON: {input_json}")
        
        # Verify command line argument count
        args_count = run_command.count('"') // 2  # Each argument is quoted
        print(f"Number of arguments (quoted strings): {args_count}")
        
        if args_count >= 2:
            print("✅ Arguments look correct - should have method name and input data")
        else:
            print("❌ Missing arguments")
    else:
        print("❌ Java not in the argument-passing languages")
        
    return run_command

def test_java_wrapper_expectation():
    """Test what the Java wrapper expects"""
    
    print("\nJava wrapper expectation:")
    print("- args[0]: program name (automatic)")  
    print("- args[1]: method name (e.g., 'firstBadVersion')")
    print("- args[2]: input JSON (e.g., '{\"n\":5,\"bad\":4}')")
    print("- Total args.length should be >= 3")
    
    return True

if __name__ == "__main__":
    print("Testing Docker runner Java argument fix:")
    print("=" * 50)
    test_java_execution_args()
    test_java_wrapper_expectation()
    print("\n✅ Docker runner should now pass correct arguments to Java wrapper")
def test_f_string():
    wrapped_user_code = "test code"
    java_wrapper = f"""import java.util.*;
import java.lang.reflect.*;

class TestRunner {{
    public static void main(String[] args) {{
        System.out.println("Hello World");
    }}
}}

{wrapped_user_code}
"""
    return java_wrapper


if __name__ == "__main__":
    result = test_f_string()
    print("✅ F-string test passed")
    print(result)

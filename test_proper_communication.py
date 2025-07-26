#!/usr/bin/env python3

import sys
sys.path.append('.')

import docker
import base64
import json
import time

def test_proper_communication():
    print("Testing proper socket communication...")
    
    client = docker.from_env()
    
    try:
        # Create and setup container
        container = client.containers.run(
            "openjdk:11-jdk-slim",
            command="sleep 300", 
            detach=True,
            working_dir="/tmp",
            remove=False,
            mem_limit="128m",
            nano_cpus=300000000,
            network_mode="none",
            security_opt=["no-new-privileges:true"]
        )
        
        print(f"✅ Container started: {container.id[:12]}")
        
        # Setup server
        with open("backend/code_testing/PersistentJavaRunner.java", "r") as f:
            server_code = f.read()
        
        encoded_code = base64.b64encode(server_code.encode("utf-8")).decode("ascii")
        create_result = container.exec_run(
            f"sh -c 'echo {encoded_code} | base64 -d > /tmp/PersistentJavaRunner.java'",
            workdir="/tmp"
        )
        
        compile_result = container.exec_run("javac PersistentJavaRunner.java", workdir="/tmp")
        
        # Start server
        server_result = container.exec_run(
            "bash -c 'java -Xms32m -Xmx128m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 PersistentJavaRunner > /tmp/java_server.log 2>&1 & echo $! > /tmp/server.pid'",
            workdir="/tmp"
        )
        
        time.sleep(3)
        
        # Create a proper test request
        test_request = {
            "code": "class Solution { public int[] twoSum(int[] nums, int target) { for (int i = 0; i < nums.length; i++) { for (int j = i + 1; j < nums.length; j++) { if (nums[i] + nums[j] == target) { return new int[]{i, j}; } } } return new int[]{}; } }",
            "test_cases": [{"input": {"nums": [2, 7, 11, 15], "target": 9}}],
            "function_name": "twoSum"
        }
        
        request_json = json.dumps(test_request)
        print(f"📤 Request JSON length: {len(request_json)}")
        
        # Method 1: Use bash TCP redirect properly (need to decode base64 first)
        encoded_request = base64.b64encode(request_json.encode()).decode()
        
        print("🔌 Testing with base64 decode + netcat...")
        comm_test = container.exec_run(
            f"bash -c 'echo {encoded_request} | base64 -d | timeout 10 nc localhost 8899'",
            workdir="/tmp"
        )
        
        print(f"📤 Communication exit code: {comm_test.exit_code}")
        response = comm_test.output.decode("utf-8").strip()
        print(f"📤 Response length: {len(response)}")
        print(f"📤 Response: {response}")
        
        # Check server logs after communication
        log_check = container.exec_run("cat /tmp/java_server.log", workdir="/tmp")
        logs = log_check.output.decode('utf-8')
        print(f"📋 Server logs after communication: {logs}")
        
        # Try to parse the response as JSON
        if response:
            try:
                response_data = json.loads(response)
                print(f"✅ Valid JSON response: {response_data}")
                return True
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                return False
        else:
            print("❌ No response received")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            container.remove(force=True)
        except:
            pass

if __name__ == "__main__":
    if test_proper_communication():
        print("🎉 Socket communication is working!")
    else:
        print("❌ Socket communication failed")
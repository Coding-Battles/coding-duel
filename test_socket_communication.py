#!/usr/bin/env python3

import sys
sys.path.append('.')

import docker
import base64
import json
import time

def test_socket_communication():
    print("Testing direct socket communication...")
    
    client = docker.from_env()
    
    try:
        # Create and setup container exactly like the system does
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
        
        # Check if server is running
        pid_check = container.exec_run("cat /tmp/server.pid", workdir="/tmp")
        server_pid = pid_check.output.decode("utf-8").strip()
        print(f"✅ Server PID: {server_pid}")
        
        # Test request
        test_request = {
            "code": "class Solution { public int[] twoSum(int[] nums, int target) { return new int[]{0, 1}; } }",
            "test_cases": [{"input": {"nums": [2, 7], "target": 9}}],
            "function_name": "twoSum"
        }
        
        request_json = json.dumps(test_request)
        encoded_request = base64.b64encode(request_json.encode()).decode()
        
        print("🔌 Testing communication methods...")
        
        # Method 1: Try with netcat
        nc_test = container.exec_run(f"echo {encoded_request} | base64 -d | nc localhost 8899", workdir="/tmp")
        print(f"📤 Netcat result (exit {nc_test.exit_code}): {nc_test.output.decode('utf-8')[:200]}")
        
        # Method 2: Try with bash TCP redirect  
        bash_test = container.exec_run(f"bash -c 'echo \"{request_json}\" > /dev/tcp/localhost/8899'", workdir="/tmp")
        print(f"📤 Bash TCP result (exit {bash_test.exit_code}): {bash_test.output.decode('utf-8')[:200]}")
        
        # Method 3: Try with telnet if available
        telnet_test = container.exec_run("which telnet", workdir="/tmp")
        if telnet_test.exit_code == 0:
            print("📤 Telnet available, testing...")
        else:
            print("📤 Telnet not available")
        
        # Check server logs
        log_check = container.exec_run("cat /tmp/java_server.log", workdir="/tmp")
        logs = log_check.output.decode('utf-8')
        print(f"📋 Server logs: {logs}")
        
        return True
        
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
    test_socket_communication()
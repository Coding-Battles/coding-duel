#!/usr/bin/env python3

import sys
sys.path.append('.')

import docker
import base64
import json
import time

def test_server_parsing():
    print("Testing Java server response with debug info...")
    
    client = docker.from_env()
    
    try:
        # Create container
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
        
        # Create the exact test request that produces the issue
        test_request = {
            "code": """
class Solution {
    public int missingNumber(int[] nums) {
        int n = nums.length;
        long expectedSum = (long)n * (n + 1) / 2;
        long actualSum = 0;
        for (int num : nums) {
            actualSum += num;
        }
        return (int)(expectedSum - actualSum);
    }
}
""",
            "test_cases": [
                {"input": {"nums": [3, 0, 1]}},
                {"input": {"nums": [0, 1]}},
                {"input": {"nums": [9, 6, 4, 2, 3, 5, 7, 0, 1]}}
            ],
            "function_name": "missingNumber",
            "method_signature": {"params": [{"name": "nums", "type": "int[]"}], "return_type": "int"}
        }
        
        request_json = json.dumps(test_request)
        
        print(f"📤 Sending request with {len(test_request['test_cases'])} test cases")
        print(f"📤 Request length: {len(request_json)} characters")
        
        # Send request using bash TCP redirect
        comm_script = f'''#!/bin/bash
exec 3<>/dev/tcp/localhost/8899
echo '{request_json}' >&3
cat <&3
exec 3<&-
exec 3>&-
'''
        
        script_encoded = base64.b64encode(comm_script.encode()).decode()
        script_create = container.exec_run(
            f"sh -c 'echo {script_encoded} | base64 -d > /tmp/socket_comm.sh && chmod +x /tmp/socket_comm.sh'",
            workdir="/tmp"
        )
        
        # Execute communication
        socket_send = container.exec_run(
            "timeout 10 bash /tmp/socket_comm.sh",
            workdir="/tmp"
        )
        
        if socket_send.exit_code == 0 or socket_send.exit_code == 124:  # 124 = timeout
            response = socket_send.output.decode("utf-8").strip()
            print(f"📤 Response length: {len(response)} characters")
            print(f"📤 Raw response: {response}")
            
            # Try to parse as JSON
            try:
                response_data = json.loads(response)
                if isinstance(response_data, list):
                    print(f"✅ Parsed {len(response_data)} results from response")
                    for i, result in enumerate(response_data):
                        print(f"  Result {i+1}: {result}")
                else:
                    print(f"✅ Parsed single result: {response_data}")
            except json.JSONDecodeError as e:
                print(f"❌ Could not parse JSON: {e}")
        else:
            print(f"❌ Communication failed: {socket_send.output.decode('utf-8')}")
        
        # Check server logs
        log_check = container.exec_run("cat /tmp/java_server.log", workdir="/tmp")
        logs = log_check.output.decode('utf-8')
        print(f"\n📋 Server logs:")
        print(logs)
        
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
    test_server_parsing()
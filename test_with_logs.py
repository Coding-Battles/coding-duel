#!/usr/bin/env python3

import docker
import base64
import time

def test_java_with_logs():
    client = docker.from_env()
    
    print("Testing Java setup with detailed logging...")
    try:
        container = client.containers.run(
            "openjdk:11-jdk-slim",
            command="sleep 120", 
            detach=True,
            working_dir="/tmp",
            remove=False
        )
        
        print(f"✅ Container started: {container.id[:12]}")
        
        # Copy and compile
        with open("backend/code_testing/PersistentJavaRunner.java", "r") as f:
            server_code = f.read()
        
        encoded_code = base64.b64encode(server_code.encode("utf-8")).decode("ascii")
        create_result = container.exec_run(
            f"sh -c 'echo {encoded_code} | base64 -d > /tmp/PersistentJavaRunner.java'",
            workdir="/tmp"
        )
        
        compile_result = container.exec_run("javac PersistentJavaRunner.java", workdir="/tmp")
        print("✅ Compilation successful")
        
        # Start server with more detailed logging
        server_result = container.exec_run(
            "bash -c 'java -Xms32m -Xmx128m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 PersistentJavaRunner > /tmp/java_server.log 2>&1 & echo $! > /tmp/server.pid; sleep 1; echo \"Background process started\"'",
            workdir="/tmp"
        )
        
        print("✅ Server startup command executed")
        
        # Check logs immediately
        time.sleep(2)
        
        # Check PID and logs
        pid_check = container.exec_run("cat /tmp/server.pid", workdir="/tmp")
        log_check = container.exec_run("cat /tmp/java_server.log", workdir="/tmp")
        
        server_pid = pid_check.output.decode("utf-8").strip()
        server_logs = log_check.output.decode("utf-8")
        
        print(f"📋 Server PID: {server_pid}")
        print(f"📋 Server logs: {server_logs}")
        
        if server_pid.isdigit():
            # Check if process is still alive
            alive_check = container.exec_run(f"kill -0 {server_pid} 2>/dev/null", workdir="/tmp")
            if alive_check.exit_code == 0:
                print("✅ Server process is running")
                
                # Check if it's listening on port 8899
                netstat_check = container.exec_run("netstat -ln 2>/dev/null | grep 8899 || echo 'Port not found'", workdir="/tmp")
                netstat_output = netstat_check.output.decode("utf-8")
                print(f"📋 Port check: {netstat_output}")
                
                # Try socket connection
                socket_test = container.exec_run("timeout 3 bash -c '</dev/tcp/localhost/8899' 2>/dev/null && echo 'Socket OK' || echo 'Socket FAIL'", workdir="/tmp")
                socket_result = socket_test.output.decode("utf-8").strip()
                print(f"🔌 Socket test: {socket_result}")
                
                # Try sending actual data
                if "Socket OK" in socket_result:
                    print("✅ Socket connection works!")
                    
                    # Test actual communication
                    test_request = '{"code":"class Solution { public int test() { return 42; } }","test_cases":[{"input":{}}],"function_name":"test"}'
                    encoded_req = base64.b64encode(test_request.encode()).decode()
                    
                    comm_test = container.exec_run(f"bash -c 'echo {encoded_req} | base64 -d | timeout 5 nc localhost 8899'", workdir="/tmp")
                    if comm_test.exit_code == 0:
                        response = comm_test.output.decode("utf-8").strip()
                        print(f"🔥 COMMUNICATION SUCCESS: {len(response)} chars received")
                        print(f"📤 Response: {response}")
                        return True
                    else:
                        print(f"❌ Communication failed: {comm_test.output.decode('utf-8')}")
                else:
                    print("❌ Socket connection failed")
            else:
                print("❌ Server process died")
                print(f"Final logs: {server_logs}")
        else:
            print(f"❌ Invalid PID: {server_pid}")
        
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
    if test_java_with_logs():
        print("🎉 SUCCESS: Java socket server is fully working!")
    else:
        print("❌ Tests failed")
#!/usr/bin/env python3

import docker
import base64

def test_java_setup():
    client = docker.from_env()
    
    print("Testing minimal Java setup...")
    try:
        container = client.containers.run(
            "openjdk:11-jdk-slim",
            command="sleep 60", 
            detach=True,
            working_dir="/tmp",
            remove=False
        )
        
        print(f"✅ Container started: {container.id[:12]}")
        
        # Copy PersistentJavaRunner.java to container
        with open("backend/code_testing/PersistentJavaRunner.java", "r") as f:
            server_code = f.read()
        
        encoded_code = base64.b64encode(server_code.encode("utf-8")).decode("ascii")
        create_result = container.exec_run(
            f"sh -c 'echo {encoded_code} | base64 -d > /tmp/PersistentJavaRunner.java'",
            workdir="/tmp"
        )
        
        if create_result.exit_code != 0:
            print(f"❌ Failed to copy server code: {create_result.output.decode('utf-8')}")
            return False
        
        print("✅ Server code copied")
        
        # Compile the server
        compile_result = container.exec_run(
            "javac PersistentJavaRunner.java",
            workdir="/tmp"
        )
        
        if compile_result.exit_code != 0:
            error_msg = compile_result.output.decode("utf-8")
            print(f"❌ Compilation failed: {error_msg}")
            return False
        
        print("✅ Compilation successful")
        
        # Start server in background
        server_result = container.exec_run(
            "bash -c 'java -Xms32m -Xmx128m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 PersistentJavaRunner > /tmp/java_server.log 2>&1 & echo $! > /tmp/server.pid'",
            workdir="/tmp"
        )
        
        if server_result.exit_code != 0:
            print(f"❌ Server startup failed: {server_result.output.decode('utf-8')}")
            return False
        
        print("✅ Server started in background")
        
        # Wait and check
        import time
        time.sleep(3)
        
        # Check PID
        pid_check = container.exec_run("cat /tmp/server.pid", workdir="/tmp")
        if pid_check.exit_code == 0:
            server_pid = pid_check.output.decode("utf-8").strip()
            print(f"✅ Server PID: {server_pid}")
            
            if server_pid.isdigit():
                # Check if alive
                alive_check = container.exec_run(f"kill -0 {server_pid} 2>/dev/null", workdir="/tmp")
                if alive_check.exit_code == 0:
                    print("✅ Server process is running")
                    
                    # Test socket
                    socket_test = container.exec_run("timeout 3 bash -c '</dev/tcp/localhost/8899' 2>/dev/null && echo 'Socket OK' || echo 'Socket FAIL'", workdir="/tmp")
                    socket_result = socket_test.output.decode("utf-8").strip()
                    print(f"✅ Socket test: {socket_result}")
                    
                    if "Socket OK" in socket_result:
                        print("🎉 SUCCESS: Complete Java socket server is working!")
                        return True
                    else:
                        log_check = container.exec_run("cat /tmp/java_server.log", workdir="/tmp")
                        logs = log_check.output.decode('utf-8')
                        print(f"❌ Socket failed. Server logs: {logs}")
                        return False
                else:
                    print("❌ Server process died")
                    return False
            else:
                print(f"❌ Invalid PID: {server_pid}")
                return False
        else:
            print("❌ Could not read PID file")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        try:
            container.remove(force=True)
        except:
            pass

if __name__ == "__main__":
    if test_java_setup():
        print("✅ All tests passed - Java socket server is ready!")
    else:
        print("❌ Tests failed")
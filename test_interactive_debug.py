#!/usr/bin/env python3

import docker
import base64
import time

def test_interactive_debug():
    client = docker.from_env()
    
    print("Testing with interactive debugging...")
    try:
        container = client.containers.run(
            "openjdk:11-jdk-slim",
            command="sleep 300", 
            detach=True,
            working_dir="/tmp",
            remove=False
        )
        
        print(f"✅ Container started: {container.id[:12]}")
        print(f"🔧 Container ID: {container.id}")
        print("You can now run: docker exec -it {} bash".format(container.id[:12]))
        
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
        
        # Try running server in foreground first to see what happens
        print("🔧 Testing server in foreground (will timeout after 10 seconds)...")
        fg_test = container.exec_run(
            "timeout 10 java -Xms32m -Xmx128m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 PersistentJavaRunner",
            workdir="/tmp"
        )
        
        print(f"📋 Foreground test exit code: {fg_test.exit_code}")
        print(f"📋 Foreground test output: {fg_test.output.decode('utf-8')}")
        
        # Now try background with explicit nohup
        print("🔧 Testing with nohup...")
        nohup_result = container.exec_run(
            "bash -c 'nohup java -Xms32m -Xmx128m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 PersistentJavaRunner > /tmp/java_server.log 2>&1 & echo $! > /tmp/server.pid'",
            workdir="/tmp"
        )
        
        time.sleep(3)
        
        # Check everything
        pid_check = container.exec_run("cat /tmp/server.pid", workdir="/tmp")
        log_check = container.exec_run("cat /tmp/java_server.log", workdir="/tmp")
        ps_check = container.exec_run("ps aux | grep java", workdir="/tmp")
        
        server_pid = pid_check.output.decode("utf-8").strip()
        server_logs = log_check.output.decode("utf-8")
        ps_output = ps_check.output.decode("utf-8")
        
        print(f"📋 Nohup PID: {server_pid}")
        print(f"📋 Nohup logs: {server_logs}")
        print(f"📋 Process list: {ps_output}")
        
        if server_pid.isdigit():
            alive_check = container.exec_run(f"kill -0 {server_pid} 2>/dev/null", workdir="/tmp")
            print(f"📋 Process alive check exit code: {alive_check.exit_code}")
            
            if alive_check.exit_code == 0:
                print("✅ Process is running with nohup!")
                
                # Test socket
                socket_test = container.exec_run("timeout 3 bash -c '</dev/tcp/localhost/8899' 2>/dev/null && echo 'Socket OK' || echo 'Socket FAIL'", workdir="/tmp")
                socket_result = socket_test.output.decode("utf-8").strip()
                print(f"🔌 Socket test: {socket_result}")
                
                return "Socket OK" in socket_result
        
        print("❌ Server failed to start properly")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Keep container running for manual inspection
        print(f"🔧 Container {container.id[:12]} is still running for manual inspection")
        print("Run: docker exec -it {} bash".format(container.id[:12]))
        print("Then: java PersistentJavaRunner")

if __name__ == "__main__":
    test_interactive_debug()
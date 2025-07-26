#!/usr/bin/env python3

import docker
import base64
import os

client = docker.from_env()

print("Testing compilation in detail...")
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
    server_file_path = "backend/code_testing/PersistentJavaRunner.java"
    with open(server_file_path, "r") as f:
        server_code = f.read()
    
    encoded_code = base64.b64encode(server_code.encode("utf-8")).decode("ascii")
    create_result = container.exec_run(
        f"sh -c 'echo {encoded_code} | base64 -d > /tmp/PersistentJavaRunner.java'",
        workdir="/tmp"
    )
    
    if create_result.exit_code != 0:
        print(f"❌ Failed to copy server code: {create_result.output.decode('utf-8')}")
    else:
        print("✅ Server code copied successfully")
        
        # Try compilation
        compile_result = container.exec_run("javac PersistentJavaRunner.java", workdir="/tmp")
        
        if compile_result.exit_code != 0:
            error_msg = compile_result.output.decode("utf-8")
            print(f"❌ Compilation failed: {error_msg}")
        else:
            print("✅ Compilation successful")
            
            # Test the updated server startup
            print("Testing detached server startup...")
            server_result = container.exec_run(
                ["java", "-Xms32m", "-Xmx128m", "-XX:+UseSerialGC", "-XX:TieredStopAtLevel=1", "PersistentJavaRunner"],
                workdir="/tmp",
                detach=True
            )
            
            print(f"✅ Server started in detached mode")
            
            # Wait and check
            import time
            time.sleep(3)
            
            # Find process
            find_process = container.exec_run("sh -c 'pgrep -f PersistentJavaRunner'", workdir="/tmp")
            if find_process.exit_code == 0:
                server_pid = find_process.output.decode("utf-8").strip()
                print(f"✅ Found Java server process with PID: {server_pid}")
                
                # Test socket
                test_socket = container.exec_run("sh -c 'timeout 3 bash -c \"</dev/tcp/localhost/8899\" 2>/dev/null && echo \"Socket OK\" || echo \"Socket FAIL\"'", workdir="/tmp")
                socket_status = test_socket.output.decode("utf-8").strip()
                print(f"🔌 Socket test result: {socket_status}")
                
                if "Socket OK" in socket_status:
                    print("🎉 SUCCESS! Socket-based Java server is working with detached execution")
                else:
                    print("❌ Socket test failed")
            else:
                print("❌ Java process not found")
    
    container.remove(force=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
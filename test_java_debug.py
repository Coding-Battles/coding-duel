#!/usr/bin/env python3

import docker
import base64
import time

client = docker.from_env()

print("Testing Java server startup with debugging...")
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
    
    # Try running server with output capture instead of detached
    print("Testing server with output capture...")
    server_result = container.exec_run(
        "timeout 5 java -Xms32m -Xmx128m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 PersistentJavaRunner",
        workdir="/tmp"
    )
    
    print(f"Server exit code: {server_result.exit_code}")
    print(f"Server output: {server_result.output.decode('utf-8')}")
    
    # If it failed, try starting in background and checking logs
    if server_result.exit_code != 0:
        print("Server failed, trying background approach...")
        
        # Start in background with output redirection
        start_result = container.exec_run(
            "bash -c 'java -Xms32m -Xmx128m -XX:+UseSerialGC -XX:TieredStopAtLevel=1 PersistentJavaRunner > server.log 2>&1 & echo $! > server.pid'",
            workdir="/tmp"
        )
        
        time.sleep(2)
        
        # Check logs
        log_result = container.exec_run("cat server.log", workdir="/tmp")
        print(f"Background server logs: {log_result.output.decode('utf-8')}")
        
        # Check PID
        pid_result = container.exec_run("cat server.pid", workdir="/tmp")
        print(f"PID file content: {pid_result.output.decode('utf-8')}")
    
    container.remove(force=True)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
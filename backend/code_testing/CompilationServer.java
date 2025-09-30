import java.io.*;
import java.net.*;
import java.util.*;
import javax.tools.*;
import java.net.URI;

/**
 * Persistent Java compilation server to eliminate JVM startup overhead.
 * Listens on port 8901 and compiles Java source code in memory.
 */
public class CompilationServer {
    private static final int PORT = 8901;
    private static final JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
    private static final StandardJavaFileManager fileManager = compiler.getStandardFileManager(null, null, null);
    
    public static void main(String[] args) {
        System.out.println("[COMPILATION SERVER] Starting Java compilation server on port " + PORT);
        
        if (compiler == null) {
            System.err.println("❌ [COMPILATION SERVER] No Java compiler available!");
            System.exit(1);
        }
        
        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            System.out.println("[COMPILATION SERVER] Server listening on port " + PORT);
            
            while (true) {
                try (Socket clientSocket = serverSocket.accept()) {
                    handleCompilationRequest(clientSocket);
                } catch (Exception e) {
                    System.err.println("❌ [COMPILATION SERVER] Error handling client: " + e.getMessage());
                    e.printStackTrace();
                }
            }
        } catch (IOException e) {
            System.err.println("❌ [COMPILATION SERVER] Failed to start server: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    private static void handleCompilationRequest(Socket clientSocket) throws IOException {
        BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        PrintWriter out = new PrintWriter(clientSocket.getOutputStream(), true);
        
        try {
            // Read source code length
            String lengthStr = in.readLine();
            if (lengthStr == null) {
                out.println("ERROR: No length specified");
                return;
            }
            
            int length = Integer.parseInt(lengthStr.trim());
            System.out.println("[COMPILATION SERVER] Receiving " + length + " characters of source code");

            // Read source code
            char[] buffer = new char[length];
            int totalRead = 0;
            while (totalRead < length) {
                int read = in.read(buffer, totalRead, length - totalRead);
                if (read == -1) {
                    throw new IOException("Unexpected end of stream");
                }
                totalRead += read;
            }
            
            String sourceCode = new String(buffer);
            System.out.println("[COMPILATION SERVER] Compiling source code...");
            
            // Compile the source code
            CompilationResult result = compileSource(sourceCode);
            
            if (result.success) {
                System.out.println(" [COMPILATION SERVER] Compilation successful");
                out.println("SUCCESS");
                out.println(result.outputPath);
            } else {
                System.out.println("❌ [COMPILATION SERVER] Compilation failed: " + result.error);
                out.println("ERROR");
                out.println(result.error);
            }
            
        } catch (Exception e) {
            System.err.println("❌ [COMPILATION SERVER] Error during compilation: " + e.getMessage());
            e.printStackTrace();
            out.println("ERROR");
            out.println("Internal server error: " + e.getMessage());
        }
    }
    
    private static CompilationResult compileSource(String sourceCode) {
        try {
            // Create a unique directory for this compilation
            String compilationId = "compile_" + System.currentTimeMillis() + "_" + Thread.currentThread().getId();
            String outputDir = "/tmp/" + compilationId;
            new File(outputDir).mkdirs();
            
            // Write source code to file (required for javac)
            File sourceFile = new File(outputDir, "Main.java");
            try (FileWriter writer = new FileWriter(sourceFile)) {
                writer.write(sourceCode);
            }
            
            // Set up compilation options
            List<String> options = Arrays.asList(
                "-cp", "/tmp",  // Set classpath
                "-d", outputDir,  // Output directory
                "-Xlint:none"  // Suppress warnings
            );
            
            // Compile
            Iterable<? extends JavaFileObject> compilationUnits = fileManager.getJavaFileObjectsFromFiles(Arrays.asList(sourceFile));
            DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
            
            JavaCompiler.CompilationTask task = compiler.getTask(
                null,  // Writer for additional output
                fileManager,  // File manager
                diagnostics,  // Diagnostic collector
                options,  // Compiler options
                null,  // Classes to process
                compilationUnits  // Source files
            );
            
            boolean success = task.call();
            
            if (success) {
                return new CompilationResult(true, outputDir, null);
            } else {
                // Collect compilation errors
                StringBuilder errorMsg = new StringBuilder();
                for (Diagnostic<? extends JavaFileObject> diagnostic : diagnostics.getDiagnostics()) {
                    errorMsg.append(diagnostic.getMessage(null)).append("\n");
                }
                return new CompilationResult(false, null, errorMsg.toString());
            }
            
        } catch (Exception e) {
            return new CompilationResult(false, null, "Compilation exception: " + e.getMessage());
        }
    }
    
    private static class CompilationResult {
        final boolean success;
        final String outputPath;
        final String error;
        
        CompilationResult(boolean success, String outputPath, String error) {
            this.success = success;
            this.outputPath = outputPath;
            this.error = error;
        }
    }
}
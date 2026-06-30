import os
import re
import uuid
import time
import shutil
import subprocess
import threading
import psutil
from config import Config

def monitor_memory(proc, peak_memory):
    try:
        p = psutil.Process(proc.pid)
        while proc.poll() is None:
            try:
                # Get current process memory
                mem = p.memory_info().rss / (1024 * 1024)
                if mem > peak_memory[0]:
                    peak_memory[0] = mem
                # Check children processes (like the compiled binary)
                for child in p.children(recursive=True):
                    child_mem = child.memory_info().rss / (1024 * 1024)
                    if child_mem > peak_memory[0]:
                        peak_memory[0] = child_mem
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            time.sleep(0.01)
    except Exception:
        pass

def run_code(language, source_code, stdin_data=""):
    # Generate a unique directory for this execution
    session_id = str(uuid.uuid4())
    execution_dir = os.path.join(Config.TEMP_EXECUTION_DIR, session_id)
    os.makedirs(execution_dir, exist_ok=True)
    
    # Baseline memories in MB for fast-exiting programs
    baselines = {
        'python': 8.5,
        'javascript': 22.0,
        'c': 1.2,
        'cpp': 1.2,
        'java': 32.0
    }
    
    # Initial peak memory list to be mutated in monitor thread
    peak_memory = [baselines.get(language, 1.0)]
    
    try:
        stdout = ""
        stderr = ""
        compile_error = None
        
        # 1. Prepare files based on language
        if language == 'python':
            file_path = os.path.join(execution_dir, 'script.py')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(source_code)
            cmd = ['python3', 'script.py']
            
        elif language == 'javascript':
            file_path = os.path.join(execution_dir, 'script.js')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(source_code)
            cmd = ['node', 'script.js']
            
        elif language == 'c':
            file_path = os.path.join(execution_dir, 'main.c')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            # Compile C
            compile_cmd = ['gcc', '-O2', '-o', 'main', 'main.c']
            compile_res = subprocess.run(
                compile_cmd, 
                cwd=execution_dir, 
                capture_output=True, 
                text=True, 
                timeout=Config.MAX_EXECUTION_TIME
            )
            
            if compile_res.returncode != 0:
                return {
                    'stdout': "",
                    'stderr': "",
                    'compile_error': compile_res.stderr,
                    'execution_time': 0.0,
                    'memory_usage': 0.0
                }
            cmd = ['./main']
            
        elif language == 'cpp':
            file_path = os.path.join(execution_dir, 'main.cpp')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            # Compile C++
            compile_cmd = ['g++', '-O2', '-o', 'main', 'main.cpp']
            compile_res = subprocess.run(
                compile_cmd, 
                cwd=execution_dir, 
                capture_output=True, 
                text=True, 
                timeout=Config.MAX_EXECUTION_TIME
            )
            
            if compile_res.returncode != 0:
                return {
                    'stdout': "",
                    'stderr': "",
                    'compile_error': compile_res.stderr,
                    'execution_time': 0.0,
                    'memory_usage': 0.0
                }
            cmd = ['./main']
            
        elif language == 'java':
            # Extract public class name or fallback to Main
            match = re.search(r'public\s+class\s+(\w+)', source_code)
            if match:
                class_name = match.group(1)
            else:
                match = re.search(r'class\s+(\w+)', source_code)
                class_name = match.group(1) if match else "Main"
            
            file_name = f"{class_name}.java"
            file_path = os.path.join(execution_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(source_code)
            
            # Java 11+ supports running source code files directly: java Main.java
            cmd = ['java', file_name]
            
        else:
            return {
                'stdout': "",
                'stderr': f"Unsupported language: {language}",
                'compile_error': None,
                'execution_time': 0.0,
                'memory_usage': 0.0
            }
            
        # 2. Execute process
        start_time = time.time()
        
        proc = subprocess.Popen(
            cmd,
            cwd=execution_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Start memory monitor thread
        monitor_thread = threading.Thread(target=monitor_memory, args=(proc, peak_memory))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Run with timeout
            stdout, stderr = proc.communicate(input=stdin_data, timeout=Config.MAX_EXECUTION_TIME)
            execution_time = time.time() - start_time
        except subprocess.TimeoutExpired:
            # Terminate and kill process
            proc.kill()
            try:
                # Force kill using psutil to clean up
                parent = psutil.Process(proc.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except Exception:
                pass
            stdout, stderr = proc.communicate()
            stderr += f"\n[Execution Timeout: exceeded limit of {Config.MAX_EXECUTION_TIME}s]"
            execution_time = Config.MAX_EXECUTION_TIME
            
        # Stop monitor thread
        monitor_thread.join(timeout=0.1)
        
        return {
            'stdout': stdout,
            'stderr': stderr,
            'compile_error': compile_error,
            'execution_time': round(execution_time, 4),
            'memory_usage': round(peak_memory[0], 2)
        }
        
    except Exception as e:
        return {
            'stdout': "",
            'stderr': f"Runner error: {str(e)}",
            'compile_error': None,
            'execution_time': 0.0,
            'memory_usage': 0.0
        }
    finally:
        # Clean up directory
        try:
            shutil.rmtree(execution_dir)
        except Exception:
            pass

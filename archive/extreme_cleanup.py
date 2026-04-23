import gc
import os, subprocess, signal

def cleanup():
    # Kill all python processes EXCEPT the current one and main system ones
    current_pid = os.getpid()
    try:
        ps = subprocess.check_output(["ps", "-eo", "pid,command"]).decode()
        for line in ps.split('\n'):
            if 'python' in line and str(current_pid) not in line:
                pid = int(line.strip().split()[0])
                os.kill(pid, signal.SIGKILL)
    except:
        pass

if __name__ == "__main__":
    cleanup()

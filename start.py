import subprocess
import time

while True:
    process = subprocess.Popen(["python3", "Main.py"])
    process.wait()
    print("Script crashed, restarting...")
    time.sleep(5)

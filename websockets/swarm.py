import subprocess

# Define the path to your script
script_path = "client.py"


# Function to run a single instance
def run_instance(index):
    try:
        result = subprocess.run(["python", script_path], capture_output=True, text=True)
        print(f"Instance {index} Output:\n{result.stdout}\n Error:\n{result.stderr}")
    except Exception as e:
        print(f"Error in instance {index}: {e}")


# Running 100 instances concurrently
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(run_instance, i) for i in range(1000)]

# You can also wait for all futures to complete if necessary
for future in futures:
    future.result()
    print("---")

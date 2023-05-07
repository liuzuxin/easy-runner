import sys
import time
import random

if __name__ == "__main__":
    script_name = sys.argv[1]
    seed = sys.argv[2]
    task = sys.argv[3]

    print(f"Starting {script_name} with seed {seed} for task {task}")

    # Simulate the training process
    training_duration = random.randint(100, 150)
    time.sleep(training_duration)

    print(f"Finished {script_name} with seed {seed} for task {task}")

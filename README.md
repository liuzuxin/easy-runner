# EasyRunner

EasyRunner is a lightweight tool for managing and executing multiple parallel experiments. It simplifies the process of running multiple experiments with different configurations or hyperparameters, while monitoring system resources.

## Features

- Run multiple experiments in parallel
- Monitor system resources (CPU and memory usage) during experiments
- Early termination of experiments by inputting the experiment number
- Colorized display of experiment status and resource usage
- Generate a list of instructions from a template and arguments

## Installation

To use EasyRunner, simply download or clone this repository to your local machine.

## Usage

1. Import the `EasyRunner` class from the `easy_runner.py` file.
2. Initialize an `EasyRunner` object with the required parameters.
3. Use the `start` method to run experiments.
4. Optionally, use the `compose` method to generate a list of instructions from a template and arguments.

Example:

```python
from easy_runner import EasyRunner

# Initialize the EasyRunner
runner = EasyRunner(log_name="experiment_logs")

# Create a list of instructions
instructions = [
    "python script1.py --param1 0.1 --param2 100",
    "python script1.py --param1 0.2 --param2 200",
    "python script2.py --param1 0.3 --param2 300",
    "python script2.py --param1 0.4 --param2 400",
    "python script3.py --param1 0.5 --param2 500"
]

# Run experiments
runner.start(instructions, gpus=[0], max_parallel=2)
```

Here's an example of how to use the `EasyRunner`:

```python
from easy_runner import EasyRunner

# Initialize the EasyRunner
runner = EasyRunner(log_name="experiment_logs")

# List of seeds, and tasks
seeds = [0, 10, 20]
tasks = ["TaskA-v0 --epoch 30", "TaskB-v0 --epoch 150", "TaskC-v0 --epoch 80"]

# Define the command template
template = "nohup python train_script.py --project my_project --seed {} --task {} "

# Generate a list of instructions using the compose method
instructions = runner.compose(template, [agents, seeds, tasks])

# Run the experiments
runner.start(instructions, max_parallel=4)
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions to the Experiment Grid Tool. Please open an issue or submit a pull request on the GitHub repository.


Feel free to customize this template according to your specific requirements or add any additional information you think would be helpful for users.
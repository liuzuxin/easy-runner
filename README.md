<div align="center">
  <h2>EasyRunner: Smoother Parallel Experiments</h2>
</div>
<div align="center">

  <a>![Python 3.8+](https://img.shields.io/badge/Python-3.6%2B-brightgreen.svg)</a>
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](#license)
  [![PyPI](https://img.shields.io/pypi/v/easy-runner?logo=pypi)](https://pypi.org/project/easy-runner)
  <!-- [![Downloads](https://static.pepy.tech/personalized-badge/easy-runner?period=total&left_color=grey&right_color=blue&left_text=downloads)](https://pepy.tech/project/easy-runner) -->
  <!-- [![GitHub Repo Stars](https://img.shields.io/github/stars/liuzuxin/dsrl?color=brightgreen&logo=github)](https://github.com/liuzuxin/dsrl/stargazers) -->
  <!-- [![Documentation Status](https://img.shields.io/readthedocs/fsrl?logo=readthedocs)](https://fsrl.readthedocs.io) -->
  <!-- [![CodeCov](https://codecov.io/github/liuzuxin/fsrl/branch/main/graph/badge.svg?token=BU27LTW9F3)](https://codecov.io/github/liuzuxin/fsrl)
  [![Tests](https://github.com/liuzuxin/fsrl/actions/workflows/test.yml/badge.svg)](https://github.com/liuzuxin/fsrl/actions/workflows/test.yml) -->
  <!-- [![CodeCov](https://img.shields.io/codecov/c/github/liuzuxin/fsrl/main?logo=codecov)](https://app.codecov.io/gh/liuzuxin/fsrl) -->
  <!-- [![tests](https://img.shields.io/github/actions/workflow/status/liuzuxin/fsrl/test.yml?label=tests&logo=github)](https://github.com/liuzuxin/fsrl/tree/HEAD/tests) -->
  
</div>

EasyRunner is a lightweight tool for managing and executing multiple parallel experiments with minimum dependencies. It simplifies the process of running multiple experiments with different configurations or hyperparameters, while monitoring system resources.

## Features

- Run multiple experiments in parallel
- Simple dependencies. It only depends on `prettytable` and `psutil` library. So you can basically use this for any platforms.
- Monitor system resources (CPU and memory usage) during experiments
- Early termination of experiments by inputting the experiment number
- Colorized display of experiment status and resource usage
- Generate a list of instructions from a template and arguments

## Installation

The simpliest way is to install via [PyPI](https://pypi.org/project/easy-runner).

```
pip install easy_runner
```

Alternatively, you can also install from source, simply download or clone this repository and then:

```
git clone https://github.com/liuzuxin/easy-runner.git
cd easy-runner
pip install -e .
```

## Usage

1. Initialize an `EasyRunner` object with the required parameters.
2. Specificy a list of commandline instructions to run.
3. Use the `start` method to run experiments. You can specify a list of GPU IDs for running experiments (or `None` by default).
3. Optionally, use the `compose` method to generate a list of instructions from a template and arguments.

A simple example for running a list of instructions (2 parallel) on cuda 0, 1:

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
runner.start(instructions, gpus=[0, 1], max_parallel=2)
```

Anoter example of how to use the `compose` feature to perform grid search:

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

You can try the example scripts in the `examples` folder:
```bash
cd examples
python test_easy_runner.py
```

Demo video:
<div align="center">
  <img width="600px" height="auto" src="https://github.com/liuzuxin/easy-runner/raw/main/examples/demo.gif">
</div>

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

There are still a lot of improvements could be done for this tool.
We welcome any contributions to this project. Please open an issue or submit a pull request on the GitHub repository.

Feel free to customize this template according to your specific requirements or add any additional information you think would be helpful for users.

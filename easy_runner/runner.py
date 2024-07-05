# flake8: noqa

import datetime
import itertools
import os
import select
import signal
import subprocess
import sys
import threading
import time
from collections import defaultdict
from typing import List, Optional

import psutil
from prettytable import PrettyTable

color2num = dict(
    gray=30,
    red=31,
    green=32,
    yellow=33,
    blue=34,
    magenta=35,
    cyan=36,
    white=37,
    crimson=38
)


def colorize(string, color, bold=False, highlight=False):
    """Colorize a string.
    This function was originally written by John Schulman.
    """
    attr = []
    num = color2num[color]
    if highlight: num += 10
    attr.append(str(num))
    if bold: attr.append('1')
    return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)


def get_cpu_usage():
    cpu_percent = psutil.cpu_percent()
    total_cpus = psutil.cpu_count()
    return f"{cpu_percent}%, {cpu_percent/100*total_cpus:.1f} / {total_cpus} CPUs"


def get_memory_usage():
    memory = psutil.virtual_memory()
    return f"{memory.used / (1024 ** 3):.1f}/{memory.total / (1024 ** 3):.1f} GiB"


def get_cmd_resource_usage(processes):
    cmd_cpu_percent = 0
    cmd_memory_percent = 0
    for exp_num, (p, _, _, terminated, finished) in list(processes.items()):
        if not terminated and not finished and p.poll() is None:
            try:
                process = psutil.Process(p.pid)
                children = process.children(recursive=True)
                for child in children:
                    cmd_cpu_percent += child.cpu_percent(interval=0.01)
                    cmd_memory_percent += child.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    total_cpus = psutil.cpu_count()
    memory = psutil.virtual_memory()
    cmd_cpu_usage = f"{cmd_cpu_percent/total_cpus:.1f}%, {cmd_cpu_percent/100:.1f} / {total_cpus} CPUs"
    cmd_memory_usage = f"{cmd_memory_percent * memory.total / (100 * (1024 ** 3)):.1f}/{memory.total / (1024 ** 3):.1f} GiB"
    return cmd_cpu_usage, cmd_memory_usage


class EasyRunner:
    """
    EasyRunner is a lightweight tool for running multiple scripts in parallel.
    """

    DISPLAY_MODES = ["running_only", "full"]

    def __init__(
        self,
        log_name=None,
        mode: int = 0,
        refresh: bool = True,
        refresh_time: float = 2
    ) -> None:
        """
        Initializes the EasyRunner.
        
        :param log_name: The name of the log directory, defaults to None.
        :type log_name: str, optional
        :param mode: The display mode for the console, defaults to 0.
        :type mode: int, optional
        :param refresh: Whether to refresh the console output, defaults to True.
        :type refresh: bool, optional
        :param refresh_time: The refresh interval for the console output, defaults to 2.
        :type refresh_time: float, optional
        """

        self.log_root = log_name or datetime.datetime.now().strftime("%m-%d_%H-%M-%S")
        os.makedirs(os.path.join(os.getcwd(), 'logs', self.log_root), exist_ok=True)
        self.log_root = os.path.join(os.getcwd(), 'logs', self.log_root)
        self.mode = mode
        self.refresh = refresh
        self.refresh_time = refresh_time

    def start(
        self,
        instructions: List[str],
        exp_names: Optional[List[str]] = None,
        gpus: Optional[List[int]] = None,
        max_parallel: int = 1
    ):
        """
        Starts running the experiments.
        
        :param instructions: A list of instructions for the experiments.
        :type instructions: List[str]
        :param gpus: A list of GPU IDs to use, defaults to [0].
        :type gpus: List[int], optional
        :param max_parallel: The maximum number of parallel experiments, defaults to 1.
        :type max_parallel: int, optional
        """

        self.start_time = datetime.datetime.now()
        self.main_process_active = True
        self.running_experiments = 0
        self.terminated_experiments = 0
        self.finished_experiments = 0
        signal.signal(signal.SIGINT, self.signal_handler)

        threads = [
            threading.Thread(
                target=self.run_command_thread,
                args=(instructions, exp_names, gpus, max_parallel),
                daemon=True
            ),
            threading.Thread(target=self.display_thread, daemon=True),
            threading.Thread(target=self.input_handler, daemon=True),
        ]

        for t in threads:
            t.start()

        while any(t.is_alive() for t in threads):
            for t in threads:
                t.join(timeout=1)

    def signal_handler(self, signum, frame):
        print("Ctrl+C detected. Terminating all experiments.")
        self.main_process_active = False
        self.terminate_all_experiments()

    def input_handler(self):
        # print("Enter the experiment number to kill or 'q' to quit:")
        while self.main_process_active:
            # Check if there's input available within the specified timeout (2 second)
            inputs, _, _ = select.select([sys.stdin], [], [], 2)
            if inputs:
                exp_num = sys.stdin.readline().strip()
                if exp_num.lower() == 'q':
                    self.terminate_all_experiments()
                    break
                elif exp_num.lower() == 'n':
                    self.mode += 1
                elif exp_num.lower() == 'p':
                    self.mode -= 1
                else:
                    self.terminate_experiment(exp_num)
            if self.all_experiment_done():
                break
        self.main_process_active = False

    def check_process_status(self):
        for exp_num, (p, command, start_time, terminated,
                      finished) in self.processes.items():
            status_code = p.poll()
            if status_code is None or terminated or finished:
                continue
            if status_code >= 0:
                # finished
                self.processes[exp_num] = (p, command, start_time, terminated, True)
                self.running_experiments -= 1
                self.finished_experiments += 1

    def all_experiment_done(self):
        return self.finished_experiments + self.terminated_experiments >= self.num_exp

    def run_command_thread(
        self,
        instructions: List[str],
        exp_names: Optional[List[str]] = None,
        gpus: Optional[List[int]] = None,
        max_parallel: int = 1
    ) -> None:

        self.num_exp = len(instructions)
        self.processes = {}
        exp_names = exp_names if exp_names is not None else [f"exp_{i}" for i in range(self.num_exp)]
        num_gpu = len(gpus) if gpus is not None else 1

        for i, ins in enumerate(instructions):
            while self.running_experiments >= max_parallel and self.main_process_active:
                time.sleep(1)
                self.check_process_status()

            if not self.main_process_active:
                break

            print(f"\033[92mRunning experiment {i}\033[0m: {ins}")
            if gpus is None:
                redirect = f"> {self.log_root}/{exp_names[i]}_cpu.out"
                cuda_prefix = ""
            else:
                redirect = f"> {self.log_root}/{exp_names[i]}_gpu{gpus[i % num_gpu]}.out"
                cuda_prefix = f"CUDA_VISIBLE_DEVICES={gpus[i % num_gpu]} "
            command = cuda_prefix + f"{instructions[i]} {redirect}"
            p = subprocess.Popen(command, shell=True, preexec_fn=os.setsid)
            start_time = datetime.datetime.now()
            # a tuple to store the status of the process, the last two represent
            # termination and finish status
            self.processes[i] = (p, instructions[i], start_time, False, False)
            self.running_experiments += 1

        while self.running_experiments > 0:
            time.sleep(1)
            self.check_process_status()
            if not self.main_process_active:
                break

    def terminate_experiment(self, exp_num):
        try:
            exp_num = int(exp_num)
            if exp_num in self.processes:
                p, command, start_time, terminated, finished = self.processes[exp_num]
                if not terminated and not finished:
                    os.killpg(
                        os.getpgid(p.pid), signal.SIGTERM
                    )  # Send SIGTERM signal to the process group
                    print(f"Experiment {exp_num} with PID {p.pid} terminated.")
                    self.processes[exp_num] = (
                        p, command, start_time, True, finished
                    )  # Update the flag to indicate the experiment has been terminated
                    self.terminated_experiments += 1
                    self.running_experiments -= 1
                elif terminated:
                    print(f"Experiment {exp_num} has already been terminated.")
                else:
                    print(f"Experiment {exp_num} has already finished.")
            else:
                print(
                    "Invalid experiment number. Please enter a valid experiment number or 'q' to quit."
                )
        except ValueError:
            print(
                "Invalid input. Please enter a valid experiment number or 'q' to quit."
            )

    def terminate_all_experiments(self):
        print("Terminating all experiments...")
        for exp_num, (p, _, _, terminated, finished) in self.processes.items():
            self.terminate_experiment(exp_num)
        # sys.exit(1)

    @staticmethod
    def format_time(delta):
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:03d}h {minutes:02d}m {seconds:02d}s"

    def display_thread(self):
        self.process_running_time = defaultdict(int)
        time.sleep(self.refresh_time)

        while True:
            current_time = datetime.datetime.now()
            formatted_running_time = self.format_time(current_time - self.start_time)
            cpu_usage, memory_usage = get_cpu_usage(), get_memory_usage()
            cmd_cpu_usage, cmd_memory_usage = get_cmd_resource_usage(self.processes)

            if self.refresh:
                os.system("clear")
            print("== Status ==")
            print(f"Current time: {current_time} (running for {formatted_running_time})")
            print(f"System CPU usage: {cpu_usage}; Memory usage: {memory_usage}")
            print(f"Resource usage by this node: {cmd_cpu_usage}, {cmd_memory_usage}")

            print(f"Result logdir: {self.log_root}")
            print(
                f"Number of experiments: {self.running_experiments + self.terminated_experiments + self.finished_experiments}/{self.num_exp} ({self.finished_experiments} FINISHED, {self.terminated_experiments} TERMINATED, {self.running_experiments} RUNNING)"
            )

            final_display = not self.main_process_active or self.all_experiment_done()

            display_mode = self.DISPLAY_MODES[self.mode % len(self.DISPLAY_MODES)]

            if display_mode == "running_only" and not final_display:
                self.print_running_summarization(current_time)
            else:
                self.print_all_summarization(current_time)

            if final_display:
                break
            else:
                print(
                    colorize(
                        "You can early terminate the experiment by entering the ID number or `q` for kill all:",
                        "magenta"
                    )
                )

            time.sleep(self.refresh_time)

    def print_all_summarization(self, current_time):
        table = PrettyTable()
        table.field_names = [
            colorize("Exp ID", "green"),
            colorize("Command", "cyan"),
            colorize("Running Time", "yellow"),
            colorize("Status", "magenta")
        ]

        for exp_num, (p, command, start_time, terminated,
                      finished) in self.processes.items():
            if terminated:
                status = "TERMINATED"
            elif finished:
                status = "FINISHED"
            else:
                status = "RUNNING"
                running_time = current_time - start_time
                self.process_running_time[exp_num] = self.format_time(running_time)
            
            if len(command) > 10:
                command = command[:10] + "..."

            table.add_row(
                [
                    colorize(f"Exp {exp_num}", "green"),
                    colorize(command, "cyan"),
                    colorize(self.process_running_time[exp_num], "yellow"),
                    colorize(status, "magenta")
                ]
            )
        print(table)

    def print_running_summarization(self, current_time):
        table = PrettyTable()
        table.field_names = [
            colorize("Exp ID", "green"),
            colorize("Command", "cyan"),
            colorize("Running Time", "yellow"),
        ]

        for exp_num, (p, command, start_time, terminated,
                      finished) in self.processes.items():
            if terminated or finished:
                continue
            running_time = current_time - start_time
            self.process_running_time[exp_num] = self.format_time(running_time)

            if len(command) > 10:
                command = command[:10] + "..."
            
            table.add_row(
                [
                    colorize(f"Exp {exp_num}", "green"),
                    colorize(command, "cyan"),
                    colorize(self.process_running_time[exp_num], "yellow")
                ]
            )
        print(table)

    def compose(self, template: str, args: List[List]) -> List[str]:
        """
        Generate a list of instructions from a template and arguments.

        :param template: The template of the instruction in the form of a format string.
        :type template: str
        :param args: The list of arguments for each instruction.
        :type args: List[List]
        :return: The list of instructions ready to run.
        :rtype: List[str]
        """

        all_combinations = list(itertools.product(*args))
        return [template.format(*combination) for combination in all_combinations]

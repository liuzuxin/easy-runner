from easy_runner import EasyRunner

if __name__ == "__main__":
    runner = EasyRunner(log_name="test_logs")

    script_name = [
        "dummy_train.py",
    ]
    seed = [0, 10, 20]
    task = [
        "TaskA",
        "TaskB",
    ]
    config = [0.1]

    template = "python {} {} {} {}"

    train_instructions = runner.compose(template, [script_name, seed, task, config])
    runner.start(train_instructions, max_parallel=4)

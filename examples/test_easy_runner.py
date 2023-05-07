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

    template = "python {} {} {} {}"

    train_instructions = runner.compose(template, [script_name, seed, task])
    runner.start(train_instructions, max_parallel=4)

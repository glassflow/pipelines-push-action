import os


def set_outputs(outputs: dict):
    """Write outputs to GITHUB_OUTPUT environment variable"""
    for k, v in outputs.items():
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            fh.write(f"{k}={v}\n")

from pathlib import Path

import pytest


@pytest.fixture
def yaml_file():
    return Path("tests/data/pipeline.yaml")


@pytest.fixture
def pipeline_yaml(yaml_file):
    return

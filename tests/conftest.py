from pathlib import Path

import pytest

from pipelines_push_action.yaml_utils import load_yaml_file


@pytest.fixture
def yaml_file():
    return Path("tests/data/pipeline.yaml")


@pytest.fixture
def pipeline_yaml(yaml_file):
    return load_yaml_file(yaml_file)

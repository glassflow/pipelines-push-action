import filecmp
from pathlib import Path

from pipelines_push_action import yaml_utils


def test_load_yaml_file(yaml_file):
    pipeline = yaml_utils.load_yaml_file(yaml_file)

    assert pipeline.pipeline_id is None
    assert pipeline.space_id == "my-space-id"


def test_save_yaml(yaml_file):
    original_file_data = yaml_utils.open_yaml(yaml_file)
    new_file = Path("tests/data/pipeline_new.yaml")

    try:
        yaml_utils.save_yaml(new_file, original_file_data)
        assert filecmp.cmp(yaml_file, new_file)
    finally:
        new_file.unlink()


def test_update_pipeline_id_in_yaml(yaml_file):
    pipeline = yaml_utils.load_yaml_file(yaml_file)
    new_file = Path("tests/data/pipeline_new.yaml")
    pipeline.pipeline_id = "test-pipeline-id"
    try:
        yaml_utils.update_pipeline_id_in_yaml(pipeline.pipeline_id, yaml_file, new_file)
        new_pipeline = yaml_utils.load_yaml_file(new_file)
        assert new_pipeline.pipeline_id == pipeline.pipeline_id
    finally:
        new_file.unlink()


def test_update_space_id_in_yaml(yaml_file):
    pipeline = yaml_utils.load_yaml_file(yaml_file)
    new_file = Path("tests/data/pipeline_new.yaml")
    pipeline.space_id = "new-space-id"
    try:
        yaml_utils.update_space_id_in_yaml(pipeline.space_id, yaml_file, new_file)
        new_pipeline = yaml_utils.load_yaml_file(new_file)
        assert new_pipeline.space_id == pipeline.space_id
    finally:
        new_file.unlink()


def test_map_yaml_to_files(yaml_file):
    mappings = yaml_utils.map_yaml_to_files(Path(yaml_file.parent))
    assert mappings == {
        yaml_file: [
            Path("tests/data/requirements.txt"),
            Path("tests/data/handler.py"),
        ]
    }


def test_yaml_file_to_pipeline_ok(yaml_file, pipeline_yaml):
    pipeline = yaml_utils.yaml_file_to_pipeline(
        pipeline_file=yaml_file,
        pipeline=pipeline_yaml,
        personal_access_token="my-personal-access-token",
    )
    assert pipeline.name == "Pipeline with shared code 1"
    assert pipeline.metadata == {"view_only": True}
    assert pipeline.source_config

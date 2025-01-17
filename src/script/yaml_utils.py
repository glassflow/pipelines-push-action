import itertools
from pathlib import Path

from yaml import safe_load
from glassflow import Pipeline as GlassFlowPipeline

from models import Pipeline


def load_yaml_file(file):
    """Loads Pipeline YAML file"""
    # Load YAML
    with open(file) as f:
        yaml_data = safe_load(f)

    return Pipeline(**yaml_data)


def map_yaml_to_files(path: Path) -> dict[Path, list[Path]]:
    """Maps Pipeline YAML files to .py and requirements.txt files"""
    yml_files = itertools.chain(path.rglob("*.yaml"), path.rglob("*.yml"))
    mapping = {}
    for file in yml_files:
        mapping[file] = []
        for c in load_yaml_file(file).components:
            if c.type == "transformer":
                transformer = c
                break
        else:
            continue

        if (
                transformer.requirements is not None and
                transformer.requirements.path is not None
        ):
            path = file.parent / transformer.requirements.path
            mapping[file].append(path)

        if transformer.transformation.path is not None:
            path = file.parent / transformer.transformation.path
            mapping[file].append(path)
    return mapping


def yaml_file_to_pipeline(
    pipeline_file: Path, pipeline: Pipeline, personal_access_token: str
) -> GlassFlowPipeline:
    """
    Converts a Pipeline YAML file into GlassFlow SDK Pipeline
    """
    yaml_file_dir = pipeline_file.parent

    # We have one source, transformer and sink components
    source = [c for c in pipeline.components if c.type == "source"][0]
    transformer = [c for c in pipeline.components if c.type == "transformer"][0]
    sink = [c for c in pipeline.components if c.type == "sink"][0]

    if transformer.requirements is not None:
        if transformer.requirements.value is not None:
            requirements = transformer.requirements.value
        else:
            with open(yaml_file_dir / transformer.requirements.path) as f:
                requirements = f.read()
    else:
        requirements = None

    if transformer.transformation.path is not None:
        transform = str(yaml_file_dir / transformer.transformation.path)
    else:
        transform = str(yaml_file_dir / "handler.py")
        with open(transform, "w") as f:
            f.write(transformer.transformation.value)

    pipeline_id = pipeline.pipeline_id if pipeline.pipeline_id is not None else None
    space_id = pipeline.space_id if pipeline.space_id is not None else None

    if transformer.env_vars is not None:
        env_vars = [e.model_dump(exclude_none=True) for e in transformer.env_vars]
    else:
        env_vars = None

    # TODO: Handle source and sink config_secret_ref
    # TODO: Handle env_var value_secret_ref
    return GlassFlowPipeline(
        personal_access_token=personal_access_token,
        id=pipeline_id,
        name=pipeline.name,
        space_id=space_id,
        env_vars=env_vars,
        transformation_file=transform,
        requirements=requirements,
        sink_kind=sink.kind,
        sink_config=sink.config,
        source_kind=source.kind,
        source_config=source.config,
    )


def add_pipeline_id_to_yaml(yaml_path: Path, pipeline_id: str):
    """Prepend the pipeline id to the yaml file"""
    with open(yaml_path, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"pipeline_id: {pipeline_id}" + "\n" + content)


def add_space_id_to_yaml(yaml_path: Path, space_id: str):
    """Prepend the space id to the yaml file"""
    with open(yaml_path, "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write(f"space_id: {space_id}" + "\n" + content)
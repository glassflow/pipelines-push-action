import itertools
from pathlib import Path
from typing import Any

import ruamel.yaml
from glassflow import Pipeline as GlassFlowPipeline

from pipelines_push_action.errors import YAMLFileEmptyError
from pipelines_push_action.models import Pipeline


def load_yaml_file(file):
    """Loads Pipeline YAML file"""
    # Load YAML
    yaml_data = open_yaml(file)
    return Pipeline(**yaml_data)


def open_yaml(path: Path) -> dict[str, Any]:
    """Opens a yaml file... Nothing too exciting there.

    Args:
        path (Path): Full filename path pointing to the yaml file we want to open.

    Returns:
        Dict[str, Any]: A python dict containing the content from the yaml file.
    """
    if path.is_file():
        with open(path, "r") as stream:
            ryaml = ruamel.yaml.YAML(typ="rt")
            yaml_dict = ryaml.load(stream)
            if yaml_dict:
                return yaml_dict
            raise YAMLFileEmptyError(f"The following file {path.resolve()} seems empty.")
    raise FileNotFoundError(f"File {path.resolve()} was not found.")


def save_yaml(path: Path, data: dict[str, Any]) -> None:
    """Saves a YAML content.

    Args:
        path (Path): Full filename path pointing to the yaml file we want to save.
        data (dict[str, Any]): Data to save in the file.
    """
    with open(path, "w") as outfile:
        ryaml = ruamel.yaml.YAML(typ="rt")
        ryaml.width = 100
        ryaml.indent(mapping=2, sequence=4, offset=2)
        ryaml.dump(data, outfile)


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
        metadata={"view_only": True},
    )


def pipeline_to_yaml(pipeline: Pipeline, input_yaml: Path, output_yaml: Path = None) -> None:
    yaml_data = open_yaml(input_yaml)

    pipeline_dict = pipeline.model_dump(exclude_none=True)

    yaml_data["pipeline_id"] = pipeline.pipeline_id
    yaml_data["space_id"] = pipeline.space_id
    yaml_data["name"] = pipeline.name
    for idx, c in enumerate(pipeline_dict["components"]):
        yaml_data["components"][idx].update(c)

    if output_yaml is not None:
        save_yaml(output_yaml, yaml_data)
    else:
        save_yaml(input_yaml, yaml_data)

def update_pipeline_id_in_yaml(pipeline_id: str, input_yaml: Path, output_yaml: Path = None) -> None:
    """Update the pipeline id to the yaml file"""
    yaml_data = open_yaml(input_yaml)
    yaml_data["pipeline_id"] = pipeline_id

    if output_yaml is not None:
        save_yaml(output_yaml, yaml_data)
    else:
        save_yaml(input_yaml, yaml_data)


def update_space_id_in_yaml(space_id: str, input_yaml: Path, output_yaml: Path = None) -> None:
    """Update the space id to the yaml file"""
    yaml_data = open_yaml(input_yaml)
    yaml_data["space_id"] = space_id

    if output_yaml is not None:
        save_yaml(output_yaml, yaml_data)
    else:
        save_yaml(input_yaml, yaml_data)
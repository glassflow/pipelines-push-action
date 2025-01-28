import argparse
import logging
import sys
from pathlib import Path

from glassflow import GlassFlowClient

from pipelines_push_action.github_utils import set_outputs
from pipelines_push_action.yaml_utils import (
    load_yaml_file,
    map_yaml_to_files,
    yaml_file_to_pipeline,
    update_pipeline_id_in_yaml,
    update_space_id_in_yaml
)

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def generate_outputs(
    changes: dict
):
    """Returns a dictionary of changes that will be applied"""
    to_create = len(changes["to_create"])
    to_update = len(changes["to_update"])
    to_update_ids = " ".join([p["pipeline"].pipeline_id for p in changes["to_update"]])
    to_delete = len(changes["to_delete"])
    to_delete_ids = " ".join([p["pipeline"].pipeline_id for p in changes["to_delete"]])
    spaces_to_create = len(changes["spaces_to_create"])

    message = f"""
Expected changes on your GlassFlow pipelines:
\t‣ Create {to_create} pipelines
\t‣ Update {to_update} pipelines {"" if to_update == 0 else f'(IDs: {to_update_ids})'}
\t‣ Delete {to_delete} pipelines {"" if to_update == 0 else f'(IDs: {to_delete_ids})'}
    """
    spaces_to_create_count = len(changes["spaces_to_create"])
    if spaces_to_create_count > 0:
        spaces_to_create_names = [s["name"] for s in changes["spaces_to_create"]]
        message += (f"\nThe following {spaces_to_create_count} "
                    f"new spaces will be created: {' '.join(spaces_to_create_names)}")

    log.info(message)
    set_outputs({
        "to-create-count": to_create,
        "to-update-count": to_update,
        "to-update-ids": to_update_ids,
        "to-delete-count": to_delete,
        "to-delete-ids": to_delete_ids,
        "space-to-create-count": spaces_to_create,
    })


def create_pipelines(to_create, client: GlassFlowClient) -> list[str]:
    new_pipeline_ids = []
    for change in to_create:
        pipeline = change["pipeline"]
        file = change["file"]
        gf_pipeline = yaml_file_to_pipeline(
            pipeline_file=file,
            pipeline=pipeline,
            personal_access_token=client.personal_access_token
        )

        new_pipeline = gf_pipeline.create()
        new_pipeline_ids.append(new_pipeline.id)
        update_pipeline_id_in_yaml(input_yaml=file, pipeline_id=new_pipeline.id)
        log.info(f"Created pipeline {new_pipeline.id}")
    return new_pipeline_ids


def update_pipelines(to_update, client: GlassFlowClient) -> None:
    for change in to_update:
        pipeline = change["pipeline"]
        file = change["file"]
        gf_pipeline = yaml_file_to_pipeline(
            pipeline_file=file,
            pipeline=pipeline,
            personal_access_token=client.personal_access_token
        )

        existing_pipeline = client.get_pipeline(gf_pipeline.id)
        existing_pipeline.update(
            name=gf_pipeline.name,
            transformation_file=gf_pipeline.transformation_file,
            requirements=gf_pipeline.requirements,
            sink_kind=gf_pipeline.sink_kind,
            sink_config=gf_pipeline.sink_config,
            source_kind=gf_pipeline.source_kind,
            source_config=gf_pipeline.source_config,
            env_vars=gf_pipeline.env_vars,
        )
        log.info(f"Updated pipeline {gf_pipeline.id}")


def delete_pipelines(to_delete, client: GlassFlowClient) -> None:
    for d in to_delete:
        file = d["file"]
        pipeline = d["pipeline"]

        if file.suffix in [".yaml", ".yml"]:
            p = client.get_pipeline(pipeline_id=pipeline.pipeline_id)
            p.delete()
            log.info(f"Deleted pipeline {p.id}")


def create_spaces(to_create, client: GlassFlowClient) -> dict[Path, str]:
    new_spaces = {}
    for change in to_create:
        name = change["name"]
        file = change["file"]

        space = client.create_space(name)
        new_spaces[file] = space.id
        update_space_id_in_yaml(space_id=space.id, input_yaml=file)
    return new_spaces


def get_pipelines_to_change(
    files_deleted: list[Path],
    files_changed: list[Path],
    pipelines_dir: Path
) -> dict:
    """Returns a dictionary of changes that will be applied"""
    pipeline_2_files = map_yaml_to_files(pipelines_dir)

    pipelines_changed = set()
    for file in files_changed:
        if file.suffix in [".yaml", ".yml"]:
            pipelines_changed.add(file)
        elif file.suffix == ".py" or file.name == "requirements.txt":
            for k in pipeline_2_files:
                if file in pipeline_2_files[k]:
                    pipelines_changed.add(k)
        else:
            continue

    to_create = []
    to_update = []
    spaces_to_create = []
    for file in pipelines_changed:
        p = load_yaml_file(file)
        if p.pipeline_id is not None:
            to_update.append({"file": file, "pipeline": p})
        else:
            to_create.append({"file": file, "pipeline": p})

        if p.space_id is None:
            spaces_to_create.append({"file": file, "name": p.space_name})

    to_delete = []
    for file in files_deleted:
        if file.suffix not in [".yaml", ".yml"]:
            continue

        try:
            p = load_yaml_file(file)
            to_delete.append({"file": file, "pipeline": p})
        except Exception as e:
            log.error(e)
        finally:
            file.unlink()

    return {
        "to_create": to_create,
        "to_update": to_update,
        "to_delete": to_delete,
        "spaces_to_create": spaces_to_create,
    }


def push_to_cloud(
    files_changed: list[Path],
    files_deleted: list[Path],
    pipelines_dir: Path,
    client: GlassFlowClient,
    dry_run: bool = False,
):
    changes = get_pipelines_to_change(files_deleted, files_changed, pipelines_dir)
    generate_outputs(changes)
    if dry_run:
        log.info("This is a dry run. No changes will be applied.")
        exit(0)

    new_spaces = create_spaces(changes["spaces_to_create"], client)
    # Update space_id in pipelines to create
    for idx, change in enumerate(changes["to_create"]):
        if change["file"] in new_spaces:
            pipeline = change["pipeline"]
            pipeline.space_id = new_spaces[change["file"]]
            changes["to_create"][idx]["pipeline"] = pipeline

    new_pipeline_ids = create_pipelines(changes["to_create"], client)
    update_pipelines(changes["to_update"], client)
    delete_pipelines(changes["to_delete"], client)

    if new_pipeline_ids:
        set_outputs({"to-create-ids": " ".join(new_pipeline_ids)})

    if new_spaces:
        set_outputs({"spaces-to-create-ids": " ".join(new_spaces.values())})


def main():
    parser = argparse.ArgumentParser("Push pipelines configuration to GlassFlow cloud")
    parser.add_argument(
        "-d",
        "--files-deleted",
        help="List of files that were deleted (`.yaml`, `.yml`, `.py` or "
        "`requirements.txt`) to sync to GlassFlow.",
        type=Path,
        nargs="+",
    )
    parser.add_argument(
        "-a",
        "--files-changed",
        help="List of files with changes (`.yaml`, `.yml`, `.py` or "
        "`requirements.txt`) to sync to GlassFlow.",
        type=Path,
        nargs="+",
    )
    parser.add_argument(
        "--root-dir",
        help="Github Root directory",
        type=Path,
        default="."
    )
    parser.add_argument(
        "--pipelines-dir",
        help="Path to directory with your GlassFlow pipelines.",
        type=Path,
        default="pipelines",
    )
    parser.add_argument(
        "-t",
        "--personal-access-token",
        help="GlassFlow Personal Access Token.",
        type=str,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        required=False,
        help="If set to True, no changes will be push to GlassFlow.",
    )
    args = parser.parse_args()

    files_deleted = args.files_deleted if args.files_deleted else []
    files_changed = args.files_changed if args.files_changed else []
    client = GlassFlowClient(personal_access_token=args.personal_access_token)
    push_to_cloud(
        files_deleted=files_deleted,
        files_changed=files_changed,
        pipelines_dir=args.pipelines_dir,
        client=client,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()

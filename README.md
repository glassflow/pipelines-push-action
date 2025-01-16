# pipelines-push-action

This Github Action lets you automate GlassFlow pipelines deployments as code.

This GA does:
- Get all the files changed since last commit (using https://github.com/marketplace/actions/changed-files)
  - changes on `*.yaml`, `*.py` and `requirements.txt` files
- Update all the pipelines with changes
  - If the YAML has `pipeline_id`, the action will update the pipeline with the new configuration (assume the pipeline exists, it fails otherwise).
  - If the YAML does not include the `pipeline_id`, it will create a new pipeline and update the YAML to add the `pipeline_id`.
- Delete all pipelines which YAML file has been deleted


## Usage

```yaml
name: Push to GlassFlow
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: glassflow/pipelines-push-action@v1
        with:
          glassflow-personal-access-token: ${{ secrets.GlassFlowPAT }}
```

## Inputs

- **glassflow-personal-access-token** _(required)_ - GlassFlow Personal Access Token (can be found in your profile https://app.glassflow.dev/profile). Use Github secrets to store your GlassFlow Personal Access Token.
- **pipelines-dir** _(optional)_ - The directory containing your pipelines (Default: `'pipelines'`).
- **dry-run** _(optional)_ - If set to 'true' the action will not push changes to GlassFlow (Default: `'false'`).

## Outputs

- **to-create-count** - Number of new pipelines to create.
- **to-create-ids** - Pipeline IDs that are created (only available if input `dry-run` is `false`).
- **to-update-count** - Number of pipelines to update.
- **to-update-ids** - Pipeline IDs that will be updated.
- **to-delete-count** - Number of pipelines to delete.
- **to-delete-ids** - Pipeline IDs that will be deleted.

## Notes

- **What happens if a pipeline was deleted from the Webapp and changes are introduced in the pipeline's YAML?**: The action will fail since the `pipeline_id` from the YAML will not exist in GlassFlow anymore
- **What happens if I update a pipeline in the Webapp?**: This GA action only syncs from YAML to GlassFlow, not the other way around. So if a pipeline is modified in the webapp, the changes might be overwritten next time you add changes to the pipeline's YAML, handler or requirements files.

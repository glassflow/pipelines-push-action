# pipelines-push-action

This Github Action lets you automate GlassFlow pipelines deployments as code.

This Github Action does:

- **Track Changes in your Pipelines**: Get all the files changed since last commit (using https://github.com/marketplace/actions/changed-files). Changes on `*.yaml`, `*.py` and `requirements.txt` files
- **Create Spaces**: Pipelines can be assigned to non-existing spaces by omitting the key `space_id` and adding the key `space_name`. The action will create a new space with the give name and fill in the `space_id` in the YAML file.
- **Create Pipelines**: New pipelines will not have an ID assigned until they are created, so the YAML file should have an empty key `pipeline_id` or 
no `pipeline_id` key. The action will create the pipeline and fill in the ID in the YAML file.
- **Update Pipelines**: Any changes to the pipeline YAML file or the files liked to he pipeline (`requirements.txt` or python files) will be 
pushed to GlassFlow.
- **Delete Pipelines**: This action will delete pipelines which YAML file gets deleted!


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
- **space-to-create-count** - Number of spaces to be created
- **spaces-to-create-ids** - Space IDs that were created

## Notes

- **What happens if a pipeline was deleted from the Webapp and changes are introduced in the pipeline's YAML?**: The action will fail since the `pipeline_id` from the YAML will not exist in GlassFlow anymore
- **What happens if I update a pipeline in the Webapp?**: This GA action only syncs from YAML to GlassFlow, not the other way around. So if a pipeline is modified in the webapp, the changes might be overwritten next time you add changes to the pipeline's YAML, handler or requirements files.

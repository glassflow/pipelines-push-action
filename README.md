# pipelines-push-action

A GitHub Action to automate GlassFlow pipeline deployments as code.

## Features

This GitHub Action enables you to:

- **Track Changes in Your Pipelines**: Detect changes in `*.yaml`, `*.py`, and `requirements.txt` files since the last commit (via [Changed Files Action](https://github.com/marketplace/actions/changed-files)).
- **Create Spaces**: Assign pipelines to new spaces by omitting `space_id` and specifying `space_name`. The action will create a space with the given name and update the YAML file with the assigned `space_id`.
- **Create Pipelines**: New pipelines without an assigned `pipeline_id` (empty or missing `pipeline_id` key) will be created, and the YAML file will be updated with the assigned ID.
- **Update Pipelines**: Changes to pipeline YAML files, `requirements.txt`, or linked Python files will be pushed to GlassFlow.
- **Delete Pipelines**: If a pipeline's YAML file is deleted, the corresponding pipeline will be deleted from GlassFlow.

## Configuration

To use this action, configure your repository with a **GlassFlow Personal Access Token**:

1. Go to your repository's Settings > Secrets and variables > Actions.
2. Add a new secret named GlassFlowPAT (or any name you prefer).
3. Set the value to your GlassFlow Personal Access Token, which can be found on your GlassFlow profile page.

GitHub encrypts your token, and the action will not expose it in logs.

## Usage

Below is an example GitHub Actions workflow to push pipelines to GlassFlow on every push to the `main` branch:

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

| Name | Required | Description |
|------|----------|-------------|
| `glassflow-personal-access-token` | ✅ | GlassFlow Personal Access Token (stored in GitHub Secrets). |
| `pipelines-dir` | ❌ | Directory containing pipelines (Default: `'pipelines'`). |
| `dry-run` | ❌ | If `'true'`, changes will not be pushed to GlassFlow (Default: `'false'`). |

## Outputs

| Output | Description |
|--------|-------------|
| `to-create-count` | Number of new pipelines to create. |
| `to-create-ids` | Pipeline IDs created (available only if `dry-run` is `false`). |
| `to-update-count` | Number of pipelines to update. |
| `to-update-ids` | Pipeline IDs updated. |
| `to-delete-count` | Number of pipelines to delete. |
| `to-delete-ids` | Pipeline IDs deleted. |
| `space-to-create-count` | Number of spaces to be created. |
| `spaces-to-create-ids` | Space IDs created. |

## FAQs

- **What happens if a pipeline was deleted from the Web App, but its YAML file is modified?**
  - The action will fail because the `pipeline_id` in the YAML file no longer exists in GlassFlow.
- **What happens if I update a pipeline in the Web App?**
  - This action syncs changes **from YAML to GlassFlow** only. Updates made in the web app may be overwritten when changes are pushed from the YAML, handler, or `requirements.txt` files.

---

This action provides a streamlined way to manage your GlassFlow pipelines as code, ensuring consistency and automation in your deployment process.


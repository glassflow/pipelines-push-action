# glassflow-action-update

Github Action to push the changes on your pipelines to GlassFlow.

This GA does:
- Get all the files changed since last commit (using https://github.com/marketplace/actions/changed-files)
  - changes on `*.yaml`, `*.py` and `requirements.txt` files
- Update all the pipelines with changes
  - If the YAML has `pipeline_id`, the action will pull the pipeline and update it with the new configuration
  - If the YAML does not include the `pipeline_id`, it will create a new pipeline and update the YAML to include the `pipeline_id`.

Until we do not have a secrets store, the action will also:
- Decrypt `secrets.yaml.enc` (using input encryption key)
- When creating/updating pipelines, inject secrets 

We might have to create two github actions:
1. Docker container action with the code to interact with glassflow
2. Composite action bundling together the action with the 
## Questions

#### What happens if a pipeline was deleted from the Webapp and changes are introduced in the pipeline's YAML?
The action will fail since the `pipeline_id` from the YAML will not exist in GlassFlow anymore

#### What happens if I update a pipeline in the Webapp?
This GA action only syncs from YAML to GlassFlow, not the other way around. So if a pipeline is 
modified in the webapp, the changes might be overwritten next time you add changes to the 
pipeline's YAML, handler or requirements files.


Create one or more test workflows that will test the MCP server in this repository.

## Core functionality
- Run demo.py in the scripts folder. Pass the subscription id found in secret AZURE_SUBSCRIPTION_ID
- Error out if any errors are encountered running demo.py
- Do separate runs for Linux and windows so that I'm sure the MCP server works in both operating systems
- Trigger the workflow on dispatch and if pull requests are created or changed.
- Document the new workflows in the README.md in the root.
- Output any errors in a convenient format that I can use to have you investigate and fix the errors.

## Azure authentication
- Authentication will use a service principal
- Assume the following secrets will be available to the workflow for authentication
    - AZURE_TENANT_ID
    - AZURE_CLIENT_ID
    - AZURE_CLIENT_SECRET
    - AZURE_SUBSCRIPTION_ID
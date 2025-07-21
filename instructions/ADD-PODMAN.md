Add an OCI image definition for the MCP server using podman and workflow to create that image and publish it to GitHub.

## Core Functionality
- Create a workflow that will use podman to create an OCI image
- The workflow should test the image in the same way that workflows test-linux.yml and test-windows.yml do
- If the image passes it's tests, deploy the OCI image to GitHub
- Use the same Azure credential inputs as used in workflows test-linux.yml and test-windows.yml
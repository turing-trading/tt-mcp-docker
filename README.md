# Docker MCP server

An MCP server for Docker

## Components

### Resources

The server implements a couple resources for every running container:

- Stats: CPU, memory, etc. for a container
- Logs: tail some logs from a container

### Prompts

- `docker_compose`: use natural language instead of YAML to compose containers. Simply provide a project name and a description of the containers comprising the project, and the LLM will come up with a deployment plan. Examples:
    - name: `wordpress`, containers: "deploy a WordPress container and a supporting MySQL container, exposing Wordpress on port 9000"
    - name: `nginx`, containers: "deploy an nginx container exposing it on port 9000"

### Tools

#### Containers

- `list_containers`
- `create_container`
- `run_container`
- `start_container`
- `fetch_container_logs`
- `stop_container`
- `remove_container`

#### Images

- `list_images`
- `pull_image`
- `push_image`
- `build_image`
- `remove_image`

#### Networks

- `list_networks`
- `create_network`
- `remove_network`

#### Volumes

- `list_volumes`
- `create_volume`
- `remove_volume`

## Configuration

This server uses the Python Docker SDK's `from_env` method. For configuration details, see [the documentation](https://docker-py.readthedocs.io/en/stable/client.html#docker.client.from_env).

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "mcp-server-docker": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/repo",
        "run",
        "mcp-server-docker"
      ]
    }
  }
  ```
</details>

## Development

Prefer using Devbox to configure your development environment.

See the `devbox.json` for helpful development commands.

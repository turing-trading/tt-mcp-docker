import json
import logging
from collections.abc import Sequence
from typing import Any

import docker
import mcp.types as types
from mcp.server import Server
from pydantic import AnyUrl, ValidationError

from .input_schemas import (
    BuildImageInput,
    ContainerActionInput,
    CreateContainerInput,
    CreateNetworkInput,
    CreateVolumeInput,
    FetchContainerLogsInput,
    ListContainersInput,
    ListImagesInput,
    ListNetworksInput,
    ListVolumesInput,
    PullPushImageInput,
    RemoveContainerInput,
    RemoveImageInput,
    RemoveNetworkInput,
    RemoveVolumeInput,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docker-server")

server = Server("docker-server")
docker_client = docker.from_env()


@server.list_resources()
async def list_resources() -> list[types.Resource]:
    resources = []
    for container in docker_client.containers.list():
        resources.extend(
            [
                types.Resource(
                    uri=AnyUrl(f"docker://containers/{container.id}/logs"),
                    name=f"Logs for {container.name}",
                    description=f"Live logs for container {container.name}",
                    mimeType="text/plain",
                ),
                types.Resource(
                    uri=AnyUrl(f"docker://containers/{container.id}/stats"),
                    name=f"Stats for {container.name}",
                    description=f"Live resource usage stats for container {container.name}",
                    mimeType="application/json",
                ),
            ]
        )
    return resources


@server.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    if not str(uri).startswith("docker://containers/"):
        raise ValueError(f"Unknown resource URI: {uri}")

    parts = str(uri).split("/")
    if len(parts) != 5:  # docker://containers/{id}/{logs|stats}
        raise ValueError(f"Invalid container resource URI: {uri}")

    container_id = parts[3]
    resource_type = parts[4]
    container = docker_client.containers.get(container_id)

    if resource_type == "logs":
        logs = container.logs(tail=100).decode("utf-8")
        return json.dumps(logs.split("\n"))

    elif resource_type == "stats":
        stats = container.stats(stream=False)
        return json.dumps(stats, indent=2)

    else:
        raise ValueError(f"Unknown container resource type: {resource_type}")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_containers",
            description="List all Docker containers",
            inputSchema=ListContainersInput.model_json_schema(),
        ),
        types.Tool(
            name="create_container",
            description="Create a new Docker container",
            inputSchema=CreateContainerInput.model_json_schema(),
        ),
        types.Tool(
            name="run_container",
            description="Run an image in a new Docker container",
            inputSchema=CreateContainerInput.model_json_schema(),
        ),
        types.Tool(
            name="start_container",
            description="Start a Docker container",
            inputSchema=ContainerActionInput.model_json_schema(),
        ),
        types.Tool(
            name="fetch_container_logs",
            description="Fetch logs for a Docker container",
            inputSchema=FetchContainerLogsInput.model_json_schema(),
        ),
        types.Tool(
            name="stop_container",
            description="Stop a Docker container",
            inputSchema=ContainerActionInput.model_json_schema(),
        ),
        types.Tool(
            name="remove_container",
            description="Remove a Docker container",
            inputSchema=RemoveContainerInput.model_json_schema(),
        ),
        types.Tool(
            name="list_images",
            description="List Docker images",
            inputSchema=ListImagesInput.model_json_schema(),
        ),
        types.Tool(
            name="pull_image",
            description="Pull a Docker image",
            inputSchema=PullPushImageInput.model_json_schema(),
        ),
        types.Tool(
            name="push_image",
            description="Push a Docker image",
            inputSchema=PullPushImageInput.model_json_schema(),
        ),
        types.Tool(
            name="build_image",
            description="Build a Docker image from a Dockerfile",
            inputSchema=BuildImageInput.model_json_schema(),
        ),
        types.Tool(
            name="remove_image",
            description="Remove a Docker image",
            inputSchema=RemoveImageInput.model_json_schema(),
        ),
        types.Tool(
            name="list_networks",
            description="List Docker networks",
            inputSchema=ListNetworksInput.model_json_schema(),
        ),
        types.Tool(
            name="create_network",
            description="Create a Docker network",
            inputSchema=CreateNetworkInput.model_json_schema(),
        ),
        types.Tool(
            name="remove_network",
            description="Remove a Docker network",
            inputSchema=RemoveNetworkInput.model_json_schema(),
        ),
        types.Tool(
            name="list_volumes",
            description="List Docker volumes",
            inputSchema=ListVolumesInput.model_json_schema(),
        ),
        types.Tool(
            name="create_volume",
            description="Create a Docker volume",
            inputSchema=CreateVolumeInput.model_json_schema(),
        ),
        types.Tool(
            name="remove_volume",
            description="Remove a Docker volume",
            inputSchema=RemoveVolumeInput.model_json_schema(),
        ),
    ]


@server.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    if arguments is None:
        arguments = {}

    result = None

    try:
        if name == "list_containers":
            args = ListContainersInput.model_validate(arguments)
            containers = docker_client.containers.list(**args.model_dump())
            result = [
                {
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags,
                }
                for c in containers
            ]

        elif name == "create_container":
            args = CreateContainerInput.model_validate(arguments)
            container = docker_client.containers.create(
                **args.model_dump(),
            )
            result = {
                "status": container.status,
                "id": container.id,
                "name": container.name,
            }

        elif name == "run_container":
            args = CreateContainerInput.model_validate(arguments)
            container = docker_client.containers.run(
                **args.model_dump(),
            )
            result = {
                "status": container.status,
                "id": container.id,
                "name": container.name,
            }

        elif name == "start_container":
            args = ContainerActionInput.model_validate(arguments)
            container = docker_client.containers.get(args.container_id)
            container.start()
            result = {"status": container.status, "id": container.id}

        elif name == "stop_container":
            args = ContainerActionInput.model_validate(arguments)
            container = docker_client.containers.get(args.container_id)
            container.stop()
            result = {"status": container.status, "id": container.id}

        elif name == "remove_container":
            args = RemoveContainerInput.model_validate(arguments)
            container = docker_client.containers.get(args.container_id)
            container.remove(force=args.force)
            result = {"status": "removed", "id": args.container_id}

        elif name == "fetch_container_logs":
            args = FetchContainerLogsInput.model_validate(arguments)
            container = docker_client.containers.get(args.container_id)
            logs = container.logs(tail=args.tail).decode("utf-8")
            result = {"logs": logs.split("\n")}

        elif name == "list_images":
            args = ListImagesInput.model_validate(arguments)
            filters = {}
            if args.include_dangling is not None:
                filters["dangling"] = args.include_dangling
            if args.filter_labels:
                filters["label"] = args.filter_labels

            images = docker_client.images.list(
                name=args.name,
                all=args.all,
                filters=filters,
            )
            result = [{"id": img.id, "tags": img.tags} for img in images]

        elif name == "pull_image":
            args = PullPushImageInput.model_validate(arguments)
            image = docker_client.images.pull(args.repository, tag=args.tag)
            result = {"id": image.id, "tags": image.tags}

        elif name == "push_image":
            args = PullPushImageInput.model_validate(arguments)
            docker_client.images.push(args.repository, tag=args.tag)
            result = {
                "status": "pushed",
                "repository": args.repository,
                "tag": args.tag,
            }

        elif name == "build_image":
            args = BuildImageInput.model_validate(arguments)
            image = docker_client.images.build(
                path=args.path, tag=args.tag, dockerfile=args.dockerfile
            )
            result = {"id": image[0].id, "tags": image[0].tags}

        elif name == "remove_image":
            args = RemoveImageInput.model_validate(arguments)
            docker_client.images.remove(image=args.image, force=args.force)
            result = {"status": "removed", "image": args.image}

        elif name == "list_networks":
            ListNetworksInput.model_validate(arguments)  # Validate empty input
            networks = docker_client.networks.list()
            result = [
                {"id": net.id, "name": net.name, "driver": net.attrs["Driver"]}
                for net in networks
            ]

        elif name == "create_network":
            args = CreateNetworkInput.model_validate(arguments)
            network = docker_client.networks.create(
                name=args.name, driver=args.driver, internal=args.internal
            )
            result = {"id": network.id, "name": network.name}

        elif name == "remove_network":
            args = RemoveNetworkInput.model_validate(arguments)
            network = docker_client.networks.get(args.network_id)
            network.remove()
            result = {"status": "removed", "id": args.network_id}

        elif name == "list_volumes":
            ListVolumesInput.model_validate(arguments)  # Validate empty input
            volumes = docker_client.volumes.list()
            result = [
                {"name": vol.name, "driver": vol.attrs["Driver"]} for vol in volumes
            ]

        elif name == "create_volume":
            args = CreateVolumeInput.model_validate(arguments)
            volume = docker_client.volumes.create(
                name=args.name, driver=args.driver, labels=args.labels
            )
            result = {"name": volume.name, "driver": volume.attrs["Driver"]}

        elif name == "remove_volume":
            args = RemoveVolumeInput.model_validate(arguments)
            volume = docker_client.volumes.get(args.volume_name)
            volume.remove(force=args.force)
            result = {"status": "removed", "name": args.volume_name}

        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except ValidationError as e:
        await server.request_context.session.send_log_message(
            "error", "Failed to validate input provided by LLM: " + str(e)
        )
        return [
            types.TextContent(
                type="text", text=f"ERROR: You provided invalid Tool inputs: {e}"
            )
        ]

    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )

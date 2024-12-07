from typing import Literal

from pydantic import BaseModel, Field


class FetchContainerLogsInput(BaseModel):
    container_id: str = Field(..., description="Container ID or name")
    tail: int | Literal["all"] = Field(
        100, description="Number of lines to show from the end"
    )


class ListContainersInput(BaseModel):
    all: bool = Field(
        False, description="Show all containers (default shows just running)"
    )


class CreateContainerInput(BaseModel):
    image: str = Field(..., description="Docker image name")
    name: str | None = Field(None, description="Container name")
    entrypoint: str | None = Field(None, description="Entrypoint to run in container")
    command: str | None = Field(None, description="Command to run in container")
    network: str | None = Field(None, description="Network to attach the container to")
    environment: dict[str, str] | None = Field(
        None, description="Environment variables"
    )
    ports: dict[str, int | list[int] | tuple[str, int] | None] | None = Field(
        None, description="Port mappings"
    )
    volumes: dict[str, dict[str, str]] | list[str] | None = Field(
        None, description="Volume mappings"
    )


class ContainerActionInput(BaseModel):
    container_id: str = Field(..., description="Container ID or name")


class RemoveContainerInput(BaseModel):
    container_id: str = Field(..., description="Container ID or name")
    force: bool = Field(False, description="Force remove the container")


class ListImagesInput(BaseModel):
    name: str | None = Field(
        None, description="Filter images by repository name, if desired"
    )
    all: bool = Field(False, description="Show all images (default hides intermediate)")
    include_dangling: bool | None = Field(None, description="Show dangling images")
    filter_labels: list[str] | None = Field(
        None, description="Filter by label, either `key` or `key=value` format"
    )


class PullPushImageInput(BaseModel):
    repository: str = Field(..., description="Image repository")
    tag: str | None = Field("latest", description="Image tag")


class BuildImageInput(BaseModel):
    path: str = Field(..., description="Path to build context")
    tag: str = Field(..., description="Image tag")
    dockerfile: str | None = Field(None, description="Path to Dockerfile")


class RemoveImageInput(BaseModel):
    image: str = Field(..., description="Image ID or name")
    force: bool = Field(False, description="Force remove the image")


class ListNetworksInput(BaseModel):
    pass


class CreateNetworkInput(BaseModel):
    name: str = Field(..., description="Network name")
    driver: str | None = Field("bridge", description="Network driver")
    internal: bool = Field(False, description="Create an internal network")


class RemoveNetworkInput(BaseModel):
    network_id: str = Field(..., description="Network ID or name")


class ListVolumesInput(BaseModel):
    pass


class CreateVolumeInput(BaseModel):
    name: str = Field(..., description="Volume name")
    driver: str | None = Field("local", description="Volume driver")
    labels: dict[str, str] | None = Field(None, description="Volume labels")


class RemoveVolumeInput(BaseModel):
    volume_name: str = Field(..., description="Volume name")
    force: bool = Field(False, description="Force remove the volume")

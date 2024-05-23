#!/bin/bash

PROJECT_ROOT="$(realpath "$(dirname "$0")/../..")"
CONTAINER_SCRIPTS="/recipes/tools/ubuntu-24.04-docker/.container_scripts"

echo "Preparing to launch and configure Ubuntu 24.04 docker container"

if [ -n "$(groups) | grep docker" ]; then
	echo "User not in docker group, sudo will be required"
	DOCKER_CMD="sudo docker"
else
	DOCKER_CMD="docker"
fi

echo "The root of this repo ($PROJECT_ROOT)"
echo "will be mapped into the container as a read-only volume"
echo

$DOCKER_CMD run --rm -it -v "$PROJECT_ROOT":/recipes:ro \
	-e HTTP_PROXY="$HTTP_PROXY" -e HTTPS_PROXY="$HTTPS_PROXY" \
    -e http_proxy="$http_proxy" -e https_proxy="$https_proxy" \
    -e no_proxy="$no_proxy" --net=host \
	ubuntu:24.04 /bin/bash $CONTAINER_SCRIPTS/configure.sh

echo
echo "Container exited"

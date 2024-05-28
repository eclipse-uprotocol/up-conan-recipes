#!/bin/bash

PROJECT_ROOT="$(realpath "$(dirname "$0")/../..")"
CONTAINER_SCRIPTS="/recipes/tools/ubuntu-24.04-docker/.container_scripts"

echo "Preparing to launch and configure Ubuntu 24.04 docker container"

if [ -n "$(groups) | grep docker" ]; then
	echo "User not in docker group, sudo will be required"
	echo
	DOCKER_CMD="sudo docker"
else
	DOCKER_CMD="docker"
fi

MAP_VOLS=()
for arg in "$@"; do
	if [ "$arg" == "-h" ] || [ "$arg" == "--help" ]; then
		echo "$(basename "$0") [-h, --help] [path] [path]..." 1>&2
		echo
		echo "Launches a docker container to run some builds in. The container"
		echo "will be deleted on exit so that each launch is always clean."
		echo
		echo "This repo will be mapped as a read-only volume at /recipes."
		echo
		echo "Optionally, a list of paths can be provided to map in to the"
		echo "container. These will be mapped as read-only volumes in the"
		echo "'/root/mapped/' directory. Mapped paths must be owned by the"
		echo "current user ($USER)."

		exit 0
	fi

	if [ -e "$arg" ] && [[ -O "$arg" ]]; then
		echo "Path '$(realpath "$arg")' will be mapped into"
		echo "the container as read-only at '/root/mapped/$(basename "$arg")'"
		echo
		MAP_VOLS+=("-v$(realpath "$arg"):/root/mapped/$(basename "$arg"):ro")
	else
		if [ -e "$arg" ]; then
			echo "Path '$arg' is not owned by the current user ($USER)" 1>&2
		else
			echo "Path '$arg' does not exist" 1>&2
		fi
		exit 1
	fi
done

echo "The root of this repo ($PROJECT_ROOT)"
echo "will be mapped into the container as a read-only volume"
echo

$DOCKER_CMD run --rm -it -v "$PROJECT_ROOT":/recipes:ro \
	-e HTTP_PROXY="$HTTP_PROXY" -e HTTPS_PROXY="$HTTPS_PROXY" \
	-e http_proxy="$http_proxy" -e https_proxy="$https_proxy" \
	-e no_proxy="$no_proxy" --net=host \
	"${MAP_VOLS[@]}" \
	ubuntu:24.04 /bin/bash $CONTAINER_SCRIPTS/configure.sh

echo
echo "Container exited"

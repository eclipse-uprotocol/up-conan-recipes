#!/bin/bash

PROJECT_ROOT="$(realpath "$(dirname "$0")/../..")"
CONTAINER_SCRIPTS="/data/recipes/tools/ubuntu-22.04-docker/.container_scripts"

echo "Preparing to launch and configure Ubuntu 22.04 docker container"

if [ -z "$(groups | grep docker)" ]; then
	echo "User not in docker group, sudo will be required"
	echo
	DOCKER_CMD="sudo docker"
else
	DOCKER_CMD="docker"
fi

MAP_VOLS=()
for arg in "$@"; do
	if [ "$arg" == "-h" ] || [ "$arg" == "--help" ]; then
		echo "$(basename "$0") [-h, --help, -s --enable-sudo] [path] [path]..." 1>&2
		echo 1>&2
		echo "Launches a docker container to run some builds in. The container" 1>&2
		echo "will be deleted on exit so that each launch is always clean." 1>&2
		echo 1>&2
		echo "    -h --help        Print this help message" 1>&2
		echo "    -s --enable-sudo Allow the use of sudo within the container." 1>&2
		echo "                     This requires setting a password when the" 1>&2
		echo "                     container is launched. It can be used to" 1>&2
		echo "                     install additional packages." 1>&2
		echo 1>&2
		echo "This repo will be mapped as a read-only volume at /data/recipes." 1>&2
		echo 1>&2
		echo "Optionally, a list of paths can be provided to map in to the" 1>&2
		echo "container. These will be mapped as read-write volumes in the" 1>&2
		echo "'/data/' directory. Mapped paths must be owned by the" 1>&2
		echo "current user ($USER)." 1>&2

		exit 0
	fi

	if [ "$arg" == "-s" ] || [ "$arg" == "--enable-sudo" ]; then
		export ENABLE_SUDO=sudo

	elif [ -e "$arg" ] && [[ -O "$arg" ]]; then
		mpath="$(basename "$arg")"
		echo "Path '$(realpath "$arg")' will be mapped into"
		echo "the container at '/data/$mpath'"
		echo
		MAP_VOLS+=("-v$(realpath "$arg"):/data/$mpath")
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

echo "Launching container as $USER ($(id -u):$(id -g))"
$DOCKER_CMD run --rm -it -v "$PROJECT_ROOT":/data/recipes:ro \
	-e HTTP_PROXY="$HTTP_PROXY" -e HTTPS_PROXY="$HTTPS_PROXY" \
	-e http_proxy="$http_proxy" -e https_proxy="$https_proxy" \
	-e no_proxy="$no_proxy" --net=host -e USER_ID=$(id -u) \
	-e GROUP_ID=$(id -g) -e ENABLE_SUDO=$ENABLE_SUDO \
	"${MAP_VOLS[@]}" ubuntu:22.04 /bin/bash $CONTAINER_SCRIPTS/configure.sh

echo
echo "Container exited"

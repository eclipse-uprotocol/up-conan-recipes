#!/bin/bash

CONTAINER_SCRIPTS="/data/recipes/tools/ubuntu-22.04-docker/.container_scripts"

# Exit on errors
set -e

echo "Installing packages"
export DEBIAN_FRONTEND=noninteractive
apt-get -y update
apt-get -y install wget tmux cmake g++ git $ENABLE_SUDO gdb valgrind \
    clang-format clang-tidy clang-format-12 clang-tidy-12
unset DEBIAN_FRONTEND

echo
echo "Installing conan"
wget https://github.com/conan-io/conan/releases/download/2.3.0/conan-2.3.0-amd64.deb
dpkg -i conan-2.3.0-amd64.deb

echo
echo "Configuring container user"
groupadd -g $GROUP_ID -o user
useradd --shell /bin/bash -u $USER_ID -g $GROUP_ID -o -c "" -m user

if [ -n "$ENABLE_SUDO" ]; then
	echo
	echo "Granting sudo permissions"
	echo "NOTE: User will be required to create a password"
	usermod -aG sudo user
	passwd -de user
fi

echo
echo "Switching to user $USER_ID"
cd /data
exec su user "$CONTAINER_SCRIPTS/user_setup.sh"

#!/bin/bash

apt-get -y update
apt-get -y install wget tmux cmake g++ git

wget https://github.com/conan-io/conan/releases/download/2.3.0/conan-2.3.0-amd64.deb
dpkg -i conan-2.3.0-amd64.deb
conan profile detect

cd /recipes
exec bash -il

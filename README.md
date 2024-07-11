# uProtocol C++ Conan Recipes (up-conan-recipes)

This is a collection of Conan recipes for uProtocol C++ libraries. For each
uP package, two recipes are provided: release and developer.

The release recipes aim to provide a repeatable way to build all tagged releases
of the various uProtocol libraries. They pull the source archive for a given
tag from github, confirm the checksum, and build the package.

The developer packages are intended to support arbitrary builds for developers.
They will, by default, clone eclipse-uprotocol/[repo] and build the main branch.
Conan options can be provided to override the fork and commit that are checked
out and built.

## Building Release Packages

With Conan 2:

```
conan create --version 1.6.0 --build=missing up-core-api/release/
conan create --version 1.0.0-rc0 --build=missing up-cpp/release/
conan create --version 1.0.0-rc0 --build=missing up-transport-zenoh-cpp/release/
conan create --version 0.1.0 --build=missing up-transport-vsomeip-cpp/release/
```

## Building Developer Packages

The default fork and checkout commit can be overridden with
`-o fork=[fork]` and `-o commitish=[commit/branch/tag]`

With Conan 2:

```
conan create --version 1.5.8 --build=missing up-core-api/developer/
conan create --version 0.2.0 --build=missing up-cpp/developer/
conan create --version 0.2.0 --build=missing up-transport-zenoh-cpp/developer/
conan create --version 0.1.0 --build=missing up-transport-vsomeip-cpp/developer/
```

Note that developer recipes will generally only support recent commits in a
library's repo. Older releases are available through the release recipes.

When changing fork or commit-ish for developer builds, it will be necessary to
first remove the any existing copies of the target package. For example, up-cpp
would be removed with `conan remove 'up-cpp'`.

## Running in a clean docker container

```
sudo docker run -it -v .:/recipes:ro ubuntu:24.04 /bin/bash
apt update && apt install wget git g++ cmake
wget https://github.com/conan-io/conan/releases/download/2.3.0/conan-2.3.0-amd64.deb
dpkg -i conan-2.3.0-amd64.deb
conan profile detect

# Build packages here
```

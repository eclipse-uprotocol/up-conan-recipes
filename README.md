# uProtocol C++ Conan Recipes (up-conan-recipes)

This is a collection of Conan recipes for uProtocol C++ libraries. For each uP
package, two recipes are provided: release and developer.

The release recipes aim to provide a repeatable way to build all tagged releases
of the various uProtocol libraries. They pull the source archive for a given tag
from github, confirm the checksum, and build the package.

The developer packages are intended to support arbitrary builds for developers.
They will, by default, clone eclipse-uprotocol/[repo] and build the main branch.
Conan options can be provided to override the fork and commit that are checked
out and built.

## Building Release Packages

With Conan 2:

```shell
conan create --version 1.6.0-alpha4 --build=missing up-core-api/release/
conan create --version 1.0.1 --build=missing up-cpp/release/
conan create --version 1.0.0-rc3 --build=missing up-transport-zenoh-cpp/release/
```

## Building Developer Packages

The default fork and checkout commit can be overridden with `-o fork=[fork]` and
`-o commitish=[commit/branch/tag]`

With Conan 2:

```shell
conan create --version 1.6.1-dev --build=missing up-core-api/developer/
conan create --version 1.1.0-dev --build=missing up-cpp/developer/
conan create --version 1.0.0-dev --build=missing up-transport-zenoh-cpp/developer/
conan create --version 1.0.0-dev --build=missing up-transport-socket-cpp/developer/
```

Note that developer recipes will generally only support recent commits in a
library's repo. Older releases are available through the release recipes.

When changing fork or commit-ish for developer builds, it will be necessary to
first remove the any existing copies of the target package. For example, up-cpp
would be removed with `conan remove 'up-cpp'`.

## Building (Temporary) Zenoh Packages

At time of writing, conan packages were not available for zenoh-c and zenoh-cpp.
They are prerequisites for the up-transport-zenoh-cpp packages. With Conan 2:

```shell
conan create --version 1.2.1 zenohc-tmp/prebuilt
conan create --version 1.2.1 zenohcpp-tmp/from-source
```

## Running in a clean docker container

```shell
cd tools/ubuntu-24.04-docker/
./launch-shell.sh

# Build packages here
```

## Building Release Packages for QNX (cross-compile)

**NOTE**: QNX cross-compilation are only supported from a Linux(x86_64) build machine.
          For QNX, we have to explicitly build all dependencies

Pre-requisite:

* Install QNX license and SDP installation (~/.qnx and ~/qnx800 by default)
  - https://www.qnx.com/products/everywhere/ (**Non-Commercial Use**)

```shell
# source QNX SDP
source <QNX_SDP>/qnxsdp-env.sh

# build protobuf for Linux
conan create --version=3.21.12 --build=missing protobuf

# IMPORTANT
# update conan settings for QNX8.0 support
conan config install tools/qnx-8.0-extension/settings_user.yml

# build protobuf for QNX
#
# <profile-name> could be one of: nto-7.1-aarch64-le, nto-7.1-x86_64, nto-8.0-aarch64-le, nto-8.0-x86_64
# <version-number>: 3.15.0, 3.21.12, 5.27.2
#
conan create -pr:h=tools/profiles/<profile-name> --version=3.21.12 --build=missing protobuf

# build up-core-api for QNX
#
# <profile-name>: nto-7.1-aarch64-le, nto-7.1-x86_64, nto-8.0-aarch64-le, nto-8.0-x86_64
# <version-number>: 1.6.0-alpha2, 1.6.0-alpha3, 1.6.0-alpha4
#
conan create -pr:h=tools/profiles/<profile-name> --version=1.6.0-alpha2 up-core-api/release/

# build gtest for QNX
#
# <profile-name>: nto-7.1-aarch64-le, nto-7.1-x86_64, nto-8.0-aarch64-le, nto-8.0-x86_64
# <version-number>: 1.10.0, 1.13.0, 1.14.0
#
conan create -pr:h=tools/profiles/<profile-name> --version=1.14.0 gtest

# build up-cpp for QNX
#
# <profile-name>: nto-7.1-aarch64-le, nto-7.1-x86_64, nto-8.0-aarch64-le, nto-8.0-x86_64
# <version-number>: 1.0.0-rc0, 1.0.0, 1.0.1-rc1, 1.0.1
#
conan create -pr:h=tools/profiles/<profile-name> --version=1.0.1 --build=missing up-cpp/release
```

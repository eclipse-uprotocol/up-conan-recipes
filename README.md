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
# build zenoh transport layer based on zenohc-tmp temporary solution
conan create --version 1.0.0-rc5 zenohc-tmp/prebuilt
conan create --version 1.0.0-rc5 zenohcpp-tmp/from-source
conan create --version 1.0.0-rc3 --build=missing up-transport-zenoh-cpp/release/
# OR build zenoh transport layer based on zenoh-pico backend
conan create --version 1.0.0-rc5 zenoh-pico
conan create --version 1.0.0-rc5 -o backend=zenoh-pico zenoh-cpp
conan create --version 1.0.0-rc3 -o backend=zenoh-pico up-transport-zenoh-cpp/release
```

## Building Developer Packages

The default fork and checkout commit can be overridden with `-o fork=[fork]` and
`-o commitish=[commit/branch/tag]`

With Conan 2:

```shell
conan create --version 1.6.1-dev --build=missing up-core-api/developer/
conan create --version 1.1.0-dev --build=missing up-cpp/developer/
conan create --version 1.5.0 zenohc-tmp/prebuilt
conan create --version 1.5.0 zenohcpp-tmp/from-source
conan create --version 1.0.0-dev --build=missing up-transport-zenoh-cpp/developer/
#conan create --version 1.0.0-dev --build=missing up-transport-socket-cpp/developer/
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
conan create --version 1.5.0 zenohc-tmp/prebuilt
conan create --version 1.5.0 zenohcpp-tmp/from-source
```

## Building Zenoh Packages - with zenoh-c backend

```shell
conan create --version 1.5.0 zenoh-c/prebuilt
conan create --version 1.5.0 zenoh-cpp -o backend=zenoh-c
```

## Building Zenoh Packages - with zenoh-pico backend

The [zenoh-c] library is actually a C language binding over the [zenoh] library implemented in Rust.
To have a pure C language implementation that is more feasible for embedded and QNX, we need to use
another Zenoh implementation based on the [zenoh-pico] backend.

```shell
conan create --version 1.5.0 zenoh-pico
conan create --version 1.5.0 zenoh-cpp -o backend=zenoh-pico
```
**NOTE**: To run the Zenoh transport layer based on the [zenoh-pico] backend,
          we need to deploy and run the zenoh-router service first.
          Please see below for details on how to do this.

## Building Zenoh Router
```shell
# Deploy zenoh-router
conan create --version 1.5.0 zenoh-router/prebuilt
conan install --requires=zenoh-router/1.5.0 -d=direct_deploy --deployer-folder=<PATH_TO_ZENOHD_STAGE>
# Run zenoh-router service with proper configuration
<PATH_TO_ZENOHD_STAGE>/direct_deploy/zenoh-router/zenohd -l "tcp/<HOST_IP>:7447"
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
#
conan create -pr:h=tools/profiles/nto-8.0-x86_64 --version=3.21.12 --build=missing protobuf
conan create -pr:h=tools/profiles/nto-8.0-x86_64 --version=1.6.0-alpha4 up-core-api/release/
conan create -pr:h=tools/profiles/nto-8.0-x86_64 --version=1.14.0 gtest
conan create -pr:h=tools/profiles/nto-8.0-x86_64 --version=1.0.1 --build=missing up-cpp/release
# build zenoh transport layer for QNX on pico backend
conan create -pr:h=tools/profiles/nto-8.0-x86_64 --version 1.0.0-rc5 zenoh-pico
conan create -pr:h=tools/profiles/nto-8.0-x86_64 --version 1.0.0-rc5 -o backend=zenoh-pico zenoh-cpp
conan create -pr:h=tools/profiles/nto-8.0-x86_64 --version 1.0.0-rc3 -o backend=zenoh-pico --build=missing up-transport-zenoh-cpp/release

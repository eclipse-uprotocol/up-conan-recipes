# uProtocol C++ Conan Recipes

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
conan create --version 1.5.8 up-core-api/release/
conan create --version 0.2.0 up-cpp/release/
conan create --version 0.2.0 up-transport-zenoh-cpp/release/
conan create --version 0.1.0 up-transport-vsomeip-cpp/release/
```

## Building Developer Packages

The default fork and checkout commit can be overridden with
`-o fork=[fork]` and `-o commitish=[commit/branch/tag]`

With Conan 2:

```
conan create --version 1.5.8 up-core-api/developer/
conan create --version 0.2.0 up-cpp/developer/
conan create --version 0.2.0 up-transport-zenoh-cpp/developer/
conan create --version 0.1.0 up-transport-vsomeip-cpp/developer/
```

Note that developer recipes will generally only support recent commits in a
library's repo. Older releases are available through the release recipes.

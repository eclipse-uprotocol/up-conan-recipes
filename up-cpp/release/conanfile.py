from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import copy, get
import os
import yaml

class upCoreApiRecipe(ConanFile):
    name = "up-cpp"

    # Optional metadata
    license = "Apache-2.0"
    author = "Contributors to the Eclipse Foundation <uprotocol-dev@eclipse.org>"
    url = "https://github.com/eclipse-uprotocol/up-cpp"
    description = "This library provides a C++ uProtocol API for the development of uEntities"
    topics = ("automotive", "iot", "uprotocol", "messaging")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def requirements(self):
        version_data = self.conan_data[self.version]
        if "requirements" in version_data:
            for requirement, version in version_data["requirements"].items():
                self.requires(f"{requirement}/{version}")
        else:
            self.output.warning("No requirements specified in conandata.yml. Please check your configuration.")

        if "test-requirements" in version_data:
            for requirement, version in version_data["test-requirements"].items():
                self.test_requires(f"{requirement}/{version}")

    def source(self):
        get(self, **self.conan_data[self.version]["sources"], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        # Unfixed warnings by default are treated as an error
        tc.cache_variables["CMAKE_CXX_FLAGS_INIT"] = "-Wno-error=unused-but-set-variable -Wno-error=pedantic -Wno-error=conversion"
        if self.settings.os == "Neutrino":
            tc.cache_variables["CMAKE_SYSTEM_NAME"] = "QNX"
            tc.cache_variables["CMAKE_CXX_COMPILER"] = "q++"
            # Trick to suppress compiler option '-pthread' which is not acceptable by qcc
            #tc.cache_variables["CMAKE_HAVE_LIBC_PTHREAD"] = "True"
            if   self.settings.arch == "armv8": #aarch64le
                tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "aarch64le"
                tc.cache_variables["CMAKE_CXX_COMPILER_TARGET"] = "gcc_ntoaarch64le"
            elif self.settings.arch == "x86_64": #x86_64
                tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "x86_64"
                tc.cache_variables["CMAKE_CXX_COMPILER_TARGET"] = "gcc_ntox86_64"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(cli_args=["--verbose"])

    def package(self):
        cmake = CMake(self)
        cmake.install(cli_args=["--verbose"])

    def package_info(self):
        self.cpp_info.libs = ["up-cpp"]

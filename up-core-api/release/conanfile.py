from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import copy, get
import os
import yaml

class upCoreApiRecipe(ConanFile):
    name = "up-core-api"

    # Optional metadata
    license = "Apache-2.0"
    author = "Contributors to the Eclipse Foundation <uprotocol-dev@eclipse.org>"
    url = "https://github.com/eclipse-uprotocol/up-spec"
    description = "Provides the uProtocol data model and core services definitions compiled for C++ from source proto files"
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

    def build_requirements(self):
        version_data = self.conan_data[self.version]
        if "build_requirements" in version_data:
            for requirement, version in version_data["build_requirements"].items():
                self.tool_requires(f"{requirement}/{version}")
        else:
            self.output.warning("No build requirements specified in conandata.yml. Please check your configuration.")


    # We are providing our own cmake config since one is not included in the
    # spec repo.
    def export_sources(self):
        copy(self, "CMakeLists.txt",
             self.recipe_folder + "/..", self.export_sources_folder)

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
        if self.settings.os == "Neutrino":
            tc.cache_variables["CMAKE_SYSTEM_NAME"] = "QNX"
            tc.cache_variables["CMAKE_C_COMPILER"] = "qcc"
            tc.cache_variables["CMAKE_CXX_COMPILER"] = "q++"
            tc.cache_variables["CMAKE_CXX_STANDARD"] = 14
            if   self.settings.arch == "armv8": #aarch64le
                tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "aarch64le"
                tc.cache_variables["CMAKE_CXX_COMPILER_TARGET"] = "gcc_ntoaarch64le"
                tc.cache_variables["CMAKE_C_COMPILER_TARGET"] = "gcc_ntoaarch64le"
            elif self.settings.arch == "x86_64": #x86_64
                tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "x86_64"
                tc.cache_variables["CMAKE_CXX_COMPILER_TARGET"] = "gcc_ntox86_64"
                tc.cache_variables["CMAKE_C_COMPILER_TARGET"] = "gcc_ntox86_64"
            tc.cache_variables["CMAKE_CXX_FLAGS_INIT"] = "-D_XOPEN_SOURCE=700 -D_QNX_SOURCE"
            tc.cache_variables["CMAKE_C_FLAGS_INIT"] = "-D_XOPEN_SOURCE=700 -D_QNX_SOURCE"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(cli_args=["--verbose"])

    def package(self):
        cmake = CMake(self)
        cmake.install(cli_args=["--verbose"])

    def package_info(self):
        self.cpp_info.libs = ["up-core-api"]

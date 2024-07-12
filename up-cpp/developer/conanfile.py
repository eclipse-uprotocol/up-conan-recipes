from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import copy


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
            "fork": ["ANY"],
            "commitish": ["ANY"] }

    default_options = {
            "shared": False,
            "fPIC": True,
            "fork": "eclipse-uprotocol/up-cpp",
            "commitish": "main"}

    requires = "up-core-api/[~1.6, include_prerelease]", "spdlog/[~1.13]", "protobuf/[~3.21]"
    test_requires = "gtest/[~1.14]"

    def init(self):
        self.fork = self.options.get_safe("fork", "eclipse-uprotocol/up-cpp")
        self.commitish = self.options.get_safe("commitish", "main")

    def source(self):

        git = Git(self)
        git.clone(f"https://github.com/{self.fork}.git", target=".")
        git.checkout(self.commitish)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["up-cpp"]

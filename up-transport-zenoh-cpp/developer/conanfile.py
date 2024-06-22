from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import copy


class upZenohTransportRecipe(ConanFile):
    name = "up-transport-zenoh-cpp"

    # Optional metadata
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of hello package here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")

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
            "fork": "eclipse-uprotocol/up-transport-zenoh-cpp",
            "commitish": "main"}

    requires = "zenohc/0.11.0.3", "up-cpp/0.2.0", "up-core-api/[>=1.5.8]", "spdlog/[>=1.13.0]", "protobuf/[>=3.21.12]"
    test_requires = "gtest/1.14.0"

    def source(self):
        # Workaround for compatibility with conan1 and conan2
        # https://github.com/conan-io/conan/issues/13506
        try:
            fork = self.options.fork
            commitish = self.options.commitish
        except:
            fork = self.info.options.fork
            commitish = self.info.options.commitish

        git = Git(self)
        git.clone("https://github.com/{}.git".format(fork), target=".")
        git.checkout(commitish)

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
        self.cpp_info.libs = ["up-transport-zenoh-cpp"]

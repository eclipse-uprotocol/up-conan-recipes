from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import copy


class UpClientSocket(ConanFile):
    name = "up-transport-socket-cpp"

    # Optional metadata
    license = "Apache-2.0 license"
    author = "Contributors to the Eclipse Foundation <uprotocol-dev@eclipse.org>"
    url = "https://github.com/eclipse-uprotocol/up-tck"
    description = "C++ up client socket library for testagent"
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
            "fork": "eclipse-uprotocol/up-tck",
            "commitish": "main"}

    requires = "up-core-api/[~1.6, include_prerelease]", "spdlog/[~1.13]", "protobuf/[~3.21]", "up-cpp/[^1.0, include_prerelease]", "fmt/10.2.1"

    def init(self):
        self.fork = self.options.get_safe("fork", "eclipse-uprotocol/up-tck")
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
        cmake.configure(build_script_folder="up_client_socket/cpp")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["up-transport-socket-cpp"]

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import copy
import os


class upCoreApiRecipe(ConanFile):
    name = "up-core-api"

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
            "fork": "eclipse-uprotocol/up-spec",
            "commitish": "main"}

    requires = "protobuf/3.21.12"

    def init(self):
        self.fork = self.options.get_safe("fork", "eclipse-uprotocol/up-spec")
        self.commitish = self.options.get_safe("commitish", "main")

    # We are providing our own cmake config since one is not included in the
    # spec repo.
    def export_sources(self):
        copy(self, "CMakeLists.txt",
             self.recipe_folder + "/..", self.export_sources_folder)

    def source(self):
        git = Git(self, folder="up-spec")
        git.clone(f"https://github.com/{self.fork}.git", target=".")
        git.checkout(self.commitish)
        os.symlink("up-spec/up-core-api", "up-core-api")

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
        self.cpp_info.libs = ["up-core-api"]

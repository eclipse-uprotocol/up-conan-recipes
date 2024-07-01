from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import copy
import os
import yaml

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
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def init(self):
        # Load data from conandata.yml
        conandata = self.load_conandata()
        version_data = conandata.get(self.version, {})
        
        # Default values
        default_fork = "eclipse-uprotocol/up-spec"
        default_commitish = "main"
        default_requirements = [("protobuf/3.21.12")]

        # Set fork with default fallback
        self.fork = version_data.get("fork", default_fork)
        if "fork" not in version_data:
            self.output.warning(f"Fork not specified in conandata.yml, using default: {default_fork}")

        # Set commitish with default fallback
        self.commitish = version_data.get("commitish", default_commitish)
        if "commitish" not in version_data:
            self.output.warning(f"Commitish not specified in conandata.yml, using default: {default_commitish}")
        
        # Handle requirements
        self.handle_requirements(version_data, default_requirements)

    def handle_requirements(self, version_data, default_requirements):
        if "requirements" in version_data:
            for requirement, version in version_data["requirements"].items():
                self.requires(f"{requirement}/{version}")
        else:
            self.output.warning("No requirements specified in conandata.yml. Please check your configuration.")
            self.output.warning("Using default requirements")
            for requirement in default_requirements:
                self.requires(requirement)



    def load_conandata(self):
        # Load conandata.yml
        conandata_path = os.path.join(self.recipe_folder, "conandata.yml")
        with open(conandata_path, "r") as f:
            return yaml.safe_load(f)

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

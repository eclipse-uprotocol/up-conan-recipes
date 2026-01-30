from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get
from conan.errors import ConanInvalidConfiguration

class upZenohTransportRecipe(ConanFile):
    name = "up-transport-zenoh-cpp"

    # Optional metadata
    license = "Apache-2.0"
    author = "Contributors to the Eclipse Foundation <uprotocol-dev@eclipse.org>"
    url = "https://github.com/eclipse-uprotocol/up-transport-zenoh-cpp"
    description = "This library provides a Zenoh-based uProtocol transport for C++ uEntities"
    topics = ("automotive", "iot", "uprotocol", "messaging")

    # Binary configuration
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "backend": ["zenoh-tmp", "zenoh-c", "zenoh-pico"],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "backend": "zenoh-tmp",
    }

    def validate(self):
        if self.settings.os == "Neutrino" and "zenoh-pico" != self.options.backend:
            raise ConanInvalidConfiguration(f"OS {self.settings.os}/{self.settings.arch} does not support {self.options.backend}")

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

        if "zenoh-tmp" == self.options.backend:
            version = version_data["zenoh-backend"]["zenoh-tmp"]
            self.requires(f"zenohcpp/{version}")
        elif "zenoh-c" == self.options.backend:
            version = version_data["zenoh-backend"]["zenoh-c"]
            self.requires(f"zenoh-cpp/{version}", options={"backend":"zenoh-c"})
            self.requires(f"zenoh-c/{version}")
        elif "zenoh-pico" == self.options.backend:
            version = version_data["zenoh-backend"]["zenoh-pico"]
            self.requires(f"zenoh-cpp/{version}", options={"backend":"zenoh-pico"})
            self.requires(f"zenoh-pico/{version}")
        else:
            raise ConanInvalidConfiguration(f"Zenoh backend: {self.options.backend} is not supported")

    def source(self):
        get(self, **self.conan_data[self.version]["sources"], strip_root=True)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        if "zenoh-tmp" == self.options.backend:
            tc.cache_variables["WITH_ZENOH_PICO"] = False
            tc.cache_variables["WITH_ZENOH_C"] = False
        elif "zenoh-c" == self.options.backend:
            tc.cache_variables["WITH_ZENOH_PICO"] = False
            tc.cache_variables["WITH_ZENOH_C"] = True
        elif "zenoh-pico" == self.options.backend:
            tc.cache_variables["WITH_ZENOH_PICO"] = True
            tc.cache_variables["WITH_ZENOH_C"] = False
        else:
            raise ConanInvalidConfiguration(f"Zenoh backend: {self.options.backend} is not supported")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["up-transport-zenoh-cpp"]

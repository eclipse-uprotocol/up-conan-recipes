from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, rmdir, rm, rename
from conan.tools.scm import Git

import os

class protobufRecipe(ConanFile):
    name = "protobuf"
    version = "3.21.12"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    #url = "<Package recipe repository url here, for issues about the package>"
    #homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "lite": [True, False],
        #"upb": [True, False], ##is not supported in v3.21.12
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "lite": False,
        #"upb": False, #is not supported in v3.21.12
    }

    def export_sources(self):
        copy(self, "protobuf-conan-protoc-target.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/qnx-ports/protobuf.git", target=".")
        git.checkout("qnx-v21.12")

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake", "protobuf")

    def generate(self):
        tc = CMakeToolchain(self)
        #tc.cache_variables["CMAKE_INSTALL_CMAKEDIR"] = self._cmake_install_base_path.replace("\\", "/") # not needed for v3.21.12
        #tc.cache_variables["QNX"] = True #only needed for test build - skipped for package
        tc.cache_variables["CMAKE_SYSTEM_NAME"] = "QNX"
        #tc.cache_variables["CMAKE_ASM_COMPILER"] = "qcc" #no needed for protobuf
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
        else:
            raise ConanInvalidConfiguration(f"Unsupported architecture: {self.settings.arch}")
        #tc.cache_variables["CONAN_CXX_FLAGS"] = "-D_XOPEN_SOURCE=700 -D_QNX_SOURCE" #Old approach did not recomended for conan2
        #tc.cache_variables["CONAN_C_FLAGS"] = "-D_XOPEN_SOURCE=700 -D_QNX_SOURCE" #Old approach did not recomended for conan2
        tc.cache_variables["CMAKE_CXX_FLAGS_INIT"] = "-D_XOPEN_SOURCE=700 -D_QNX_SOURCE"
        tc.cache_variables["CMAKE_C_FLAGS_INIT"] = "-D_XOPEN_SOURCE=700 -D_QNX_SOURCE"
        #tc.cache_variables["protobuf_INSTALL"] = False #It is a big misstake to set it False!!!! Deactivate cmake install()
        tc.cache_variables["protobuf_BUILD_TESTS"] = False
        #tc.cache_variables["protobuf_BUILD_LIBUPB"] = self.options.get_safe("upb") #is not supported in v3.21.12
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(cli_args=["--verbose"])

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install(cli_args=["--verbose"])
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        #rmdir(self, os.path.join(self.package_folder, "lib", "cmake", "utf8_range")) #no needs for v3.21.12

        #this is needed for version v3.21.12
        rename(self, os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-config.cmake"),
                    os.path.join(self.package_folder, self._cmake_install_base_path, "protobuf-generate.cmake"))

        cmake_config_folder = os.path.join(self.package_folder, self._cmake_install_base_path)
        rm(self, "protobuf-config*.cmake", folder=cmake_config_folder)
        rm(self, "protobuf-targets*.cmake", folder=cmake_config_folder)
        copy(self, "protobuf-conan-protoc-target.cmake", src=self.export_sources_folder, dst=cmake_config_folder)

        if not self.options.lite:
            rm(self, "libprotobuf-lite*", os.path.join(self.package_folder, "lib"))
            rm(self, "libprotobuf-lite*", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Protobuf")
        self.cpp_info.set_property("cmake_file_name", "protobuf")
        self.cpp_info.set_property("pkg_config_name", "protobuf_full_package") # unofficial, but required to avoid side effects (libprotobuf component "steals" the default global pkg_config name)

        build_modules = [
            os.path.join(self._cmake_install_base_path, "protobuf-generate.cmake"),
            os.path.join(self._cmake_install_base_path, "protobuf-module.cmake"),
            os.path.join(self._cmake_install_base_path, "protobuf-options.cmake"),
            os.path.join(self._cmake_install_base_path, "protobuf-conan-protoc-target.cmake"),
        ]
        self.cpp_info.set_property("cmake_build_modules", build_modules)

        # libprotobuf
        self.cpp_info.components["libprotobuf"].set_property("cmake_target_name", "protobuf::libprotobuf")
        self.cpp_info.components["libprotobuf"].set_property("pkg_config_name", "protobuf")
        self.cpp_info.components["libprotobuf"].builddirs.append(self._cmake_install_base_path)
        self.cpp_info.components["libprotobuf"].libs = ["protobuf"]

        # libprotoc
        self.cpp_info.components["libprotoc"].set_property("cmake_target_name", "protobuf::libprotoc")
        self.cpp_info.components["libprotoc"].libs = ["protoc"]
        self.cpp_info.components["libprotoc"].requires = ["libprotobuf"]

        # libprotobuf-lite
        if self.options.lite:
            self.cpp_info.components["libprotobuf-lite"].set_property("cmake_target_name", "protobuf::libprotobuf-lite")
            self.cpp_info.components["libprotobuf-lite"].set_property("pkg_config_name", "protobuf-lite")
            self.cpp_info.components["libprotobuf-lite"].builddirs.append(self._cmake_install_base_path)
            self.cpp_info.components["libprotobuf-lite"].libs = ["protobuf-lite"]

        #self.env_info.PATH.append(os.path.join(self.package_folder, "bin")) #NOT clear
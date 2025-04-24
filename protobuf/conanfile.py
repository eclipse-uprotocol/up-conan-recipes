from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, rename, replace_in_file, rmdir, rm, save
from conan.tools.scm import Git

import os

class protobufRecipe(ConanFile):
    name = "protobuf"
    version = "3.21.12"
    description = "Protocol Buffers - Google's data interchange format"
    topics = ("protocol-buffers", "protocol-compiler", "serialization", "rpc", "protocol-compiler")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/protocolbuffers/protobuf"
    license = "BSD-3-Clause"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_zlib": [True, False],
        "with_rtti": [True, False],
        "lite": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_zlib": True,
        "with_rtti": True,
        "lite": False,
    }

    @property
    def _is_clang_x86(self):
        return self.settings.compiler == "clang" and self.settings.arch == "x86"

    def export_sources(self):
        copy(self, "protobuf-conan-protoc-target.cmake", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_zlib and self.settings.os != "Neutrino":
            self.requires("zlib/[>=1.2.11 <2]")

    def validate(self):
        valid_os = ["Linux", "Neutrino"]
        if self.settings.os not in valid_os:
            raise ConanInvalidConfiguration(f"This package is not compatible with os {self.settings.os}")

        valid_archs = ["armv8", "x86_64"]
        if self.settings.arch not in valid_archs:
            raise ConanInvalidConfiguration(f"This package is not compatible with arch:{self.settings.arch}")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/qnx-ports/protobuf.git", target=".")
        git.checkout("qnx-v21.12")

    @property
    def _cmake_install_base_path(self):
        return os.path.join("lib", "cmake", "protobuf")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CMAKE_INSTALL_CMAKEDIR"] = self._cmake_install_base_path.replace("\\", "/")
        tc.cache_variables["protobuf_WITH_ZLIB"] = self.options.with_zlib
        tc.cache_variables["protobuf_BUILD_TESTS"] = False
        tc.cache_variables["protobuf_BUILD_PROTOC_BINARIES"] = True
        tc.cache_variables["protobuf_DEBUG_POSTFIX"] = ""
        tc.cache_variables["protobuf_BUILD_LIBPROTOC"] = True
        tc.cache_variables["protobuf_DISABLE_RTTI"] = not self.options.with_rtti
        tc.cache_variables["protobuf_BUILD_LIBUPB"] = False
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
        if self.settings.os == "Linux":
            # Use RPATH instead of RUNPATH to help with specific case
            # in the grpc recipe when grpc_cpp_plugin is run with protoc
            # in the same build. RPATH ensures that the rpath in the binary
            # is respected for transitive dependencies too
            project_include = os.path.join(self.generators_folder, "protobuf_project_include.cmake")
            save(self, project_include, "add_link_options(-Wl,--disable-new-dtags)")
            tc.variables["CMAKE_PROJECT_INCLUDE"] = project_include
            # Note: conan2 only could be:
            # tc.extra_exelinkflags.append("-Wl,--disable-new-dtags")
            # tc.extra_sharedlinkflags.append("-Wl,--disable-new-dtags")

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        # In older versions of protobuf, this file defines the `protobuf_generate` function
        protobuf_config_cmake = os.path.join(self.source_folder, "cmake", "protobuf-config.cmake.in")
        replace_in_file(self, protobuf_config_cmake, "@_protobuf_FIND_ZLIB@", "")
        replace_in_file(self, protobuf_config_cmake,
            "include(\"${CMAKE_CURRENT_LIST_DIR}/protobuf-targets.cmake\")",
            ""
        )

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build(cli_args=["--verbose"])

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install(cli_args=["--verbose"])
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

        #this is needed for version < 3.22.0
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
        if self.options.with_zlib and self.settings.os != "Neutrino": #zlib is default lib in QNX
            self.cpp_info.components["libprotobuf"].requires = ["zlib::zlib"]

        if self.settings.os == "Linux":
            self.cpp_info.components["libprotobuf"].system_libs.extend(["m", "pthread"])
            if self._is_clang_x86 or "arm" in str(self.settings.arch):
                self.cpp_info.components["libprotobuf"].system_libs.append("atomic")
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
            if self.settings.os == "Linux":
                self.cpp_info.components["libprotobuf-lite"].system_libs.extend(["m", "pthread"])
                if self._is_clang_x86 or "arm" in str(self.settings.arch):
                    self.cpp_info.components["libprotobuf-lite"].system_libs.append("atomic")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Protobuf"
        self.cpp_info.filenames["cmake_find_package_multi"] = "protobuf"
        self.cpp_info.names["pkg_config"] ="protobuf_full_package"
        for generator in ["cmake_find_package", "cmake_find_package_multi"]:
            self.cpp_info.components["libprotobuf"].build_modules[generator] = build_modules
        if self.options.lite:
            for generator in ["cmake_find_package", "cmake_find_package_multi"]:
                self.cpp_info.components["libprotobuf-lite"].build_modules[generator] = build_modules
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))

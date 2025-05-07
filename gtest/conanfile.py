from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, rm, rmdir
from conan.tools.scm import Git
import os

required_conan_version = ">=2.1"


class GTestConan(ConanFile):
    name = "gtest"
    version = "1.13.0"
    description = "Google's C++ test framework"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/googletest"
    topics = ("testing", "google-testing", "unit-test")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_gmock": [True, False],
        "no_main": [True, False],
        "hide_symbols": [True, False],
        "disable_pthreads": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_gmock": True,
        "no_main": False,
        "hide_symbols": False,
        "disable_pthreads": False,
    }
    # disallow cppstd compatibility, as it affects the ABI in this library
    # see https://github.com/conan-io/conan-center-index/issues/23854
    # Requires Conan >=1.53.0 <2 || >=2.1.0 to work
    extension_properties = {"compatibility_cppstd": False}

# not needed for QNX Neutrino
#    def export_sources(self):
#        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src") #internal source name within Conan

    def package_id(self):
        del self.info.options.no_main # Only used to expose more targets

    def validate(self):
        valid_os = ["Neutrino"]
        if self.settings.os not in valid_os:
            raise ConanInvalidConfiguration(f"This package is not compatible with os {self.settings.os}")

    def source(self):
        git = Git(self)
        git.clone(url="https://github.com/qnx-ports/googletest.git", target=".")
        git.checkout("qnx_v1.13.0")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_GMOCK"] = self.options.build_gmock
        tc.variables["gtest_hide_internal_symbols"] = self.options.hide_symbols
        tc.variables["gtest_disable_pthreads"] = self.options.disable_pthreads
        if self.settings.os == "Neutrino":
            tc.cache_variables["CMAKE_SYSTEM_NAME"] = "QNX"
            tc.cache_variables["CMAKE_CXX_COMPILER"] = "q++"
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
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_file_name", "GTest")

        # gtest
        self.cpp_info.components["libgtest"].set_property("cmake_target_name", "GTest::gtest")
        self.cpp_info.components["libgtest"].set_property("cmake_target_aliases", ["GTest::GTest"])
        self.cpp_info.components["libgtest"].set_property("pkg_config_name", "gtest")
        self.cpp_info.components["libgtest"].libs = ["gtest"]
        if self.settings.os == "Neutrino":
            self.cpp_info.components["libgtest"].system_libs.append("regex")
        if self.options.shared:
            self.cpp_info.components["libgtest"].defines.append("GTEST_LINKED_AS_SHARED_LIBRARY=1")

        # gtest_main
        if not self.options.no_main:
            self.cpp_info.components["gtest_main"].set_property("cmake_target_name", "GTest::gtest_main")
            self.cpp_info.components["gtest_main"].set_property("cmake_target_aliases", ["GTest::Main"])
            self.cpp_info.components["gtest_main"].set_property("pkg_config_name", "gtest_main")
            self.cpp_info.components["gtest_main"].libs = ["gtest_main"]
            self.cpp_info.components["gtest_main"].requires = ["libgtest"]

        # gmock
        if self.options.build_gmock:
            self.cpp_info.components["gmock"].set_property("cmake_target_name", "GTest::gmock")
            self.cpp_info.components["gmock"].set_property("pkg_config_name", "gmock")
            self.cpp_info.components["gmock"].libs = ["gmock"]
            self.cpp_info.components["gmock"].requires = ["libgtest"]

            # gmock_main
            if not self.options.no_main:
                self.cpp_info.components["gmock_main"].set_property("cmake_target_name", "GTest::gmock_main")
                self.cpp_info.components["gmock_main"].set_property("pkg_config_name", "gmock_main")
                self.cpp_info.components["gmock_main"].libs = ["gmock_main"]
                self.cpp_info.components["gmock_main"].requires = ["gmock"]

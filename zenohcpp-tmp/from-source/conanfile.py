#
# Copyright (c) 2024 ZettaScale Technology
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ZettaScale Zenoh Team, <zenoh@zettascale.tech>
#
from conan import ConanFile
from conan.tools.files import copy, download, get
from conan.tools.cmake import cmake_layout
from conan.tools.cmake import CMake, CMakeToolchain

import platform
import os

required_conan_version = ">=1.53.0"

class ZenohCppPackageConan(ConanFile):
    name = "zenohcpp"
    description = "C++ API for Eclipse Zenoh: Zero Overhead Pub/Sub, Store/Query and Compute protocol"
    tags = ["iot", "networking", "robotics", "messaging", "ros2", "edge-computing", "micro-controller", "header-only"]
    license = "EPL-2.0 OR Apache-2.0"
    author = "ZettaScale Zenoh Team <zenoh@zettascale.tech>"

    url = "https://github.com/eclipse-zenoh/zenoh-cpp"
    homepage = "https://github.com/eclipse-zenoh/zenoh-cpp"

    package_type = "header-library"
    generators = "CMakeDeps", "CMakeToolchain"

    options = { }
    default_options = { }
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        self.cpp.package.includedirs = ["include"]
        cmake_layout(self)

    def requirements(self):
        self.requires("zenohc/{}".format(self.version))

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.build_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure(
            build_script_folder=self.conan_data["build"][self.version]["build_script_folder"]
        )
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zenohcpp")
        self.cpp_info.set_property("cmake_target_name", "zenohcpp::lib")

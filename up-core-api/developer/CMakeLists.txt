cmake_minimum_required(VERSION 3.18)
project(up-core-api VERSION 1.5.8 LANGUAGES CXX DESCRIPTION "uProtocol Core API")

find_package(protobuf CONFIG REQUIRED)
if (IS_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/up-core-api/uprotocol/")
    set(MY_IMPORT_DIRS "${CMAKE_CURRENT_SOURCE_DIR}/up-core-api/uprotocol/")
else()
    message(FATAL_ERROR "Could not find up-core-api.")
endif()

####################################################################
# Use protoc to generate the C++ headers / sources from .proto files
set(CMAKE_CURRENT_SOURCE_DIR ${MY_IMPORT_DIRS})

file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/uprotocol")
set(MY_PROTOC_OUT_DIR ${CMAKE_BINARY_DIR}/uprotocol)

#Load up all the proto files that need to be compiled via protoc (into header/source files)
file(GLOB_RECURSE PROTO_FILES ${MY_IMPORT_DIRS}/*.proto)

#Create an INTERFACE to hold the generated proto files
add_library(up-core-api-protos INTERFACE ${PROTO_FILES})

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS TARGET up-core-api-protos IMPORT_DIRS ${MY_IMPORT_DIRS} PROTOC_OUT_DIR ${MY_PROTOC_OUT_DIR})
protobuf_generate(LANGUAGE cpp TARGET up-core-api-protos PROTOS ${PROTO_FILES} IMPORT_DIRS ${MY_IMPORT_DIRS} PROTOC_OUT_DIR ${MY_PROTOC_OUT_DIR})

##########################
# Build the actual library
add_library(up-core-api)
target_include_directories(up-core-api
	PUBLIC
	${CMAKE_BINARY_DIR}
	${MY_PROTOC_OUT_DIR}
	${protobuf_INCLUDE_DIRS}
)
target_link_libraries(up-core-api ${protobuf_LIBRARIES})
target_sources(up-core-api
	PRIVATE
	${PROTO_HDRS}
	${PROTO_SRCS}
)

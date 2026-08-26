cmake_minimum_required(VERSION 3.16)

project(dd_canvas VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(DD_BUILD_DOCS "Build Doxygen documentation when Doxygen is available" ON)

define_property(TARGET PROPERTY DD_PUBLIC_API_HEADERS)

add_library(dd_canvas
    src/canvas.cpp
    src/ppm_writer.cpp
)

target_include_directories(dd_canvas
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)
set_target_properties(dd_canvas PROPERTIES
    OUTPUT_NAME dd_canvas
    DD_PUBLIC_API_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/include/dd_canvas/canvas.hpp;${CMAKE_CURRENT_SOURCE_DIR}/include/dd_canvas/ppm_writer.hpp"
)

add_executable(dd_demo app/main.cpp)
target_link_libraries(dd_demo PRIVATE dd_canvas)

include(CTest)
if(BUILD_TESTING)
    add_executable(dd_canvas_tests tests/canvas_tests.cpp)
    target_link_libraries(dd_canvas_tests PRIVATE dd_canvas)
    add_test(NAME dd_canvas_tests COMMAND dd_canvas_tests)
endif()

if(DD_BUILD_DOCS)
    find_package(Doxygen QUIET)
    if(DOXYGEN_FOUND)
        set(DOXYGEN_INPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")
        set(DOXYGEN_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/docs")
        configure_file(${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile @ONLY)
        add_custom_target(dd_docs
            COMMAND ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            COMMENT "Generating API documentation"
            VERBATIM
        )
    else()
        message(STATUS "Doxygen not found; target dd_docs will not be available")
    endif()
endif()

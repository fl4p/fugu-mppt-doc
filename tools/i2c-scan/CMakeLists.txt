# The following lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)

include_directories($ENV{IDF_PATH}/components/driver/include)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(i2c-scan)


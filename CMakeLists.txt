################################################################################
# Project:  Lib PyQt
# Purpose:  CMake build scripts
# Author:   Dmitry Baryshnikov, dmitry.baryshnikov@nexgis.com
################################################################################
# Copyright (C) 2017, NextGIS <info@nextgis.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################
cmake_minimum_required(VERSION 2.8.12 FATAL_ERROR)

project(pyqt4)

# some init settings
set(CMAKE_COLOR_MAKEFILE ON)
# set path to additional CMake modules
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})

include(util)
check_version(PYQT_MAJOR_VERSION PYQT_MINOR_VERSION)
set(VERSION "${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}")
report_version(${PROJECT_NAME} ${VERSION})

set(INSTALL_SIP_DIR ${CMAKE_INSTALL_PREFIX}/share/pyqt4)

set(CONFIGURE_ARGS --destdir ${CMAKE_INSTALL_PREFIX})
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --confirm-license --no-docstrings --qsci-api)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --bindir ${CMAKE_INSTALL_PREFIX}/bin)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --qsci-api-destdir ${CMAKE_INSTALL_PREFIX}/qsci)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --sipdir ${INSTALL_SIP_DIR})

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --debug)
endif()

set(DOWNLOAD_URL "http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}")
if(WIN32)
    # http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_win-4.12.zip
    set(PYQT_INPUT_NAME "PyQt4_gpl_win-${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}")
    set(DOWNLOAD_URL "${DOWNLOAD_URL}/${PYQT_INPUT_NAME}.zip")
elseif(APPLE)
    # http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_mac-4.12.tar.gz
    set(PYQT_INPUT_NAME "PyQt4_gpl_mac-${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}")
    set(DOWNLOAD_URL "${DOWNLOAD_URL}/${PYQT_INPUT_NAME}.tar.gz")
else()
    # http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_x11-4.12.tar.gz
    set(PYQT_INPUT_NAME "PyQt4_gpl_x11-${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}")
    set(DOWNLOAD_URL "${DOWNLOAD_URL}/${PYQT_INPUT_NAME}.tar.gz")
endif()
set(OUT_NAME "pyqt.tar.gz")

if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}")
    status_message("Download ${DOWNLOAD_URL}")
    file(DOWNLOAD "${DOWNLOAD_URL}" "${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}"
         SHOW_PROGRESS
     )
endif()

include(ProcessorCount)
ProcessorCount(CPU_COUNT)
if(NOT CPU_COUNT OR CPU_COUNT EQUAL 0)
    set(CPU_COUNT 1)
endif()

find_package(PythonInterp REQUIRED)

include(FindAnyProject)

find_anyproject(SIP REQUIRED)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --sip ${SIP_BINARY_PATH} --sip-incdir ${SIP_INCLUDE_DIR} -j ${CPU_COUNT})

find_anyproject(Qt4 REQUIRED COMPONENTS QtCore)

set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --qmake ${QT_QMAKE_EXECUTABLE})

message(STATUS "Configure args: ${CONFIGURE_ARGS}")

if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME})
    status_message("Extract ${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}")
    execute_process(COMMAND ${CMAKE_COMMAND} -E tar xzf ${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME})
endif()

execute_process(COMMAND ${CMAKE_COMMAND} -E copy_if_different
          ${CMAKE_SOURCE_DIR}/cmake/configure-ng.py.in
          ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/configure-ng.py
)
# file(REMOVE "${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}/configure-ng.py")
# configure_file(${CMAKE_SOURCE_DIR}/cmake/configure-ng.py.in ${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}/configure-ng.py COPYONLY)

status_message("Configure")
execute_process(COMMAND ${PYTHON_EXECUTABLE} configure-ng.py ${CONFIGURE_ARGS}
    OUTPUT_FILE ${CMAKE_CURRENT_BINARY_DIR}/configure.out
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
)

file(STRINGS ${CMAKE_CURRENT_BINARY_DIR}/configure.out CONF_OUT)

foreach(CONF_OUT_LINE ${CONF_OUT})
    if(CONF_OUT_LINE MATCHES "SIP FLAGS:")
        string(SUBSTRING ${CONF_OUT_LINE} 11 -1 INSTALL_SIP_FLAGS)
    endif()
endforeach()

#TODO: Fix on WINDOWS
add_custom_target(build_qt ALL make -j ${CPU_COUNT}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
    VERBATIM
)

install(CODE "execute_process(
              COMMAND make install
              WORKING_DIRECTORY  ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
             )"
)

if(OSX_FRAMEWORK)
    install(CODE "execute_process(COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_SOURCE_DIR}/cmake/mac_rpath_fix.py ${QT_LIBRARY_DIR}
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        )"
    )
endif()

if (REGISTER_PACKAGE)
    set(EXPORT_PACKAGE_NAME PyQt4)
    string(TOUPPER ${EXPORT_PACKAGE_NAME} EXPORT_PACKAGE_NAME_UPPER)
    set(EXPORT_PACKAGE_LIB_NAME qt4)

    export(PACKAGE ${EXPORT_PACKAGE_NAME})

    include(CMakePackageConfigHelpers)
    configure_package_config_file(
        ${CMAKE_SOURCE_DIR}/cmake/PackageConfig.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/${EXPORT_PACKAGE_NAME}Config.cmake
        INSTALL_DESTINATION ${CMAKE_CURRENT_BINARY_DIR} )
    write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/${EXPORT_PACKAGE_NAME}ConfigVersion.cmake
        VERSION ${VERSION}
        COMPATIBILITY AnyNewerVersion )
endif()

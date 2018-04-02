################################################################################
# Project:  Lib PyQt
# Purpose:  CMake build scripts
# Author:   Dmitry Baryshnikov, dmitry.baryshnikov@nexgis.com
################################################################################
# Copyright (C) 2017-2018, NextGIS <info@nextgis.com>
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

if(NOT DEFINED PACKAGE_VENDOR)
    set(PACKAGE_VENDOR NextGIS)
endif()

if(NOT DEFINED PACKAGE_BUGREPORT)
    set(PACKAGE_BUGREPORT info@nextgis.com)
endif()

# some init settings
set(CMAKE_COLOR_MAKEFILE ON)
# set path to additional CMake modules
set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake ${CMAKE_MODULE_PATH})

if(OSX_FRAMEWORK AND (BUILD_SHARED_LIBS OR BUILD_STATIC_LIBS))
  message(FATAL_ERROR "Only OSX_FRAMEWORK key or any or both BUILD_SHARED_LIBS
                       and BUILD_STATIC_LIBS keys are permitted")
endif()

if(OSX_FRAMEWORK)
    set(CMAKE_MACOSX_RPATH ON)
endif()

set(INSTALL_CMAKECONF_DIR CMake CACHE INTERNAL "Installation directory for cmake config files" FORCE)

if(NOT WITH_PYTHON2 AND NOT WITH_PYTHON3)
    set(WITH_PYTHON2 ON)
endif()

if(WITH_PYTHON2)
    find_package(PythonInterp 2)
    if(PYTHONINTERP_FOUND)
        set(PYTHON2_EXECUTABLE ${PYTHON_EXECUTABLE})
        set(PYTHON2_VERSION_MAJOR ${PYTHON_VERSION_MAJOR})
        set(PYTHON2_VERSION_MINOR ${PYTHON_VERSION_MINOR})
    else()
        message(WARNING "Cannot find python 2")
    endif()
endif()

unset(PYTHONINTERP_FOUND)
unset(PYTHON_EXECUTABLE)
unset(PYTHON_VERSION_MAJOR)
unset(PYTHON_VERSION_MINOR)

if(WITH_PYTHON3)
    # Hack, not find python3 withouut this
    find_program(PYTHON3_EXECUTABLE python3)
    set(PYTHON_EXECUTABLE ${PYTHON3_EXECUTABLE})

    find_package(PythonInterp 3)
    if(PYTHONINTERP_FOUND)
        set(PYTHON3_EXECUTABLE ${PYTHON_EXECUTABLE})
        set(PYTHON3_VERSION_MAJOR ${PYTHON_VERSION_MAJOR})
        set(PYTHON3_VERSION_MINOR ${PYTHON_VERSION_MINOR})
    else()
        message(WARNING "Cannot find python 3")
    endif()
endif()

if(NOT PYTHON2_EXECUTABLE AND NOT PYTHON3_EXECUTABLE)
    message(FATAL_ERROR "Cannot find python")
endif()

if(PYTHON2_EXECUTABLE)
    set(PYTHON_EXECUTABLE ${PYTHON2_EXECUTABLE})
    set(PYTHON_VERSION_MAJOR ${PYTHON2_VERSION_MAJOR})
    set(PYTHON_VERSION_MINOR ${PYTHON2_VERSION_MINOR})
else()
    set(PYTHON_EXECUTABLE ${PYTHON3_EXECUTABLE})
    set(PYTHON_VERSION_MAJOR ${PYTHON3_VERSION_MAJOR})
    set(PYTHON_VERSION_MINOR ${PYTHON3_VERSION_MINOR})
endif()

include(util)
check_version(PYQT_MAJOR_VERSION PYQT_MINOR_VERSION PYQT_PATCH_VERSION)
set(VERSION "${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}.${PYQT_PATCH_VERSION}")
report_version(${PROJECT_NAME} ${VERSION})

set(TMP_INSTALL_PREFIX "${CMAKE_CURRENT_BINARY_DIR}/inst")

set(INSTALL_SIP_DIR share/pyqt4)

if(OSX_FRAMEWORK)
    set(INSTALL_PYTHON_DIR Library/Python/${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages)
else()
    set(INSTALL_PYTHON_DIR lib/python${PYTHON_VERSION_MAJOR}${PYTHON_VERSION_MINOR}/site-packages)
endif()
set(CONFIGURE_ARGS --destdir ${TMP_INSTALL_PREFIX}/${INSTALL_PYTHON_DIR})

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --debug)
endif()

set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --confirm-license --no-docstrings --qsci-api)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --bindir ${TMP_INSTALL_PREFIX}/bin)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --qsci-api-destdir ${TMP_INSTALL_PREFIX}/qsci)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --sipdir ${TMP_INSTALL_PREFIX}/${INSTALL_SIP_DIR})


if(OSX_FRAMEWORK)
    set(FLAGS "ARCHFLAGS=-arch x86_64")
elseif(WIN32)
    if(MSVC_VERSION EQUAL 1400)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS80COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1500)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS90COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1600)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS100COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1700)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS110COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1800)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS120COMNTOOLS}")
    elseif(MSVC_VERSION EQUAL 1900)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=$ENV{VS140COMNTOOLS}")
    else() # 1912 - Need to copy vcvarsall.bat from VC\Auxiliary\Build to VC
        get_filename_component(_COMNTOOLS_PREFIX "${CMAKE_C_COMPILER}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        # get_filename_component(_COMNTOOLS_PREFIX "${_COMNTOOLS_PREFIX}" PATH)
        set(FLAGS ${FLAGS} "VS90COMNTOOLS=${_COMNTOOLS_PREFIX}")
    endif()
else()
    set(FLAGS "NextGIS=TRUE")
endif()

if(PYQT_PATCH_VERSION EQUAL 0)
    set(PYQT_INPUT_VERSION "${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}")
else()
    set(PYQT_INPUT_VERSION "${PYQT_MAJOR_VERSION}.${PYQT_MINOR_VERSION}.${PYQT_PATCH_VERSION}")
endif()

set(DOWNLOAD_URL "http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-${PYQT_INPUT_VERSION}")
if(WIN32)
    # http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_win-4.12.zip
    set(PYQT_INPUT_NAME "PyQt4_gpl_win-${PYQT_INPUT_VERSION}")
    set(DOWNLOAD_URL "${DOWNLOAD_URL}/${PYQT_INPUT_NAME}.zip")
elseif(APPLE)
    # http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_mac-4.12.tar.gz
    set(PYQT_INPUT_NAME "PyQt4_gpl_mac-${PYQT_INPUT_VERSION}")
    set(DOWNLOAD_URL "${DOWNLOAD_URL}/${PYQT_INPUT_NAME}.tar.gz")
else()
    # http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.12/PyQt4_gpl_x11-4.12.tar.gz
    set(PYQT_INPUT_NAME "PyQt4_gpl_x11-${PYQT_INPUT_VERSION}")
    set(DOWNLOAD_URL "${DOWNLOAD_URL}/${PYQT_INPUT_NAME}.tar.gz")
endif()
set(OUT_NAME "pyqt.tar.gz")

if(NOT EXISTS "${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}")
    status_message("Download ${DOWNLOAD_URL}")
    file(DOWNLOAD "${DOWNLOAD_URL}" "${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}"
         SHOW_PROGRESS
     )
endif()

if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME})
    status_message("Extract ${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME}")
    execute_process(COMMAND ${CMAKE_COMMAND} -E tar xzf ${CMAKE_CURRENT_BINARY_DIR}/${OUT_NAME})
endif()

include(FindAnyProject)

find_anyproject(SIP REQUIRED)
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --sip ${SIP_BINARY_PATH} --sip-incdir ${SIP_INCLUDE_DIR})

find_anyproject(ZLIB REQUIRED)
find_anyproject(Qt4 REQUIRED COMPONENTS QtCore)
# Create qt.conf
get_property(QT_QMAKE_EXECUTABLE TARGET Qt4::qmake PROPERTY IMPORTED_LOCATION)
get_filename_component(QT_BIN_DIR "${QT_QMAKE_EXECUTABLE}" PATH)
get_filename_component(QT_ROOT_DIR "${QT_BIN_DIR}" PATH)
file(WRITE ${QT_BIN_DIR}/qt.conf "[Paths]\nPrefix = ${QT_ROOT_DIR}")
set(CONFIGURE_ARGS ${CONFIGURE_ARGS} --qmake=${QT_QMAKE_EXECUTABLE})
file(READ ${PROJECT_SOURCE_DIR}/cmake/configure-ng.py.in _CONF)

if(OSX_FRAMEWORK)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/qt.conf "[Paths]\nPrefix = ${QT_ROOT_DIR}")
    get_filename_component(ZLIB_ROOT_DIR "${ZLIB_INCLUDE_DIRS}" PATH)
    get_filename_component(ZLIB_ROOT_DIR "${ZLIB_ROOT_DIR}" PATH)

    string(REPLACE "pro_lines.append('CONFIG -= cmake')" "pro_lines.append('CONFIG -= app_bundle')
    pro_lines.append('unix:QMAKE_LFLAGS += \\\"-Wl,-rpath,\\'${QT_ROOT_DIR}/lib\\' -Wl,-rpath,\\'${ZLIB_ROOT_DIR}\\'\\\"')
" _CONF "${_CONF}")
    string(REPLACE "os.path.join(target_config.pyqt_module_dir" "os.path.join('..', '${INSTALL_PYTHON_DIR}'" _CONF "${_CONF}")
elseif(WIN32)
    file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/release/qt.conf "[Paths]\nPrefix = ${QT_ROOT_DIR}")
    file(COPY ${QT_ROOT_DIR}/lib/QtCore4.dll DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/release/)
    file(GLOB PRLS "${QT_ROOT_DIR}/lib/*.prl")
    file(REMOVE ${PRLS})
    get_filename_component(VC_COMPILER_DIR ${CMAKE_CXX_COMPILER} DIRECTORY)
    find_file(VCVARSALL_BAT
        NAMES vsdevcmd.bat vcvarsall.bat
        PATHS "${VC_COMPILER_DIR}/.." "${VC_COMPILER_DIR}/../.." "${VC_COMPILER_DIR}/../../../../../../../.." "${VC_COMPILER_DIR}/../../../../../../.."
        PATH_SUFFIXES "Common7/Tools" "Tools"
    )

    get_filename_component(ZLIB_ROOT_DIR "${ZLIB_INCLUDE_DIRS}" PATH)
    file(COPY ${ZLIB_ROOT_DIR}/bin/zlib1.dll DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/release/)

    if(DEFINED CMAKE_GENERATOR)
        # TODO: Need different arguments for vsdevcmd.bat and vcvarsall.bat. Now support only VC2017
        string(FIND ${CMAKE_GENERATOR} "Win64" POS)
        if(POS GREATER -1)
            set(VCVARSALL_BAT_ARG -arch=amd64)
        else()
            set(VCVARSALL_BAT_ARG -arch=x86)
        endif()
    endif()

    message(STATUS "VCVARSALL_BAT: ${VCVARSALL_BAT} ${VCVARSALL_BAT_ARG}")
endif()
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/configure-ng.py "${_CONF}")

message(STATUS "Configure args: ${CONFIGURE_ARGS}")

macro(build_py ver)
    if(WIN32)
        string(REPLACE ";" "  " CONFIGURE_ARGS "${CONFIGURE_ARGS}")
        file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/conf.bat "@echo off
call \"${VCVARSALL_BAT}\" ${VCVARSALL_BAT_ARG}
cd ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
set ${FLAGS}
${PYTHON${ver}_EXECUTABLE} configure-ng.py ${CONFIGURE_ARGS}
")

        file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/make.bat "@echo off
call \"${VCVARSALL_BAT}\" ${VCVARSALL_BAT_ARG}
cd ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
set ${FLAGS}
%1 %2
")
        set(CONFIGURE_CMD ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/make.bat)
        set(_CMD ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/conf.bat)
    else()
        set(CONFIGURE_CMD ${CMAKE_COMMAND} -E env "${FLAGS}")
        set(_CMD ${CONFIGURE_CMD} ${PYTHON${ver}_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}/configure-ng.py ${CONFIGURE_ARGS})
    endif()

    status_message("Configure in ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}\nCOMMAND: ${_CMD}\nENV: ${FLAGS}")
    execute_process(COMMAND ${_CMD}
        OUTPUT_FILE ${CMAKE_CURRENT_BINARY_DIR}/configure.out
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
    )

    file(STRINGS ${CMAKE_CURRENT_BINARY_DIR}/configure.out CONF_OUT)

    foreach(CONF_OUT_LINE ${CONF_OUT})
        if(CONF_OUT_LINE MATCHES "SIP FLAGS:")
            string(SUBSTRING ${CONF_OUT_LINE} 11 -1 INSTALL_SIP_FLAGS)
        endif()
    endforeach()

    if(WIN32)
        add_custom_target(build_py${ver} ALL
            COMMAND ${CONFIGURE_CMD} nmake
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
            VERBATIM
        )
        add_custom_target(install_py${ver} ALL
            COMMAND ${CONFIGURE_CMD} nmake install
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
            DEPENDS build_py${ver}
            VERBATIM
        )
    else()
        add_custom_target(build_py${ver} ALL
            COMMAND ${CONFIGURE_CMD} make
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
            VERBATIM
        )
        add_custom_target(install_py${ver} ALL
            COMMAND ${CONFIGURE_CMD} make install
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${PYQT_INPUT_NAME}
            DEPENDS build_py${ver}
            VERBATIM
        )
    endif()

    if(OSX_FRAMEWORK)
        add_custom_target(fix_py${ver} ALL
            COMMAND ${CONFIGURE_CMD}
            ${PYTHON${ver}_EXECUTABLE} ${CMAKE_SOURCE_DIR}/cmake/mac_rpath_fix.py
            WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
            DEPENDS install_py${ver}
            VERBATIM
        )
    endif()

endmacro()

if(PYTHON2_EXECUTABLE)
    build_py(2)
endif()

if(PYTHON3_EXECUTABLE)
    build_py(3)
endif()

set(PACKAGE_NAME ${PROJECT_NAME})
string(TOUPPER ${PACKAGE_NAME} PACKAGE_UPPER_NAME)

if(WIN32)
    set(INSTALL_PYUIC_PROGRAM bin/pyuic4.bat)
    set(INSTALL_PYRCC_PROGRAM bin/pyrcc4.exe)
    set(INSTALL_PYLUPDATE_PROGRAM bin/pylupdate4.exe)
else()
    set(INSTALL_PYUIC_PROGRAM bin/pyuic4)
    set(INSTALL_PYRCC_PROGRAM bin/pyrcc4)
    set(INSTALL_PYLUPDATE_PROGRAM bin/pylupdate4)
endif()

configure_file(cmake/PackageConfig.cmake.in
    ${PROJECT_BINARY_DIR}/${PACKAGE_UPPER_NAME}Config.cmake @ONLY)

if(NOT SKIP_INSTALL_LIBRARIES AND NOT SKIP_INSTALL_ALL )
    install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/inst/ DESTINATION "." USE_SOURCE_PERMISSIONS)
    install(FILES
      ${PROJECT_BINARY_DIR}/${PACKAGE_UPPER_NAME}Config.cmake
      DESTINATION ${INSTALL_CMAKECONF_DIR} COMPONENT dev)
endif()

# Archiving ====================================================================
set(PACKAGE_NAME ${PROJECT_NAME})

set(CPACK_PACKAGE_NAME "${PACKAGE_NAME}")
set(CPACK_PACKAGE_VENDOR "${PACKAGE_VENDOR}")
set(CPACK_PACKAGE_VERSION "${VERSION}")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "${PACKAGE_NAME} Installation")
set(CPACK_PACKAGE_RELOCATABLE TRUE)
set(CPACK_ARCHIVE_COMPONENT_INSTALL ON)
set(CPACK_GENERATOR "ZIP")
set(CPACK_MONOLITHIC_INSTALL ON)
set(CPACK_STRIP_FILES TRUE)

# Get cpack zip archive name
get_cpack_filename(${VERSION} PROJECT_CPACK_FILENAME)
set(CPACK_PACKAGE_FILE_NAME ${PROJECT_CPACK_FILENAME})

include(CPack)

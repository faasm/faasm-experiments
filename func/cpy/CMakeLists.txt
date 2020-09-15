set(CPYTHON_ROOT ${CMAKE_CURRENT_LIST_DIR}/../../third-party/cpython)
set(CPYTHON_INSTALL ${CPYTHON_ROOT}/install/wasm)

if(FAASM_BUILD_TYPE STREQUAL "wasm")
    # Python library to statically link
    set(PYTHON_LIBRARIES ${CPYTHON_INSTALL}/lib/libpython3.8.a)
    set(PYTHON_INCLUDE_DIRS ${CPYTHON_INSTALL}/include/python3.8)
else()
    find_package(PythonLibs)
endif()

message(STATUS "Python libs: ${PYTHON_LIBRARIES}")
message(STATUS "Python incl: ${PYTHON_INCLUDE_DIRS}")

include_directories(${PYTHON_INCLUDE_DIRS})

add_executable(mini mini.cpp)
target_link_libraries(mini faasm ${PYTHON_LIBRARIES})


cmake_minimum_required(VERSION 3.29)
project(sphenix_pp_qa)

set(CMAKE_CXX_STANDARD 14)

add_executable(sphenix_pp_qa
    pp_crossing_angles/ReadSpinDB.C
    pp_crossing_angles/spindb_test.cpp)

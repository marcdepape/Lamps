cmake_minimum_required(VERSION 2.8)

project(lamps)

find_package(PkgConfig)

pkg_check_modules(GST REQUIRED gstreamer-1.0)
pkg_check_modules(GSTRTSP REQUIRED gstreamer-rtsp-server-1.0)

include_directories(
	${GST_INCLUDE_DIRS}
	${GSTRTSP_INCLUDE_DIRS}
	)

link_directories(/usr/local/lib)

add_executable(lamps-server lamps-server.cpp)

target_link_libraries(lamps-server 
	${GST_LIBRARIES}
	${GSTRTSP_LIBRARIES}
	)

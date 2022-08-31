import cffi
import pathlib
import os

ffi = cffi.FFI()
dir = pathlib.Path().absolute()
h_file_name = os.path.join(dir, "RTC6impl.h")
with open(h_file_name) as h_file:
    ffi.cdef(h_file.read())

ffi.set_source("RTC6Static", 'include "RTC6impl.h"', libraries=["RTC6DLL"], library_dirs=[dir.as_posix()], extra_link_args=["-Wl,-rpath,."])
ffi.compile()
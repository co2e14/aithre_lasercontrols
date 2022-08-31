from ctypes import cdll
import time

RTC6_openclose = cdll.LoadLibrary("RTC6_2.so")
RTC6 = cdll.LoadLibrary("RTC6DLLx64.dll")
RTC6_openclose.RTC6open()
time.sleep(5)
print(RTC6.get_rtc_version())
RTC6_openclose.RTC6close()

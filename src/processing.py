from time import sleep

from controller.Device import Device
from controller.APK import APK, APKRuntime 
from controller.Procs import Procs
from controller.MemInfo import MemInfo
from controller.Meow import Meow
from injector import inject

apk_path = "../factory/reactor/apk.apk"

if __name__ == "__main__":
  # AVD Checking...
  dev = Device()
  while not dev.check_device():
    print "waiting for device connection..."
    sleep(3)

  print "AVD Connected Successfully..."
  print 

  # System Utility Initialization...
  proc_service = Procs()
  mem_service  = MemInfo()
  log_service  = Meow()

  log_service.thread_up()

  # Set Up Apk

  # !!! untreated threatens with relative path
  # see this:
  # stackoverflow.com/questions/7162366/get-location-of-the-py-source-file
  inject.place_injector()
  inject.inject_main_activitya()

  apk = APK(apk_path)
  apk_runtime = APKRuntime(apk)

  apk_runtime.install()
  sleep(3)
  log_service.clear()
  log_service.turn_on(apk.package_name)
  sleep(2)
  apk_runtime.start()
  sleep(4)
  log_service.turn_off
  log_service.refresh()


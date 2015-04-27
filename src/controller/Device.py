from time import sleep
import subprocess


class Device:
  def __init__(self):
    pass

  def check_device(self):
    p = subprocess.Popen(["adb", "devices"], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if not err is None:
      # raise ApeDroidError("adb devices execution error.")
      exit(1)
    if(":" not in out):
      # raise ApeDroidError("No Android device attached.")
      return False
    else:
      return True


if __name__ == "__main__":
  dev = Device()
  while not dev.check_device():
    print "waiting for device connection..."
    sleep(3)

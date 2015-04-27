import subprocess
import re

class MemInfo:
  mem_re = re.compile("^(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+).*$")
  mem_info = None
  # lock


  def __init__(self):
    self.update()


  def check_device(self):
    return True


  def update(self):
    if not self.check_device():
      self.err("ERR : device does not exist.")
      return False
    p = subprocess.Popen(["adb", "shell", "procrank"], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if err is None:
      new_mem = []
      for line in out.split("\r\n"):
        match = MemInfo.mem_re.match(line.strip())
        if not match is None:
          pid, vss, rss, pss, uss, cmd = match.groups()
          new_mem.append([pid, pss, uss, cmd])
      # acquire lock
      MemInfo.mem_info = new_mem
      # release lock
    else:
      self.err(err)
      return False

    return True


  def err(self, msg):
    print msg


if __name__ == "__main__":
  mi = MemInfo()
  print mi.mem_info

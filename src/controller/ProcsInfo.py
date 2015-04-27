import subprocess
import re

class ProcsInfo:
  ps_re = re.compile("^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+"+
                     "(\S+)\s+(\S+)\s+(\S+).*$")
  last_ps = None
  this_ps = None
  # lock


  def __init__(self):
    self.update()


  def check_device(self):
    return True


  def update(self):
    if not self.check_device():
      self.err("ERR : device does not exist.")
      return False
    p = subprocess.Popen(["adb", "shell", "ps"], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if err is None:
      new_ps = []
      for line in out.split("\r\n"):
        match = ProcsInfo.ps_re.match(line)
        if not match is None:
          user, pid, ppid, vsize, rss, wchan, pc, state, name = match.groups()
          new_ps.append([user, pid, ppid, name])
      # acquire lock
      ProcsInfo.last_ps = ProcsInfo.this_ps
      ProcsInfo.this_ps = new_ps
      # release lock
    else:
      self.err(err)
      return False

    return True


  def diff(self):
    if self.update():
      pass
      # do something else


  def err(self, msg):
    print msg


if __name__ == "__main__":
  pi = ProcsInfo()
  print pi.this_ps

import os
import re
import subprocess


"""
def is_application_start(message, cmp=""):
  names = ["android.intent.action.MAIN",
           "android.intent.category.LAUNCHER",
           cmp]
  return all([name in message for name in names])

re.compile("^Process (\S+) \(pid (\d+)\).*$"),# "died"
re.compile("^No longer want (\S+) \(pid (\d+)\).*"),#"no_want"
re.compile("^Kill (\S+) \(pid (\d+)\).*$"),#"kill"
re.compile("^Killing proc (\d+):(.*)/.*"),#"killing_proc"
re.compile("^Killing (\d+):(.*)/.*task"),#"killing"
re.compile("^Start proc (\S+) .* pid=(\d*) .*")#"start_proc"
"""

class Meow:
  log_re = re.compile("^(\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3})" + \
                      " ([A-Z])/([^\(]+)\(([^\)]+)\): (.*)$")

  def __init__(self):
    self.log_clear_sig = "Trevillie"
    self.log_clear_note = {
      "V" : True,
      "D" : True,
      "I" : True,
      "W" : True,
      "E" : True
    }
    print "Logcat Meowing..."


  def refresh(self):
    self.__init__()
  

  def take_note(self):
    # clear & time
    pass


  def clear(self):
    p = subprocess.Popen(["adb", "logcat", "-c"], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if err is None and out == "":
      print "Logcat Cleared!"
      return True
    else:
      print "Logcat Clear Failed!"
      return False


  def run(self):
    input = os.popen("adb logcat -v time")
    while True:
      try:
        line = input.readline()
      except KeyboardInterrupt:
        break

      match = Meow.log_re.match(line)

      if not match is None:
        date, time, tagtype, tag, owner, message = match.groups()
        
        # check if logs are cleaned
        if tag == self.log_clear_sig:
          self.log_clear_note[tagtype] = False
          print self.log_clear_note
        
        """
        m = regex["died"].match(message)
        if not m is None:
          proc_name, pid = m.groups()
          if procs.has_key(pid):
            procs.pop(pid)
          else:
            print "---", pid, "started not captured"
          print proc_name, pid, "died"
        """

      if len(line) == 0: break


if __name__ == "__main__":
  kitty = Meow()
  kitty.run()

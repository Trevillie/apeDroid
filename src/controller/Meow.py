import os
import re


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
                      " ([A-Z])/([^\(]+)\(([^\)]+)\): (.*)$"),

  def __init__(self):
    print "Logcat Meowing..."
    
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

# written by trevillie
import os
import re
from time import sleep
import subprocess
import threading


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
    self.started_sig = "apeDroid"
    self.trigger_sig = ""

    self.on = False
    
    self.trigger_time = ""
    self.started_time = ""
    self.log_clear_note = {
      "V" : True,
      "D" : True,
      "I" : True,
      "W" : True,
      "E" : True
    }
    print "Logcat Meowing..."


  def turn_on(self, main_activity):
    """
    Pass main_activity as a string.
    """
    self.trigger_sig = main_activity
    self.on = True
    print "Kitty turned on with", main_activity


  def turn_off(self):
    self.on = False
    print "Kitty turned off with", self.trigger_sig
    self.trigger_sig = ""
    return self.take_note()


  def refresh(self):
    self.__init__()
  

  def take_note(self):
    # clear & time
    print "------------------------------------"
    print "trigger time :", self.trigger_time
    print "started time :", self.started_time
    print "logcat clear record :", self.log_clear_note
    print "------------------------------------"
    return self.trigger_time, self.started_time, self.log_clear_note


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


  def thread_up(self):
    t = threading.Thread(target=self.run)
    t.start()


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
        
        if self.on:
          # check if logs are cleaned
          if self.log_clear_sig in tag:
            self.log_clear_note[tagtype] = False

          # take down first trigger time
          if self.trigger_sig != "":
            if "START u" in message and self.trigger_sig in message:
              if self.trigger_time == "":
                self.trigger_time = time

          # take down first started time
          if self.started_sig in tag:
            if self.started_time == "":
              self.started_time = time

      if len(line) == 0:
        print "Logcat Terminates..."
        break


if __name__ == "__main__":
  kitty = Meow()
  kitty.thread_up()
  sleep(3)
  kitty.turn_on("news")
  sleep(10)
  kitty.turn_off()

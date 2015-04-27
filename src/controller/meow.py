# -*- coding:utf8 -*-
#!/usr/bin/python

import os, re

regex = {
  "log"          : re.compile("^(\d{2}-\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3})" + \
                              " ([A-Z])/([^\(]+)\(([^\)]+)\): (.*)$"),
  "time"         : re.compile(""),
  "pid"          : re.compile(" pid=(/d*) "),
  "apk_name"     : re.compile(" cmp=(.*)/"),
}

tags = {
  "basic"         : "apeDroid",
  "load_complete" : "apeDroid_application_load_complete"
}

input = os.popen("adb logcat -v time")


def is_application_start(message, cmp=""):
  names = ["android.intent.action.MAIN",
           "android.intent.category.LAUNCHER",
           cmp]
  return all([name in message for name in names])





class Procs():
  procs = {}
  regex = {
    re.compile("^Process (\S+) \(pid (\d+)\).*$"),# "died"
    re.compile("^No longer want (\S+) \(pid (\d+)\).*"),#"no_want"
    re.compile("^Kill (\S+) \(pid (\d+)\).*$"),#"kill"
    re.compile("^Killing proc (\d+):(.*)/.*"),#"killing_proc"
    re.compile("^Killing (\d+):(.*)/.*task"),#"killing"
    re.compile("^Start proc (\S+) .* pid=(\d*) .*")#"start_proc"
  }

  def __init__(self):
    pass

  def update(self, log):
    matches = [reg.match(log.message) for reg in regex]


  def add_to_procs(self):
    pass

  def remove_from_procs(self):
    pass
    



    

while True:
  try:
    line = input.readline()
  except KeyboardInterrupt:
    break

  match = regex["log"].match(line)

  if not match is None:
    date, time, tagtype, tag, owner, message = match.groups()

    m = regex["died"].match(message)
    if not m is None:
      proc_name, pid = m.groups()
      if procs.has_key(pid):
        procs.pop(pid)
      else:
        print "---", pid, "started not captured"
      print proc_name, pid, "died"

    m = regex["no_want"].match(message)
    if not m is None:
      proc_name, pid = m.groups()
      if procs.has_key(pid):
        procs.pop(pid)
      else:
        print "---", pid, "started not captured"
      print proc_name, pid, "is not wanted"

    m = regex["kill"].match(message)
    if not m is None:
      proc_name, pid = m.groups()
      if procs.has_key(pid):
        procs.pop(pid)
      else:
        print "---", pid, "started not captured"
      print proc_name, pid, "killed"

    m = regex["killing"].match(message)
    if not m is None:
      pid, proc_name = m.groups()
      if procs.has_key(pid):
        procs.pop(pid)
      else:
        print "---", pid, "started not captured"
      print proc_name, pid, "killed"

    m = regex["killing_proc"].match(message)
    if not m is None:
      pid, proc_name = m.groups()
      if procs.has_key(pid):
        procs.pop(pid)
      else:
        print "---", pid, "started not captured"
      print proc_name, pid, "killed"

    m = regex["start_proc"].match(message)
    if not m is None:
      proc_name, pid = m.groups()
      procs[pid] = proc_name
      print proc_name, pid, "started"
      print 
      for k in procs:
        print k, procs[k]

    """
    if "com.ss.android.article.news" in message:
      print time, message
      if "START u0" in message:
        print "++++++"
        print "user trigger"

    if "apeDroid" in tag:
      print "---- " + owner
      print time, message
    """

  if len(line) == 0: break

import subprocess
import re
from time import sleep

class Procs:
  ps_re = re.compile("^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+"+
                     "(\S+)\s+(\S+)\s+(\S+).*$")
  init_ps = None
  last_ps = None
  this_ps = None
  # lock


  def __init__(self):
    ps = self.get_new_ps()
    if ps != []:
      self.init_ps = ps
      self.last_ps = ps
      self.this_ps = ps
      print "Initialization Succeeded."
    else:
      # raise Error
      print "Initialization Failed."
      pass


  def _tup2dict(self, tup):
    # for tuple with format of (user, pid, ppid, name)
    return {
      "user" : tup[0],
      "pid"  : tup[1],
      "ppid" : tup[2],
      "name" : tup[3],
    }


  def update(self):
    new_ps = self.get_new_ps()
    if new_ps != []:
      # acquire lock
      self.last_ps = self.this_ps
      self.this_ps = new_ps
      # release lock
      print "Update Succeeded."
      return True
    else:
      print "New ps is blank. Update failed."
      return False


  def get_new_ps(self):
    p = subprocess.Popen(["adb", "shell", "ps"], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if err is None:
      new_ps = []
      for line in out.split("\r\n"):
        match = Procs.ps_re.match(line)
        if not match is None:
          user, pid, ppid, vsize, rss, wchan, pc, state, name = match.groups()
          new_ps.append((user, pid, ppid, name))
      print "Getting new ps."
      return new_ps
    else:
      print "Get new ps error. New ps blank."
      return []


  def diff(self, new_snapshot, old_snapshot):
    old_set = set(old_snapshot)
    new_set = set(new_snapshot)
    new_procs = new_set - old_set
    die_procs = old_set - new_set
    return {
      "new" : list(new_procs),
      "die" : list(die_procs),
    }


  def compare_ori(self):
    self.update()
    return self.diff(self.this_ps, self.init_ps)


  def compare_last(self):
    pass


  def get_user(self, package_name):
    """
    user = p.get_user("com.ss.android.article.news")
    if user:
      print user
    """
    procs = self.get_new_ps()
    ps_in_dict = [self._tup2dict(proc) for proc in procs]
    user = set([ps["user"] for ps in ps_in_dict if package_name in ps["name"]])
    if len(user)==1:
      return user.pop()
    else:
      return None


  def get_user_procs(self, user):
    procs = self.get_new_ps()
    ps_in_dict = [self._tup2dict(proc) for proc in procs]
    pids = [ps["pid"] for ps in ps_in_dict if user == ps["user"]]
    names = [ps["name"] for ps in ps_in_dict if user == ps["user"]]
    return pids, names


  def kill_process(self, pid):
    p = subprocess.Popen(["adb", "shell", "kill", str(pid)], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if err is None:
      if out == "":
        print "Killed process, pid(", pid, ")"
        return True
      else:
        print out.strip()
    else:
      print "kill_process cmd execution error."
    return False


  def kill_user(self, user):
    count = 3
    for i in range(count):
      pids, _ = self.get_user_procs(user)
      if len(pids) > 0:
        for pid in pids:
          self.kill_process(pid)
      else:
        print "All process of", user, "is killed."
        return True
    print "Seems impossible to kill", user, "this way... Failed."
    return False


  def is_alive(self, name):
    procs = self.get_new_ps()
    ps_in_dict = [self._tup2dict(proc) for proc in procs]
    names = [ps["name"] for ps in ps_in_dict]
    return (name in names)


if __name__ == "__main__":
  p = Procs()
  # sleep(10)
  # print p.compare_ori()
  # p.kill_process(1399)
  p.kill_user("u0_a52")

# written by trevillie
import subprocess
import re

class MemInfo:
  """
  Stateless Memory Information Utility Class.
  ! May : Instance Method -> Static Method
  """
  mem_re = re.compile("^(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+).*$")

  def __init__(self):
    print "MemInfo Service Started..."


  def get_mem_info(self):
    p = subprocess.Popen(["adb", "shell", "procrank"], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if err is None:
      new_mem = []
      for line in out.split("\r\n"):
        match = MemInfo.mem_re.match(line.strip())
        if not match is None:
          pid, vss, rss, pss, uss, cmd = match.groups()
          new_mem.append({
            "pid" : pid,
            "pss" : pss,
            "uss" : uss,
            "cmd" : cmd,
          })
      return new_mem
    else:
      print "Error doing procrank..."
      return []

  
  def get_pids_mem_procrank(self, mem_infos, pids, verbose=True):
    pss = [mi["pss"] for mi in mem_infos if mi["pid"] in pids]
    uss = [mi["uss"] for mi in mem_infos if mi["pid"] in pids]
    if verbose:
      print "memory information for", pids
      print "pss :", pss
      print "uss :", uss
    pss_sum = sum([int(m[:-1]) for m in pss])
    uss_sum = sum([int(m[:-1]) for m in uss])
    if verbose:
      print "pss all together :", pss_sum, "K"
      print "uss all together :", uss_sum, "K"
    return pss_sum, uss_sum


  def get_pid_smaps_pss(self, pid, verbose=True):
    p = subprocess.Popen(["adb", "shell", "cat", "/proc/"+str(pid)+"/smaps"],
                         stdout=subprocess.PIPE)
    out, err = p.communicate()
    p.wait()

    lens = []
    for line in out.split("\r\n"):
      line = line.strip()
      if line.startswith("Pss:"):
        amount = int(line.split(" ")[-2])
        lens.append(amount)

    return sum(lens)


  def get_pids_mem(self, pids, verbose=True):
    pss_s = []
    if verbose:
      print "-------  MEMORY  -------"
      print "Calculating memory comsumption from smaps for", pids
    for pid in pids:
      pss = self.get_pid_smaps_pss(pid, verbose=verbose)
      pss_s.append(pss)
      if verbose:
        print pid, ":", pss, "KB"
    pss_sum = sum(pss_s)
    if verbose:
      print
      print "TOTAL CONSUMPTION (IN PSS) :", pss_sum, "KB"
      print

    return pss_sum


if __name__ == "__main__":
  mi = MemInfo()
  print mi.get_mem_info()

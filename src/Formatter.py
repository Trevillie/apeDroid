# written by trevillie

class Formatter:
  """
  Format result for processing.py
  To add method for index formatting, first add index in update_index,
                                      then add method format_xxx(self, brand).
  """
  def __init__(self):
    self.update_index([])


  def update_sample(self, sample_info):
    self.sample_info = sample_info
    self.brands = self.sample_info.keys()
    self.brands.remove("original")
    self.brands.insert(0, "original")
  

  def update_index(self, indexes):
    if indexes == []:
      self.indexes = ["size",
                      "memory",
                      "proc_num",
                      "time",
                      "permission_num",
                      "permission_content",
                      "signature",
                      "ratio",
                      "flag",
                      "cls_num",
                      "log_clear",
                      "so",
                      "tamper",
                      "network",
                      "debug"
                     ]
    else:
      self.indexes = indexes


  def _percentage(self, old_data, new_data):
    delta = new_data - old_data
    if delta >= 0:
      sign = "+"
    else:
      sign = "-"
      delta = -delta
    percentage = str(round(float(100*delta)/old_data, 2)) + "%"
    return " ".join([sign, percentage])


  def _num(self, s):
    try:
      return int(s)
    except ValueError:
      return float(s)


  def format_size(self, brand):
    ori_size = self.sample_info["original"]["size"]/1024
    if brand == "original":
      return str(ori_size)+" KB"
    else:
      size = self.sample_info[brand]["size"]/1024
      return str(size) + " KB / " + self._percentage(ori_size, size)


  def format_memory(self, brand):
    ori_mem = self.sample_info["original"]["memory"]
    if brand == "original":
      return str(round(ori_mem, 1))+" KB"
    else:
      mem = self.sample_info[brand]["memory"]
      return str(round(mem, 1)) + " KB / " + self._percentage(ori_mem, mem)


  def format_proc_num(self, brand):
    ori_num = self.sample_info["original"]["proc_num"]
    if brand == "original":
      return str(ori_num)
    else:
      num = self.sample_info[brand]["proc_num"]
      return str(num) + " / " + self._percentage(ori_num, num)


  def format_time(self, brand):
    ori_time = self._num(self.sample_info["original"]["startup_cost"])
    if brand == "original":
      return str(round(ori_time, 3))+" s"
    else:
      t = self._num(self.sample_info[brand]["startup_cost"])
      return str(round(t, 3)) + " s / " + self._percentage(ori_time, t)


  def format_permission_num(self, brand):
    ori_num = len(self.sample_info["original"]["permission"])
    if brand == "original":
      return str(ori_num)
    else:
      num = len(self.sample_info[brand]["permission"])
      if ori_num == num:
        return "No More Premission Required"
      return str(num) + " / " + self._percentage(ori_num, num)


  def format_permission_content(self, brand):
    if brand == "original":
      return "-"
    else:
      ori_perms = set(self.sample_info["original"]["permission"])
      perms = set(self.sample_info[brand]["permission"])
      ret = " / ".join(list(perms - ori_perms))
      if ret == "":
        ret = "No More Premission Required"
      return ret


  def format_signature(self, brand):
    if brand == "original":
      return "-"
    return self.sample_info[brand]["signature"]


  def format_ratio(self, brand):
    return str(self.sample_info[brand]["dynamic_loading"]["ratio"])


  def format_flag(self, brand):
    return self.sample_info[brand]["dynamic_loading"]["flag"]


  def format_cls_num(self, brand):
    ori_num = self._num(self.sample_info["original"]
                        ["dynamic_loading"]["cls_num"])
    if brand == "original":
      return str(ori_num)
    else:
      num = self._num(self.sample_info[brand]["dynamic_loading"]["cls_num"])
      return str(num) + " / " + self._percentage(ori_num, num)


  def format_log_clear(self, brand):
    return self.sample_info[brand]["log_clear"]


  def format_so(self, brand):
    if brand == "original":
      return "-"
    if self.sample_info[brand]["so"]:
      return "No Shared Object File Protection"
    return "Shared Object File Protected"


  def format_tamper(self, brand):
    return self.sample_info[brand]["tamper"]


  def format_network(self, brand):
    ori_ips = [conn["ip"] for conn in self.sample_info["original"]["network"]]
    if brand == "original":
      return " / ".join(ori_ips)
    else:
      ips = [conn["ip"] for conn in self.sample_info[brand]["network"]]
      new_ips = list(set(ips) - set(ori_ips))
      nw = {}
      for conn in self.sample_info[brand]["network"]:
        nw[conn["ip"]] = " ".join([conn["ip"], conn["org"], conn["region"]])
      
      new_ips_info = [nw[ip] for ip in new_ips]

      return "+"+str(len(new_ips))+" " + " / ".join(new_ips_info)


  def format_debug(self, brand):
    debug_info = self.sample_info[brand]["debug"]
    if not debug_info["tested"]:
      return "Anti-Debugging Not Tested Due To App Startup Failure"
    if debug_info["can_trace"]:
      if debug_info[True]["trace_succ"]:
        return "No Anti-Debugging Protection"
      else:
        return "No Former Tracer, Suisides When Traced"
    child = lambda x: "(Child)" if x else "(Not Child)"
    line = ["The App Is Self-Traced By",
            debug_info[False]["tracer_pid"],
            debug_info[False]["tracer_name"],
            child(debug_info[False]["tracer_child"])]
    if debug_info[False]["kill_tracer"]:
      if debug_info[False]["trace_succ"]:
        line.append("Can Kill Tracer And Trace")
      else:
        line.append("Can Kill Tracer, Suisides When We Trace It")
    else:
      line.append("Suisides When Tracer Is Killed")
    return " ".join(line)


  def format_index(self, index):
    """
    All returned content is plain string without comma.
    Return a row of index value.
    """
    collector = []
    for brand in self.brands:
      try:
        method_name = "_".join(["format", index])
        method = getattr(self, method_name)
        if not method:
          raise Exception("Method %s not implemented" % method_name)
        collector.append(method(brand))
      except KeyError:
        collector.append("NULL")
    return collector


  def write_formatted_info(self, handle):
    rows = []
    for index in self.indexes:
      rows.append(self.format_index(index))

    lines = []
    add_line = lambda x: lines.append(x+"\r\n")
    for i in range(len(self.indexes)):
      print self.indexes[i]
      add_line(self.indexes[i])
      for j in range(len(self.brands)):
        l = " : ".join([self.brands[j].ljust(10), rows[i][j]])
        print l
        add_line(l)
      print
      add_line("")

    for line in lines:
      handle.write(line)

    return self.indexes, rows


if __name__ == "__main__":
  from sample import sample
  f = Formatter(sample["com.tencent.news"])
  with open("./metrics", "w") as handle:
    f.write_formatted_info(handle)
  #print f._percentage(1.213, 9.128736123)

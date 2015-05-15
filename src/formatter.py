# written by trevillie

class Formatter:
  """
  Format result for processing.py
  To add method for index formatting, first add index in update_index,
                                      then add method format_xxx(self, brand).
  """
  def __init__(self, sample_info):
    self.update_sample(sample_info)
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
                      "time",
                      "permission_num",
                      "permission_content",
                      "signature",
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
    percentage = str(round(float(100*delta/old_data), 2)) + "%"
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
      return str(ori_mem)+" KB"
    else:
      mem = self.sample_info[brand]["memory"]
      return str(mem) + " KB / " + self._percentage(ori_mem, mem)


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


  def get_formatted_info(self):
    rows = []
    for index in self.indexes:
      rows.append(self.format_index(index))

    print "---------------"
    for i in range(len(self.indexes)):
      print self.indexes[i]
      for j in range(len(self.brands)):
        print " : ".join([self.brands[j], rows[i][j]])
      print

    return self.indexes, rows


if __name__ == "__main__":
  from sample import sample
  print sample["com.tencent.news"]["baidu"].keys()
  f = Formatter(sample["com.tencent.news"])
  f.get_formatted_info()
  #print f._percentage(1.213, 9.128736123)

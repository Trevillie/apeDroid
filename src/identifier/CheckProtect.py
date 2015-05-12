# -*- coding:utf8 -*-

from __future__ import division
from shutil import rmtree
import os
import sys
from UnzipAPK import UnzipAPK


class CheckProtect:

  def __init__(self, apk_path, unzip_path):
    self.apk_path = apk_path
    self.unzip_path = unzip_path
    self.protectflag = "Unprocessed"
    self.protectflag_dict = {
      "libsecexe.so": "Bangcle",
      "libAPKProtect.so": "APKProtect",                 
      "libprotectClass.so": "360",
      "libNSaferOnly.so": "PayEgis",
      "libnqshield.so": "Netqin",
      "libshell.so": "Tencent",
      "ijiami.dat": "ijiami",
      "libddog.so": "Nagain",
      "libmobisec.so": "Ali",
      "libbaiduprotect.so": "Baidu",
    }
    self.standard_ratio = 0.6
    self.unzip_apk_obj = UnzipAPK(self.apk_path, self.unzip_path)
    self.package_name = self.unzip_apk_obj.get_package_name()
    self.check_protectflag()


  def check_protectflag(self):
    self.protectflag = ""
    activities = self.unzip_apk_obj.get_activities()
    class_names = self.unzip_apk_obj.get_class_name()
    all_file_name, all_dir_name = self.unzip_apk_obj.get_all_name()
    hints = self.protectflag_dict.keys()

    self.protectflag += " ".join([self.protectflag_dict[hint] for
                                  hint in hints if hint in all_file_name])
    if "com.qihoo.util.StubApplication" in class_names:
      if self.protectflag == "":
        self.protectflag = "Qihoo"
      else:
        self.protectflag = self.protectflag + " " + "Qihoo"

    if "key.dat" in all_file_name and "apkprotect.com" in all_dir_name:
      if "APKProtect" not in self.protectflag:
        self.protectflag = " ".join([self.protectflag, "APKProtect"])

    class_set = set(class_names)
    activity_set = set(activities)
    exclude_set = activity_set - class_set
    print exclude_set

    class_num = len(class_set)
    activity_num = len(activity_set)
    exclude_num = len(exclude_set)
    if activity_num != 0:
      exclude_ratio = round(exclude_num/activity_num, 3)
    else:
      exclude_ratio = 1
    self.ratio = exclude_ratio
    self.class_num = class_num
    self.exclude_num = exclude_num
    self.activity_num = activity_num

    print "--------------------------------------------------------"
    print "class number    :", class_num
    print "activity number :", activity_num
    print "out-class activity number : ", exclude_num
    print "exclude ratio   :", exclude_ratio
    print "standard ratio  :", self.standard_ratio
    
    """
    for activity in exclude_set:
      print activity

    include_set_num = len([1 for act in activities if any([1 for cls in class_names if cls in act])])
    include_ratio = round(include_set_num/activity_num, 3)
    print "THE ratio :", exclude_ratio
    print "OTHER ratio :", 1-include_ratio
    """

    if self.protectflag == "":
      if exclude_ratio > self.standard_ratio:
        self.protectflag = "Suspicious-Protection"
      else:
        self.protectflag = "No-Protection-Detected"


  def get_protector_name(self):
    return self.protectflag


  def get_record(self):
    return [self.unzip_apk_obj.apk_name,
            self.package_name,
            str(self.class_num),
            str(self.activity_num),
            str(self.exclude_num),
            str(self.standard_ratio),
            str(self.ratio),
            self.protectflag]


if __name__ == "__main__":
  ori_apk_path = "../preprocess/ori_apk"
  unpack_dir = "./unpack"
  record_list = "./record.list"
  err_log = "./errlog"
  if len(sys.argv) == 2:
    if os.path.exists(sys.argv[1]):
      ori_apk_path = sys.argv[1]
      record_list = os.path.join("./result",
                                 os.path.basename(sys.argv[1])+".result")
      unpack_dir  = os.path.basename(sys.argv[1])+"_unpack"

  names = os.listdir(ori_apk_path)
  print names
  apks = [os.path.join(ori_apk_path, name) for name in names]
  with open(record_list, "a") as handle:
    for apk in apks:
      try:
        if not os.path.exists(unpack_dir):
          os.makedirs(unpack_dir)
        checker = CheckProtect(apk, unpack_dir)
        print checker.get_protector_name()
        print
        handle.write(", ".join(checker.get_record())+"\r\n")
        rmtree(unpack_dir, ignore_errors=True)
      except TypeError:
        with open(err_log, "a") as err_handle:
          err_handle.write(", ".join([apk, record_list])+"\r\n")

# -*- coding:utf8 -*-

from __future__ import division
from UnzipAPK import UnzipAPK

class CheckProtect():

  def __init__(self, apk_path, unzip_path):
    self.apk_path = apk_path
    self.unzip_path = unzip_path
    self.protectflag = u"尚未检测"
    self.protectflag_dict = {
      "libsecexe.so": u"梆梆加固",
      "libAPKProtect.so": u"APKProtect加固",                 
      "libprotectClass.so": u"360加固",
      "libNSaferOnly.so": u"通付盾加固",
      "libnqshield.so": u"网秦加固",
      "libshell.so": u"腾讯加固",
      "ijiami.dat": u"爱加密加固",
      "libddog.so": u"娜迦加固",
      "libmobisec.so": u"阿里加固",
      "libbaiduprotect.so": u"百度加固"
    }
    self.unzip_apk_obj = UnzipAPK(self.apk_path, self.unzip_path)
    self.check_protectflag()


  def check_protectflag(self):
    self.protectflag = u""
    activities = self.unzip_apk_obj.get_activities()
    class_names = self.unzip_apk_obj.get_class_name()
    all_file_name, all_dir_name = self.unzip_apk_obj.get_all_name()
    hints = self.protectflag_dict.keys()

    self.protectflag += " ".join([self.protectflag_dict[hint] for
                                  hint in hints if hint in all_file_name])

    if "key.dat" in all_file_name and "apkprotect.com" in all_dir_name:
      if u"APKProtect加固" not in self.protectflag:
        self.protectflag = " ".join([self.protectflag, u"APKProtect加固"])

    class_set = set(class_names)
    activity_set = set(activities)
    exclude_set = activity_set - class_set

    class_num = len(class_set)
    activity_num = len(activity_set)
    exclude_num = len(exclude_set)
    exclude_ratio = round(exclude_num/activity_num, 3)

    print "--------------------------------------------------------"
    print "class number    : " + str(class_num)
    print "activity number : " + str(activity_num)
    print "out-class activity number : " + str(exclude_num)
    print "THE ratio : " + str(exclude_ratio)
    
    for activity in exclude_set:
      pass
      print activity

    include_set_num = len([1 for act in activities if any([1 for cls in class_names if cls in act])])
    include_ratio = round(include_set_num/activity_num, 3)
    print "THE ratio : " + str(exclude_ratio)
    print "OTHER ratio : " + str(1-include_ratio)

    if self.protectflag == "":
      if exclude_ratio > 0.5:
        self.protectflag = u"疑似未知加密"
      else:
        self.protectflag = u"该APK未加密"
    print "--------------------------------------------------------"


  def get_protector_name(self):
    return self.protectflag


if __name__ == "__main__":
  print CheckProtect('../../apps/news.list/001.apk',
                     "../../temp/unzipdir/news_reading/").get_protector_name()

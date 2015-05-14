#!/usr/bin/python
# -*- coding:utf8 -*-
# written by trevillie

from __future__ import print_function
import os
import CheckProtect


def main():
  apk_base_path = "../../apps/新闻阅读.list"
  report_base_path = "../../report"
  unzip_path = os.path.join("../../temp/unzipdir", "news_reading")
  if not os.path.exists(unzip_path):
    os.mkdir(unzip_path)
  report_name = "news_report.list"
  names = os.listdir(apk_base_path)

  with open(os.path.join(report_base_path, report_name), "w") as f:
    for name in names:
      apk_path = os.path.join(apk_base_path, name)
      check_obj = CheckProtect.CheckProtect(apk_path, unzip_path)
      protector_name = check_obj.get_protector_name().encode("utf-8")
      package_name = check_obj.unzip_apk_obj.get_package_name()
      print("-----------------------------------------------")
      print(package_name + "^" + protector_name + "^" + name)
      print("-----------------------------------------------")
      print(package_name + "^" + protector_name + "^" + name, file=f)


if __name__ == "__main__":
  main()

"""
@p1 : "multiply" or "tamper"
"""

import os
import subprocess
from shutil import copyfile, rmtree
from controller.APK import APK
from preprocess import multiplier
from preprocess.injector import inject


def rel(relpath):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)),relpath)

place_dir = rel("./preprocess/factory/multiplier/")

def get_apk_list(ori_apk_path=rel("./preprocess/ori_apk/")):
  try:
    names = os.listdir(ori_apk_path)
    return [os.path.join(ori_apk_path, name) for name in names]
  except OSError:
    print "! os.list on %s fails" % ori_apk_path
    return []


def multiply():
  apk_paths = get_apk_list()
  for apk_path in apk_paths:
    apk = APK(apk_path)
    # something can be done here
    package_name = apk.package_name
    main_activity = apk.main_activity     # fully-qualified name here
    print package_name
    print main_activity

    vl = multiplier.get_vendor_list()
    dest_path = multiplier.init_file_structure(package_name, vl)

    rmtree(place_dir)
    multiplier.mkdir(place_dir)
    copyfile(apk_path, os.path.join(place_dir, "apk.apk"))

    os.chdir(rel("./preprocess/factory/"))
    subprocess.call(["./multiply_1.sh"])

    if inject.place_injector():
      main_activity_path = inject.name2path(main_activity)
      inject.inject_main_activity(main_activity_path)
    else:
      raise OSError

    subprocess.call(["./multiply_2.sh"])
    os.chdir(os.path.dirname(rel(__file__)))

    for mapk in get_apk_list(place_dir):
      name = os.path.basename(mapk)
      copyfile(mapk, os.path.join(dest_path, name))

    print "----------------------------------------"
    print package_name, "multiplication step done!"
    print "----------------------------------------"



if __name__ == "__main__":
  # deal with arg
  multiply()




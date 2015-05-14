# written by trevillie
import os
import subprocess
import xml.etree.ElementTree as ET
from injector import inject

PERMISSIONS = [
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.CALL_PRIVILEGED",
    "android.permission.INTERNET",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.CHANGE_WIFI_STATE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
    "com.android.launcher.permission.INSTALL_SHORTCUT",
    "android.permission.READ_PHONE_STATE",
    "android.permission.INSTALL_PACKAGES",
    "android.permission.READ_SMS",
    "android.permission.WRITE_SMS",
    "android.permission.RESTART_PACKAGES",
    "android.permission.CALL_PHONE",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.ACCESS_FINE_LOCATION",
]

def rel(relpath):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)),relpath)


def tamper_res(apk_dir):
  """
  Here suppose apk_dirs are absolute paths.
  """
  res_dir = os.path.join(apk_dir, "res/")

  p = subprocess.Popen(["grep", "-lir", "<string name", res_dir],
                       stdout=subprocess.PIPE)
  p.wait()
  out, err = p.communicate()

  stringxml_paths = []
  if err is None:
    for line in out.split("\n"):
      strings_path = line.strip()
      if strings_path != "":
        if os.path.basename(strings_path) == "strings.xml":
          stringxml_paths.append(strings_path)
  else:
    raise OSError

  for stringxml_path in stringxml_paths:
    tree = ET.parse(stringxml_path)
    root = tree.getroot()
    for string in root.iter("string"):
      if not string.text is None:
        new_string = string.text + "-_-"
        string.text = new_string
    tree.write(stringxml_path)
    print rel(stringxml_path), "tamper complete..."


def tamper_man(apk_dir):
  manifest_path = os.path.join(apk_dir, "AndroidManifest.xml")
  if not os.path.exists(manifest_path):
    print "Manifest is missing..."
    raise OSError

  used_permissions = []
  attrib_name = "{http://schemas.android.com/apk/res/android}name"

  ET.register_namespace("android", "http://schemas.android.com/apk/res/android")
  tree = ET.parse(manifest_path)
  root = tree.getroot()
  for permission in root.iter("uses-permission"):
    used_permissions.append(permission.attrib[attrib_name])
  unused_permissions = set(PERMISSIONS) - set(used_permissions)

  if len(unused_permissions) == 0:
    print "I am almost certain this is a malware..."
  else:
    permission_to_add = unused_permissions.pop()
    print "Permission to add :", permission_to_add 
    root.append(ET.Element("uses-permission",
                           attrib={attrib_name:permission_to_add}))
  tree.write(manifest_path)
  print rel(manifest_path), "tamper complete..."


def tamper_sma(apk_dir, main_activity):
  smali_path = os.path.join(apk_dir, "smali")
  if inject.place_injector(smali_path):
    main_activity_path = inject.name2path(main_activity, smali_path=smali_path)
    inject.inject_main_activity(main_activity_path)
    print "Injection Complete..."
  else:
    raise OSError


if __name__ == "__main__":
  #tamper_man("./002/")
  tamper_sma("./002/", "com.tencent.news.activity.SplashActivity")

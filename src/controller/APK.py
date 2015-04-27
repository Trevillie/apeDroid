from __future__ import division

import subprocess
import os
from zipfile import BadZipfile
from xml.dom import minidom
from time import sleep

from androguard import apk
from androguard import dvm
from androguard import analysis
#from exceptions import ApeDroidApkError 


class ApeDroidApkError(Exception):
  def __init__(self, msg):
    print msg


class APKRuntime:

  def __init__(self, apk_obj):
    self.apk = apk_obj
    self.installed = False


  def install(self):
    if self.installed:
      return True

    p = subprocess.Popen(["adb", "install", self.apk.path],
                         stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if("Failure" in out):
      raise ApeDroidApkError(self.apk.package_name + "install failed. " + out)
      return False
    else:
      self.installed = True
      return True


  def uninstall(self):
    if not self.installed:
      return True
    
    p = subprocess.Popen(["adb", "uninstall", self.apk.package_name],
                         stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()
    
    if not err is None:
      return False
    else:
      if "Failure" in out:
        return False
      else:
        self.installed = False
        return True
      

  def start(self):
    if not "." in self.apk.main_activity:
      self.apk.main_activity = "." + self.apk.main_activity
    if self.apk.main_activity.startswith("."):
      to_start = self.apk.package_name + self.apk.main_activity
    else:
      to_start = self.apk.main_activity
    to_start = self.apk.package_name + "/" + to_start
    print "Activity to start : ", to_start

    p = subprocess.Popen(["adb", "shell", "am", "start", "-n", to_start],
                         stdout=subprocess.PIPE)
    out, err = p.communicate()
    p.wait()

    if not err is None:
      return False
    if "not started" in out:
      return False
    return True


class APK:
  
  def __init__(self, apk_path):
    self.path = apk_path
    self.size = os.path.getsize(self.path)

    self.validity           = False
    self.package_name       = None
    self.permission_details = None
    self.permissions        = None
    self.main_activity      = None
    self.process            = None

    self.static_init()


  def static_init(self):
    try:
      a = apk.APK(self.path)
      if a.is_valid_APK():
        self.validity           = True
        self.package_name       = a.get_package()
        self.permission_details = a.get_details_permissions_new()
        self.permissions        = [perm["name"] for perm in self.permission_details]
        self.main_activity      = a.get_main_activity()
        self.process            = self.get_process(a)
        
        #vm = dvm.DalvikVMFormat(a.get_dex())
        #vmx = analysis.uVMAnalysis(vm)

        #static_calls = {}
        #static_calls["all_methods"] =self.get_methods(vmx)
        #static_calls["is_native_code"] = analysis.is_native_code(vmx)
        #static_calls["is_dynamic_code"] = analysis.is_dyn_code(vmx)
        #static_calls["is_reflection_code"]= analysis.is_reflection_code(vmx)

        #static_calls["dynamic_method_calls"]= analysis.get_show_DynCode(vmx)
        #static_calls["reflection_method_calls"]= analysis.get_show_ReflectionCode(vmx)
        #static_calls["permissions_method_calls"]= analysis.get_show_Permissions(vmx)
        #static_calls["crypto_method_calls"]= analysis.get_show_CryptoCode(vmx)
        #static_calls["native_method_calls"]= analysis.get_show_NativeMethods(vmx)
        #print static_calls

      else:
        raise ApeDroidApkError("APK file not valid")
    except (IOError, OSError,BadZipfile) as e:
      raise ApeDroidApkError("Error open file %s" % e)


  def get_process(self, a):
    manifest_axml = a.get_android_manifest_axml()
    manifest_doc = minidom.parseString(manifest_axml.get_buff())
    
    tags = ["activity", "service", "provider", "receiver"]
    items = []
    for tag in tags:
      items.extend(manifest_doc.getElementsByTagName(tag))

    mani_procs = list(set([str(item.getAttribute("android:process"))
                           for item in items]))
    procs = []
    for proc in mani_procs:
      if proc.startswith(":") or proc == "":
        procs.append(self.package_name + proc)
      else:
        procs.append(procs)

    return procs


if __name__ == "__main__":
  processor = APK("./done.apk")
  print processor.size
  apk_runtime = APKRuntime(processor)
  apk_runtime.start()
  # apk_runtime.install()
  # sleep(10)
  # apk_runtime.uninstall()

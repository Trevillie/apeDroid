from __future__ import division

import subprocess
import os
from androguard import apk
from androguard import dvm
from androguard import analysis
#from exceptions import ApeDroidApkError 
from zipfile import BadZipfile

from xml.dom import minidom


class ApeDroidApkError(Exception):
  def __init__(self, msg):
    print msg


class ApkProcessor:
  
  def __init__(self, apk_path):
    self.apk_path = apk_path
    self.unzip_path = "???"

    self.validity = False
    self.unpacked = False
    self.installed = False

    self.size = os.path.getsize(apk_path)

    self.info = {}

    self.package_name = ""

    self.static_init()


  def static_init(self):
    try:
      a = apk.APK(self.apk_path)
      if a.is_valid_APK():
        self.info["package_name"] = a.get_package()
        self.info["permissions"]=a.get_details_permissions_new()
        self.info["main_activity"]=a.get_main_activity()

        #vm = dvm.DalvikVMFormat(a.get_dex())
        #vmx = analysis.uVMAnalysis(vm)

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
            procs.append(self.info["package_name"] + proc)
          else:
            procs.append(procs)

        print procs



        #static_calls = {}
        #static_calls["all_methods"] =self.get_methods(vmx)
        #static_calls["is_native_code"] = analysis.is_native_code(vmx) # search for existance
        #static_calls["is_dynamic_code"] = analysis.is_dyn_code(vmx)
        #static_calls["is_reflection_code"]= analysis.is_reflection_code(vmx)

        #static_calls["dynamic_method_calls"]= analysis.get_show_DynCode(vmx)
        #static_calls["reflection_method_calls"]= analysis.get_show_ReflectionCode(vmx)
        #static_calls["permissions_method_calls"]= analysis.get_show_Permissions(vmx)
        #static_calls["crypto_method_calls"]= analysis.get_show_CryptoCode(vmx) # java internal crypto usage
        #static_calls["native_method_calls"]= analysis.get_show_NativeMethods(vmx)
        #print static_calls
        #print self.info


      else:
        raise ApeDroidApkError("apk file not valid")
    except (IOError, OSError,BadZipfile) as e:
      raise ApeDroidApkError("Error open file %s" % e)



  def install(self):
    if self.installed:
      return True

    p = subprocess.Popen(["adb", "install", self.apk_path],
                         stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    if("Failure" in out):
      raise ApeDroidApkError(self.fullname + "install failed. " + out)
      return False
    else:
      self.installed = True
      return True


  def uninstall(self):
    if not self.installed:
      return True
    
    p = subprocess.Popen(["adb", "uninstall", self.package_name],
                         stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()
    
    if not err is None:
      # do something
      return False
    else:
      if "Failure" in out:
        # do something
        return False
      else:
        # do something
        return True
      

  def start(self):
    if not "." in self.info["main_activity"]:
      self.info["main_activity"] = "." + self.info["main_activity"]

    if self.info["main_activity"].startswith("."):
      to_start = self.info["package_name"] + self.info["main_activity"]
    else:
      to_start = self.info["main_activity"]

    to_start = self.info["package_name"] + "/" + to_start

    print to_start

    p = subprocess.Popen(["adb", "shell", "am", "start", "-n", to_start],
                         stdout=subprocess.PIPE)
    out, err = p.communicate()
    p.wait()
    if not err is None:
      # do something
      return False

    if "not started" in out:
      # do something
      return False

    print out
    return True


  def clear(self, procsinfo):
    pass
    #implement this in ProcsInfo


  def my_procs(self, procsinfo):
    pass
    # find actual started process by ps comparison


  def my_mem_consumption(self, meminfo):
    pass
    # get memory consumption for all application procs


  def is_alieve(self, procsinfo):
    pass
    # implement proc alive functionality in procsinfo (take list as param)


if __name__ == "__main__":
  processor = ApkProcessor("./done.apk")
  #print processor.start()
  print processor.size

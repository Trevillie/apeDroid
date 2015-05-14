# -*- coding:utf8 -*-
# written by trevillie

import os
import zipfile
from AnalysisXML.AXML import AXML


class UnzipAPK():

  def __init__(self, apk_path, unzip_path):
    self.apk_path = apk_path
    self.apk_extr_base_dir = unzip_path
    self.apk_name = os.path.basename(apk_path)[:-4]
    print "apk name : " + self.apk_name
    self.apk_extr_dir = os.path.join(self.apk_extr_base_dir, self.apk_name)
    print "apk extracr dirctory : " + self.apk_extr_dir

    self.classes_dex_path = os.path.join(self.apk_extr_dir, "classes.dex")
    self.dexdump_path = os.path.join(self.apk_extr_dir, "classes.txt")
    self.manifest_path = os.path.join(self.apk_extr_dir, "AndroidManifest.xml")
    self.unpacked_manifest_path = os.path.join(self.apk_extr_dir,
                                               "AndroidManifest_unpack.xml")

    if not os.path.exists(self.apk_extr_dir):
      os.mkdir(self.apk_extr_dir)
      self.unzip()
      self.dexdump()
      self.unpack_manifest()


  def get_activities(self):
    axml_analysis = AXML(self.manifest_path)
    mainfest_content = axml_analysis.get_xml()
    packagename = axml_analysis.get_package()
    xml_content = mainfest_content.split("<application")[1:]
    info_list = xml_content[0].split("<activity")[1:]
    activities = []
    for tmp in info_list:
      tmp = tmp.split('android:name=')[1]
      tmp = tmp.split('" ')[0].replace('"', "")
      if ">" in tmp:
        tmp = tmp.split('>')[0]
      tmp = tmp.encode("ascii", "ignore")
      if tmp.startswith("."):
        activities.append(packagename + tmp)
      elif tmp.startswith(packagename):
        activities.append(tmp)
      elif not "." in tmp:
        activities.append(packagename + "." + tmp)
      else:
        activities.append(tmp)
    return activities


  def get_class_name(self):
    import codecs
    dexdump_str = codecs.open(self.dexdump_path, 'rb').read()
    class_name_list = []
    buf_result = dexdump_str.split("Class #")
    for class_file in buf_result:
      try:
        class_code = class_file.split("\n")
        for smali in class_code:
          if "  Class descriptor  :" in smali:
            class_name = smali.split("'")[1][1:-1].replace("/", ".")
            class_name_list.append(class_name)
            break
      except:
        pass
    print self.apk_name + " class name retrieved ..."
    return class_name_list


  def unpack_manifest(self):
    cmd = "java -jar tool/AXMLPrinter2.jar %s > %s"

    if os.path.exists(self.manifest_path):
      try:
        os.system(cmd % (self.manifest_path, self.unpacked_manifest_path))
        manifest_object = open(self.unpacked_manifest_path)
        self.manifest_content = manifest_object.read()
        print self.apk_name + " manifest unpacked ..."
      except:
        print "failure unpack manifest"
        raise


  def get_package_name(self):
    fr = open(self.unpacked_manifest_path, 'r')
    package_name = ""
    for line in fr:
      pos = line.find('package="')
      if pos > 0:
        package_name = line[pos+9:-1].strip('"')
    print self.apk_name + " package name retrieved ..."
    return package_name


  def unzip(self):
    print self.apk_path + ' unzip starting ...'
    with zipfile.ZipFile(self.apk_path, 'r') as z:
      z.extractall(self.apk_extr_dir)
    print self.apk_path + ' unzip complete ...'


  def dexdump(self):
    cmd = 'tool/dexdump -d %s > %s'
    if os.path.exists(self.classes_dex_path):
      os.system(cmd % (self.classes_dex_path, self.dexdump_path))
      print self.apk_name + " dexdump complete ..."
    else:
      print self.apk_name + " dex path does not exist, dexdump failed ..."


  def get_all_name(self):
    all_file_name = []
    all_dir_name = []

    for dirpath, dirnames, filenames in os.walk(self.apk_extr_dir):
      all_file_name.extend(filenames)
      all_dir_name.extend(dirnames)

    print self.apk_name + " all file names in package retrieved ..."
    return all_file_name, all_dir_name


if __name__ == "__main__":
  #pass
  apkPath = r"./momo.apk"
  obj = UnzipAPK(apkPath, "./unzipdir")

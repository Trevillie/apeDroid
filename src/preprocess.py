"""
@p1 : "multiply" or "tamper"
"""

import os
import subprocess
from shutil import copyfile, rmtree, move
from controller.APK import APK
from preprocess import multiplier
from preprocess.injector import inject
from preprocess import tamper


def rel(relpath):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)),relpath)

place_dir = rel("./preprocess/factory/multiplier/")

def u_list_dir(path):
  """
  @p1 : absolute path
  """
  if os.path.exists(path):
    names = os.listdir(path)
    return [os.path.join(path, name) for name in names]
  else:
    print "Path %s does not exists...", path
    return []


def multiply():
  apk_paths = u_list_dir(rel("./preprocess/ori_apk/"))
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

    for mapk in u_list_dir(place_dir):
      name = os.path.basename(mapk)
      copyfile(mapk, os.path.join(dest_path, name))

    print "----------------------------------------"
    print package_name, "multiplication step done!"
    print "----------------------------------------"


def unpack_apk(package_path, outdir):
  p = subprocess.Popen(["apktool", "d", "-o", outdir, package_path],
                       stdout=subprocess.PIPE)
  p.wait()
  out, err = p.communicate()

  if not err is None:
    raise OSError


def tamper_apk(package_path):
  apk = APK(package_path)
  main_activity = apk.main_activity     # fully-qualified name here
  out_list = []

  for name in ["res", "man", "sma"]:
    outdir = os.path.join(os.path.dirname(package_path), name)
    unpack_apk(package_path, outdir)
    out_list.append(outdir)

    if name == "sma":
      tamper.tamper_sma(outdir, main_activity)
      continue
    if name == "man":
      tamper.tamper_man(outdir)
      continue
    if name == "res":
      tamper.tamper_res(outdir)

  return out_list


def tamper_it(from_path, to_path, working_dir):
  file_name = os.path.basename(from_path)
  working_apk = os.path.join(working_dir, file_name)
  name, _ = file_name.split(".")

  copyfile(from_path, working_apk)
  tamper_apk(working_apk)

  os.chdir(working_dir)
  subprocess.call(["./pack.sh"])
  os.chdir(os.path.dirname(rel(__file__)))

  for f in ["res", "man", "sma"]:
    f_src = os.path.join(working_dir, f+".apk")
    f_dst = os.path.join(to_path, name+"_"+f+".apk")
    move(f_src, f_dst)
    print f_dst, "created..."

  os.remove(working_apk)


def do_tamper():
  sample_dir = rel("./preprocess/samples/")

  p = subprocess.Popen(["find", sample_dir, "-name", "apk_res*"],
                       stdout=subprocess.PIPE)
  p.wait()
  out, err = p.communicate()
  if not err is None:
    raise OSError
  
  apk_res_paths = []

  for line in out.split("\n"):
    apk_res_path = line.strip()
    if apk_res_path != "":
      apk_res_paths.append(apk_res_path)

  for apk_res_path in apk_res_paths:
    tamper_dir = os.path.join(os.path.dirname(apk_res_path), "tamper")
    tamper_it(apk_res_path, tamper_dir, rel("./preprocess/factory/tamper"))
    print apk_res_path, "tampering complete..."

  print "All tampering operations are done..."


if __name__ == "__main__":
  # deal with arg
  #multiply()
  #tamper_apk("/home/hector/playground/test/002.apk")
  do_tamper()

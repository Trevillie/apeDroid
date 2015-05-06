import os
import subprocess
from shutil import rmtree
import hashlib


def rel(relpath):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)),relpath)


def unpack_apk(package_path, outdir):
  p = subprocess.Popen(["apktool", "d", "-o", outdir, package_path],
                       stdout=subprocess.PIPE)
  p.wait()
  out, err = p.communicate()

  if not err is None:
    raise OSError


def list_dir(path):
  if os.path.exists(path):
    names = os.listdir(path)
    return [os.path.join(path, name) for name in names]
  else:
    print "Path %s does not exists...", path
    return []


def get_so_md5(apk_file):
  """
  Assume apk_file holds absolute file path
  """
  so_md5s = {}
  unpack_path = rel(os.path.join("./md5", "apk"))
  unpack_apk(apk_file, unpack_path)
  lib_path = os.path.join(unpack_path, "lib", "armeabi")

  if not os.path.exists(lib_path):
    raise OSError

  for so_file in list_dir(lib_path):
    file_name = os.path.basename(so_file)
    with open(so_file, "r") as handle:
      so_md5s[file_name] = hashlib.md5(handle.read()).hexdigest()

  rmtree(unpack_path)
  return so_md5s


def compare_dict(foo, bar, verbose=True):
  foo_keys = set(foo.keys())
  bar_keys = set(bar.keys())
  shared_keys = foo_keys.intersection(bar_keys)
  flag = True
  for key in shared_keys:
    if foo[key] != bar[key]:
      if verbose:
        print "+++", key, "was modified..."
      flag = False
    else:
      if verbose:
        print "---", key, "stayed the same..."
  return flag


if __name__ == "__main__":
  ori_md5 = get_so_md5("./jrtt_original.apk")
  new_md5 = get_so_md5("./jrtt_protected.apk")
  # print ori_md5
  # print new_md5
  print compare_dict(ori_md5, new_md5)

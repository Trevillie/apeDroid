import os
from shutil import copyfile


def rel(relpath):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)),relpath)


def get_vendor_list():
  vendor_list = rel("./vendor_list")
  if not os.path.exists(vendor_list):
    raise IOError
  vl = []
  with open(vendor_list, "r") as handle:
    for line in handle:
      line_content = line.strip()
      if line_content != "":
        vl.append(line_content)
  return vl


def mkdir(path):
  if not os.path.exists(path):
    os.makedirs(path)
    return True
  else:
    raise IOError
    return False


def init_file_structure(name, vl, path=rel("./samples")):
  apk_path = os.path.join(path, name)
  mkdir(apk_path)
  vl.append("")
  for vendor in vl:
    p = os.path.join(apk_path, vendor, "tamper")
    mkdir(p)
  return apk_path


if __name__ == "__main__":
  vl = get_vendor_list()
  print vl
  init_file_structure("test", vl)

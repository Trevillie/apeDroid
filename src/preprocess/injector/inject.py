import os
from shutil import move, copyfile


def name2path(smali_path, activity_name):
  """
  activity_name is fully qualified.
  """
  return os.path.join(smali_path, activity_name.replace(".", "/")) + ".smali"


def place_injector(place_dir="../factory/reactor/apk/smali"):

  if os.path.exists(place_dir):
    injector_path = "./Injector.smali"
    _, file = os.path.split(injector_path)
    copyfile(injector_path, os.path.join(place_dir, file))
    return True
  else:
    print "Specified Directory Does Not Exists... Injector Not Placed..."
    return False


def inject_main_activity(path, phosphor="./to_add.smali"):

  is_inside = False
  is_instruction = False
  is_written = False

  dirctory, _ = os.path.split(path)
  temp = os.path.join(dirctory, ".temp.smali")

  with open(path, "r") as old_smali:
    with open(temp, "w") as new_smali:
      for line in old_smali:

        if ".method" in line and "onCreate(" in line and ")V" in line:
          is_inside = True

        if is_inside:
          lc = line.strip()
          if not lc == "" and not lc.startswith("."):
            is_instruction = True

        if is_inside and is_instruction and not is_written:
          with open(phosphor, "r") as to_add:
            for inj_line in to_add:
              new_smali.write(inj_line)
          is_written = True

        new_smali.write(line)

  os.remove(path)
  move(temp, path)
  return True


if __name__ == "__main__":
  #inject_main_activity("./before.smali", "./to_add.smali")
  print name2path("../factory/reactor/apk/smali",
                  "com.tencent.news.activity.SplashActivity")

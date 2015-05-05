import os
import pprint
from time import sleep

from controller.Device import Device
from controller.APK import APK, APKRuntime 
from controller.Procs import Procs
from controller.MemInfo import MemInfo
from controller.Meow import Meow


def rel(relpath):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)),relpath)

apk_path = rel("../factory/reactor/apk.apk")
sample_path = rel("./preprocess/samples/")
sigs = ["ori", "inj", "res"]
tamps = ["man", "res", "sma", "so"]

def list_dir(path):
  try:
    names = os.listdir(path)
    return [os.path.join(path, name) for name in names]
  except OSError:
    print "! os.list on %s fails" % path
    return []


def get_sample_structure(path):
  if not os.path.exists(path):
    raise OSError
  sample = {}
  for p in list_dir(path):
    bn = os.path.basename(p)
    if bn == "tamper":
      for tp in list_dir(p):
        tbn = os.path.basename(tp)
        for tamp in tamps:
          if (tamp+".apk") in tbn:
            sample["tamper_"+tamp] = tp
            break
      continue
    if os.path.isdir(p):
      sample[bn] = get_sample_structure(p)
      continue
    for sig in sigs:
      if ("_"+sig) in bn:
        sample[sig] = p
        break
  return sample


def is_up(procs, name, verbose=True):
  for i in range(3):
    if not procs.is_alive(name):
      if verbose:
        print "---------------------------------------------------------------"
        print "Package", name, "can not run on this device."
        print "Down on count", (i+1), "/ 3  ", "Quiting..."
        print "---------------------------------------------------------------"
      return False
    sleep(3)

  if verbose:
    print "---------------------------------------------------------------"
    print "Package", name, "is started successfully."
    print "---------------------------------------------------------------"
    print "Checking Memory Information..."
    return True


def handle_sample(tests, sample, procs, mems, logs, verbose=True):
  """
  handle the 7-dim tuple for sample
  """
  ##### ori
  if "ori" in tests:
    apk = APK(sample["ori"])
    apk_runtime = APKRuntime(apk)

    # static properties
    if verbose:
      print "name :", apk.package_name
      print "size :", apk.size
      print "manifest:", apk.permissions

    apk_runtime.install()
    sleep(5)
    apk_runtime.start()
    sleep(5)

    # check if the activity starts successfully...
    if not is_up(procs, apk.package_name):
      return

    # memory information
    for i in range(3):
      u = procs.get_user(apk.package_name)
      pids, names = procs.get_user_procs(u)

      if verbose:
        print "-----------------------------"
        print "Round", (i+1), "/ 3  "
        print "user :", u
        print "pids :", pids
        print "num  :", len(pids)
        print "name :", names
      pss, uss = mems.get_pids_mem(mems.get_mem_info(), pids, verbose=True)
      sleep(3)

    # anti-bebugging
    print 
    print "-------------------------------"
    print "Anti-Debugging Test"
    u = procs.get_user(apk.package_name)
    pids, names = procs.get_user_procs(u)
    mpis = procs.get_main_process_info(apk.package_name)
    if len(mpis) == 1:
      main_process_info = mpis[0]
      
      tracerpid = procs.process_trace_info(main_process_info["pid"])
      print "TracerPid for", main_process_info["pid"], "is", tracerpid

      if tracerpid == "0":
        print "The main process is not being traced by any other process now."
        print "Try stracing", main_process_info["pid"]
        return_code = procs.strace_process(main_process_info["pid"], 8)
        if return_code == "succ":
          print "Straced Successfully!"
          print "No Anti-Debugging tricks found on the process."
        elif return_code == "died":
          print "Straced Attached. But process terminates itself."
          print "Anti-Debugging by process suiside after attachment."
        elif return_code == "fail":
          print "Strace did not attached successfully..."
          print "This is strange in this circumstance, try again later..."
      else:
        print "Process now being traced by", tracerpid
        proc_info = procs.get_proc_info(tracerpid)
        print proc_info
        if proc_info["ppid"] == main_process_info["pid"]:
          print "Main process is traced by its child process."
        t_pid = procs.process_trace_info(proc_info["pid"])
        print "TracerPid for", proc_info["pid"], "is", t_pid

        # try killing the watching process
        print "Killing watching process", tracerpid
        procs.kill_process(tracerpid)
        sleep(5)
        if procs.is_alive(main_process_info["name"]):
          print "Main process still runs."
          print "The main process is not being traced by any other process now."
          print "Try stracing", main_process_info["pid"]
          return_code = procs.strace_process(main_process_info["pid"], 8)
          if return_code == "succ":
            print "Straced Successfully!"
            print "No Anti-Debugging tricks other than tracing each other is found."
          elif return_code == "died":
            print "Straced Attached. But process terminates itself."
            print "Anti-Debugging by process suiside after attachment."
          elif return_code == "fail":
            print "Strace did not attached successfully..."
            print "This is strange in this circumstance, try again later..."
        else:
          print "Main process suisides after the struture breaks apart."

      print
      print "Anti-Debugging Test Ends here."

    else:
      print "More than one main process..."
      print "Skipping Anti_Debugging Test..."

    # clean things up
    sleep(5)
    apk_runtime.uninstall()

  ##### inj
  if "inj" in tests:
    apk = APK(sample["inj"])
    apk_runtime = APKRuntime(apk)

    apk_runtime.install()
    sleep(5)
    apk_runtime.start()
    sleep(5)

    # check if the activity starts successfully...
    if not is_up(procs, apk.package_name):
      return

    u = procs.get_user(apk.package_name)
    procs.kill_user(u)

    # measure startup time and log clear functionality
    sleep(3)
    logs.clear()
    logs.turn_on(apk.package_name)
    sleep(2)
    apk_runtime.start()
    sleep(5)
    logs.turn_off()
    logs.refresh()

    # clean things up
    apk_runtime.uninstall()


if __name__ == "__main__":
  # AVD Checking...
  dev = Device()
  while not dev.check_device():
    print "waiting for device connection..."
    sleep(3)

  print "AVD Connected Successfully..."
  print 

  # System Utility Initialization...
  proc_service = Procs()
  mem_service  = MemInfo()
  log_service  = Meow()

  log_service.thread_up()

  # Set Up Apk
  pp = pprint.PrettyPrinter(indent=4)
  for sample_path in list_dir(sample_path):
    print sample_path
    sample = get_sample_structure(sample_path)
    pp.pprint(sample)

    handle_sample(["ori"], sample, proc_service, mem_service, log_service)

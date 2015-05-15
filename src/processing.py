# written by trevillie
import os
import pprint
from time import sleep
from shutil import rmtree
import zipfile
import zlib

from controller.Device import Device
from controller.APK import APK, APKRuntime 
from controller.Procs import Procs
from controller.MemInfo import MemInfo
from controller.Meow import Meow
from network.Network import Network
from identifier.CheckProtect import CheckProtect
from so import so


def rel(relpath):
  return os.path.join(os.path.dirname(os.path.abspath(__file__)),relpath)

apk_path = rel("../factory/reactor/apk.apk")
sample_path = rel("./preprocess/samples/")
sigs = ["ori", "inj", "res"]
tamps = ["man", "res", "sma"]
identifier_unpack_dir = "./identifier/processing_unpack"
identifier_error_log  = "./identifier/processing_errors"


def average(l):
  return float(sum(l))/max(len(l),1)


def num(s):
  try:
    return int(s)
  except ValueError:
    return float(s)


def parse_time(t):
  h, m, s = [num(n) for n in t.split(":")]
  return 3600*h + 60*m + s


def time_delta(t1, t2):
  """
  Assume t1 earlier than t2, and time delta lasts no longer than 12 hours
  """
  time1 = parse_time(t1)
  time2 = parse_time(t2)
  if time1 > time2:
    h = num(t1.split(":")[0])
    time2 += 3600*(h+1)
  return time2 - time1


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
    return True


def start_network_peek(nw, verbose=True):
  nw.thread_up()
  nw.turn_on()
  if verbose:
    print
    print "Network Peeking Started..."
    print


def stop_network_peek(nw, verbose=True):
  """
  This is used in the context of an apk runtime
  @r: list of dictionary, [dict{tag->value}]
  """
  nw.turn_off()
  nw.thread_down()
  conns = nw.get_masked_connection()
  if verbose:
    print
    print "This app was connected with the following ips via tcp connection:"
    for conn in conns:
      pp.pprint(conn)
    print
  nw.refresh()
  return conns


def can_run(apk_path, procs, verbose=True):
  if verbose:
    print
    print "testing whether", apk_path, "can run or not..."
    print apk_path
    print "waiting..."
    print
  sleep(10)

  apk = APK(apk_path)
  apk_runtime = APKRuntime(apk)
  ret = False

  for i in range(3):
    apk_runtime.install()
    sleep(5)
    apk_runtime.start()
    sleep(3)
    if is_up(procs, apk.package_name):
      ret = True
      break
    sleep(3)
    apk_runtime.uninstall()

  if ret:
    apk_runtime.uninstall()
  return ret


def so_index(sample, brand_name):
  """
  @p: both are apk files
  @r: is the so files same as before?
  """
  ori_apk = sample["ori"]
  pro_apk = sample[brand_name]["ori"]
  ori_md5 = so.get_so_md5(ori_apk)
  new_md5 = so.get_so_md5(pro_apk)
  return so.compare_dict(ori_md5, new_md5)


def sig_index(start_status, brand):
  """
  @r: string, describes the signature handling pattern
  """
  try:
    ori = start_status["ori"]
    ori_pro = start_status[brand]["ori"]
    res = start_status["res"]
    res_pro = start_status[brand]["res"]
  except KeyError:
    return "No Such Brand"

  if not ori:
    return "Original App Broken"
  if ori_pro:
    return "Signature Not Protected"
  if not res:
    return "Resign App Failure"
  if res_pro:
    return "Signature Protected"
  else:
    return "Unknown Condition"


def tamper_index(run_status):
  """
  @r: string, "0" for can run, "1" for can not
  010 stands for NO anti-tamper on manifest tampering
                    anti-tamper on resource tampering
             adn NO anti-tamper on smali tampering
  returns "x" when the test cannot be done
  """
  if not run_status["res"]:
    return "x"
  return "".join(str(int(run_status["tamper_"+k])) for k in tamps)


def dynamic_loading_index(unpack_dir, apk_path, err_log):
  try:
    if not os.path.exists(unpack_dir):
      os.makedirs(unpack_dir)
    checker = CheckProtect(apk_path, unpack_dir)
    print checker.get_protector_name()
    records = checker.get_dict()
  except TypeError:
    with open(err_log, "a") as err_handle:
      err_handle.write(", ".join([apk_path, "TypeError"])+"\r\n")
    records = {"Nothing" : "TypeError"}
  except zipfile.BadZipfile:
    with open(err_log, "a") as err_handle:
      err_handle.write(", ".join([apk_path, "BadZipfile"])+"\r\n")
    records = {"Nothing" : "BadZipfile"}
  except zlib.error:
    with open(err_log, "a") as err_handle:
      err_handle.write(", ".join([apk_path, "zlib error"])+"\r\n")
    records = {"Nothing" : "zlib error"}

  rmtree(unpack_dir, ignore_errors=True)
  return records


def test_can_run(sample, procs, test=False):
  """
  @r: dictionary: "res" -> True/False, same topology as sample structure
  """
  result = {}
  for item in sample:
    if item == "":
      continue
    if item in sigs or item in ["tamper_"+tamp for tamp in tamps]:
      if test:
        result[item] = True
      else:
        result[item] = can_run(sample[item], procs)
    else:
      result[item] = test_can_run(sample[item], procs, test=test)
  return result


def test_res(apk_path, procs, mems, verbose=True):
  """
  @p: sample - sample_structure instance
  """
  ##### ori
  apk = APK(apk_path)
  apk_runtime = APKRuntime(apk)
  ret = {}

  # static properties
  ret["size"] = apk.size
  ret["permission"] = apk.permissions
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
  # return value in float, KB
  print "Checking Memory Information..."
  pss_bucket = []
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
    #pss, uss = mems.get_pids_mem(mems.get_mem_info(), pids, verbose=True)
    pss = mems.get_pids_mem(pids, verbose=True)
    pss_bucket.append(pss)
    sleep(3)

  ret["proc_num"] = len(pids)
  ret["memory"] = average(pss_bucket)

  # anti-bebugging
  anti_debugging_status = {
    "can_trace" : False,
    True  : {
      "trace_succ" : False
    },
    False : {
      "tracer_pid"  : False,
      "tracer_name" : False,
      "tracer_child": False,
      "kill_tracer" : False,
      "trace_succ"  : False
    }
  }
  print 
  print "-------------------------------"
  print "Anti-Debugging Test"
  u = procs.get_user(apk.package_name)
  pids, names = procs.get_user_procs(u)
  mpis = procs.get_main_process_info(apk.package_name)
  if len(mpis) == 1:
    anti_debugging_status["tested"] = True
    main_process_info = mpis[0]
    tracerpid = procs.process_trace_info(main_process_info["pid"])
    print "TracerPid for", main_process_info["pid"], "is", tracerpid

    if tracerpid == "0":
      anti_debugging_status["can_trace"] = True
      print "The main process is not being traced by any other process now."
      print "Try stracing", main_process_info["pid"]
      sleep(3)
      return_code = procs.strace_process(main_process_info["pid"], 8)

      if return_code == "succ":
        anti_debugging_status[True]["trace_succ"] = True
        print "Straced Successfully!"
        print "No Anti-Debugging tricks found on the process."

      elif return_code == "died":
        anti_debugging_status[True]["trace_succ"] = False
        print "Straced Attached. But process terminates itself."
        print "Anti-Debugging by process suiside after attachment."

      elif return_code == "fail":
        anti_debugging_status[True]["trace_succ"] = False
        print "Strace did not attached successfully..."
        print "This is strange in this circumstance, try again later..."

    else:
      anti_debugging_status["can_trace"] = False
      print "Process now being traced by", tracerpid
      proc_info = procs.get_proc_info(tracerpid)
      print proc_info
      anti_debugging_status[False]["tracer_pid"] = tracerpid
      anti_debugging_status[False]["tracer_name"] = proc_info["name"]

      if proc_info["ppid"] == main_process_info["pid"]:
        anti_debugging_status[False]["tracer_child"] = True
        print "Main process is traced by its child process."
      else:
        anti_debugging_status[False]["tracer_child"] = True

      t_pid = procs.process_trace_info(proc_info["pid"])
      print "TracerPid for", proc_info["pid"], "is", t_pid

      # try killing the watching process
      print "Killing watching process", tracerpid
      procs.kill_process(tracerpid)
      sleep(5)
      if procs.is_alive(main_process_info["name"]):
        anti_debugging_status[False]["kill_tracer"] = True
        print "Main process still runs."
        print "The main process is not being traced by any other process now."
        print "Try stracing", main_process_info["pid"]
        sleep(3)
        return_code = procs.strace_process(main_process_info["pid"], 8)

        if return_code == "succ":
          anti_debugging_status[False]["trace_succ"] = True
          print "Straced Successfully!"
          print "No Anti-Debugging tricks other than tracing each other is found."

        elif return_code == "died":
          anti_debugging_status[False]["trace_succ"] = False
          print "Straced Attached. But process terminates itself."
          print "Anti-Debugging by process suiside after attachment."

        elif return_code == "fail":
          anti_debugging_status[False]["trace_succ"] = False
          print "Strace did not attached successfully..."
          print "This is strange in this circumstance, try again later..."
      else:
        anti_debugging_status[False]["kill_tracer"] = False
        anti_debugging_status[False]["trace_succ"] = False
        print "Main process suisides after the struture breaks apart."

    print
    print "Anti-Debugging Test Ends here."

  else:
    anti_debugging_status["tested"] = False
    print "More than one main process..."
    print "Skipping Anti_Debugging Test..."

  ret["debug"] = anti_debugging_status

  # clean things up
  sleep(5)
  apk_runtime.uninstall()
  return ret


def test_injected(apk_path, procs, logs):
  """
  Test indexes of injected apps
  @p: apk_path, such as sample["inj"]
  @r: startup_time, log clear status(raw)
  """
  apk = APK(apk_path)
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
  trigger_time, start_time, log_clear = logs.turn_off()
  logs.refresh()

  # clean things up
  apk_runtime.uninstall()

  startup_cost = time_delta(trigger_time, start_time)
  print "time_delta :", startup_cost

  return startup_cost, log_clear


def work_on_one_brand(sample, run_status, procs, mems, logs, nets):
  """
  Suppose you have the whole package of apps by one brand
  ONLY use key of "ori", "res", "inj", "tamper_"[...]
  Let nothing be added in when thing goes wrong
  Be ready to except KeyError when analysing with the function
  """
  info = {}
  start_network_peek(nets)

  if run_status["res"]:
    res_info = test_res(sample["res"], procs, mems)
    for k in res_info:
      info[k] = res_info[k]

  dynamic_info = dynamic_loading_index(identifier_unpack_dir, sample["res"],
                                       identifier_error_log)
  info["dynamic_loading"] = dynamic_info

  tamper_info = tamper_index(run_status)
  if tamper_info != "x": info["tamper"] = tamper_info

  if run_status["inj"]:
    startup_cost, log_clear = test_injected(sample["inj"], procs, logs)
    bool2str = lambda x: "1" if x else "0"
    levels = ["V", "D", "I", "W", "E"]
    info["startup_cost"] = str(startup_cost)
    info["log_clear"] = "".join([bool2str(log_clear[l]) for l in levels])
  else:
    info["startup_cost"] = "Can Not Measure"
    info["log_clear"] = "Can Not Measure"

  info["network"] = stop_network_peek(nets)
  return info


if __name__ == "__main__":
  # AVD Checking...
  dev = Device()
  while not dev.check_device():
    print "waiting for device connection..."
    sleep(3)

  print "AVD Connected Successfully..."
  print 

  # System Utility Initialization...
  proc_service    = Procs()
  mem_service     = MemInfo()
  log_service     = Meow()
  network_service = Network()

  log_service.thread_up()

  # Set Up Apk
  pp = pprint.PrettyPrinter(indent=4)
  samples_info = {}
  for sample_path in list_dir(sample_path):
    print sample_path
    sample = get_sample_structure(sample_path)
    # pp.pprint(sample)
    run_status = test_can_run(sample, proc_service, test=True)

    # vendors == ["baidu", "bangcle", ...]
    vendors = [k for k in sample.keys()
               if not k.startswith("tamper_") and not k in sigs]
    sample_info = {}

    sleep(15)
    ori_info = work_on_one_brand(sample, run_status, proc_service,
                                 mem_service, log_service, network_service)
    sample_info["original"] = ori_info

    # brand == str(vendor name)
    for brand in vendors:
      sleep(15)
      # standalone test
      info = work_on_one_brand(sample[brand], run_status[brand], proc_service,
                               mem_service, log_service, network_service)
      pp.pprint(info)

      # comparison test
      info["so"] = so_index(sample, brand)              # bool
      info["signature"] = sig_index(run_status, brand)  # str
      sample_info[brand] = info

    samples_info[os.path.basename(sample_path)] = sample_info

  pp.pprint(samples_info)

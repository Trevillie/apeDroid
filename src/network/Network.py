import os
import subprocess
import re
import socket
import struct
import pprint


def hex2ip(hex_string):
  return socket.inet_ntoa(struct.pack("<L", int(hex_string, 16)))


def get_sock_info(num):
  p = subprocess.Popen(["adb", "shell", "cat", "/proc/net/tcp"],
                       stdout=subprocess.PIPE)
  p.wait()
  out, err = p.communicate()

  if err is None:
    for line in out.split("\r\n"):
      if ":" in line:
        if str(num) == line.split(":")[0].strip():
          src_ip = hex2ip(line.split(":")[1].strip())
          src_port = str(int(line.split(":")[2].split(" ")[0].strip(), 16))
          dst_ip = hex2ip(line.split(":")[2].split(" ")[1].strip())
          dst_port = str(int(line.split(":")[3].split(" ")[0].strip(), 16))
          print "src:", src_ip+":"+src_port
          print "dst:", dst_ip+":"+dst_port
          return line.strip()
  else:
    return ""


def get_ip_info(ip_str):
  p = subprocess.Popen(["curl", "--silent","ipinfo.io/"+ip_str], stdout=subprocess.PIPE)
  p.wait()
  out, err = p.communicate()
  info = {}

  if err is None:
    ip_re = re.compile("^\"(.+)\": \"(.+)\"$")
    for line in out.split("{")[1].split("}")[0].split("\n"):
      match = ip_re.match(line.strip().strip(","))
      if not match is None:
        attrib = match.groups()[0]
        value = match.groups()[1]
        info[attrib] = value

  return info


def get_dst_ip():
  p = subprocess.Popen(["sudo", "lsof", "-i", "tcp", "-c", "VBoxHeadl",
                        "-n", "-a"], stdout=subprocess.PIPE)
  p.wait()
  out, err = p.communicate()

  ips = []
  if err is None:
    for line in out.split("VBoxHeadl"):
      if "->" in line:
        ip = line.split("->")[1].split(":")[0]
        ips.append(ip)
        print ip

  return ips


if __name__ == "__main__":
  pp = pprint.PrettyPrinter(indent=4)
  for ip in get_dst_ip():
    print ip
    pp.pprint(get_ip_info(ip))

  exit()
  input = os.popen("adb shell strace -p 2755 -f -e trace=network -s 10000")
  socks = set([])
  while True:
    try:
      line = input.readline()
    except KeyboardInterrupt:
      break
    if "recvfrom" in line or "sendto" in line:
      if not "resume" in line:
        num = line.split("(")[1].split(",")[0]
        if num not in socks:
          socks.add(num)
          print num
          print get_sock_info(num)
          print 

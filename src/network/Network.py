# written by trevillie
import os
import subprocess
import re
import socket
import struct
import threading
import pprint
from time import sleep

class Network:
  def __init__(self):
    self.connection_pool = {}
    self.turn_off()
    self.thread = None
    self.running = False


  def refresh(self):
    self.__init__()


  def turn_on(self):
    self.on = True
    self.update_connection_info()


  def turn_off(self):
    self.on = False


  def run(self):
    while self.running:
      if self.on:
        self.update_connection_info()
      sleep(2)


  def thread_up(self):
    self.thread = threading.Thread(target=self.run)
    self.running = True
    self.thread.start()


  def thread_down(self):
    if self.running:
      self.running = False
      self.thread.join()
      self.thread = None


  def get_ip_info(self, ip_str):
    p = subprocess.Popen(["curl", "--silent","ipinfo.io/"+ip_str], stdout=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    info = {}
    if err is None:
      ip_re = re.compile("^\"(.+)\": \"(.+)\"$")
      if "{" in out:
        for line in out.split("{")[1].split("}")[0].split("\n"):
          match = ip_re.match(line.strip().strip(","))
          if not match is None:
            attrib = match.groups()[0]
            value = match.groups()[1]
            info[attrib] = value

    return info


  def get_dst_ip(self):
    p = subprocess.Popen(["sudo", "lsof", "-i", "tcp", "-c", "VBoxHeadl", "-n",
                          "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    out, err = p.communicate()

    ips = []
    for line in out.split("VBoxHeadl"):
      if "->" in line:
        ip = line.split("->")[1].split(":")[0]
        ips.append(ip)

    return ips


  def update_connection_info(self):
    for ip in self.get_dst_ip():
      if not ip in self.connection_pool:
        self.connection_pool[ip] = {}


  def get_connection(self):
    for ip in self.connection_pool:
      if self.connection_pool[ip] == {}:
        self.connection_pool[ip] = self.get_ip_info(ip)
    return self.connection_pool


  def get_masked_connection(self):
    tags = [#"China Unicom",
            #"China Telecom",
            "China Education and Research Network Center",
            "Province Network"]
    conns = [v for v in self.get_connection().values()
             if not any([tag in v["org"] for tag in tags])]
    return conns


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


def strace_socket(pid):
  input = os.popen("adb shell strace -p " + str(pid) +
                   " -f -e trace=network -s 10000")
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


if __name__ == "__main__":
  pp = pprint.PrettyPrinter()
  nw = Network()
  nw.thread_up()
  nw.turn_on()
  sleep(8)
  nw.turn_off()
  nw.thread_down()
  conns = nw.get_masked_connection()
  print "----"
  for conn in conns:
    pp.pprint(conn)
  print
  nw.refresh()

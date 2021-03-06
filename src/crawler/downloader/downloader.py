#!/usr/bin/python
# -*- coding:utf8 -*-
# written by trevillie

import sys
import threading
import time
import datetime as dt
import urllib2
import os
import hashlib
import signal
import Queue
import shutil


NUM_THREAD = 4
work_queue_lock = threading.Lock()


class Downloader(threading.Thread):

  def __init__(self, work_queue, output_dir, apk_list):
    threading.Thread.__init__(self)
    self.exit_event = threading.Event()
    self.work_queue = work_queue
    self.proxies = None
    self.complete = False
    self.output_dir = output_dir
    self.current_file_size = 0
    self.file_size = 0

  def exit(self):
    print("%s: asked to exit." % self.getName())
    self.exit_event.set()
    self.join()
    return self.report()

  def report(self):
    if self.file_size == 0:
      return 0
    return float(self.current_file_size) / self.file_size

  def run(self):
    while not self.exit_event.isSet():
      work_queue_lock.acquire()
      if not self.work_queue.empty():
        [self.rank, self.url, self.name] = self.work_queue.get()
        work_queue_lock.release()
        self.download()
        if self.complete == True:
          self.save()
          print "----------------------------------"
          print "       Remaining Item : " + str(self.work_queue.qsize())
          print "       " + dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          print "----------------------------------"
        else:
          work_queue_lock.acquire()
          self.work_queue.put([self.rank, self.url, self.name])
          work_queue_lock.release()
      else:
        work_queue_lock.release()
    print("%s: received exit event." % self.getName())

  def download(self):
    print("%s: downloading %s" % (self.getName(), self.url))
    self.complete = False
    self.current_file_size = 0
    self.file_size = 0
    proxy_handler = urllib2.ProxyHandler()
    if (self.proxies):
      proxy_handler = urllib2.proxyHandler(self.proxies);
    opener = urllib2.build_opener(proxy_handler)
    opener.addheaders = [
      ('User-Agent', r"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 "
        "(KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11"),
      ('Referer', self.url)
    ]
    urllib2.install_opener(opener)
    opening = urllib2.urlopen(self.url)
    meta = opening.info()
    self.file_size = int(meta.getheaders("Content-Length")[0])
    temp_file_name = "%d.apk" % (time.time() * 1000000)
    temp_dir = self.output_dir + os.sep + "temp"
    self.temp_output_path = temp_dir + os.sep + temp_file_name
    with open(self.temp_output_path, 'wb') as fil:
      block_size = 10240
      while True:
        buf = opening.read(block_size)
        self.current_file_size += len(buf)
        fil.write(buf)
        if not buf:
          if self.file_size - self.current_file_size == 0:
            self.complete = True
          break

  def save(self):
    with open(self.temp_output_path, 'r') as fil:
      m = hashlib.md5()
      m.update(fil.read())
      md5_digest = m.hexdigest()
    new_output_path = self.output_dir + os.sep + self.rank + \
                      '|' + self.name.strip() + '.apk'

    if os.path.isfile(new_output_path):
      os.remove(new_output_path)
    os.rename(self.temp_output_path, new_output_path)
    print("%s: %s.apk is completed." % (self.getName(), md5_digest))


class Monitor(threading.Thread):
  def __init__(self, threads):
    threading.Thread.__init__(self)
    self.threads = threads
    self.exit_event = threading.Event()
  def exit(self):
    self.exit_event.set()
    self.join()
  def run(self):
    while not self.exit_event.isSet():
      for t in self.threads:
        if t.report() == 0:
          print(" new"),
        else:
          print("%3.0f%%" % (t.report()*100)),
      print("")
      time.sleep(1)


def get_undownloaded_url(apk_list):
  undownloaded_urls = []
  downloaded_ranks = [name.split("|")[0] for name in os.listdir(sys.argv[2])
                      if name.endswith("apk")]
  with open(apk_list) as apks:
    for apk in apks:
      [rank, name, version, down_num, url] = apk.strip().split("^")
      if rank in downloaded_ranks:
        continue
      undownloaded_urls.append([rank, url, name])
  return undownloaded_urls


def fill_work_queue(work_queue, undownloaded_urls):
  for u in undownloaded_urls:
    work_queue.put(u)


def import_work(work_queue, apk_list):
  undownloaded_urls = get_undownloaded_url(apk_list)
  fill_work_queue(work_queue, undownloaded_urls)
  return len(undownloaded_urls)


class Watcher:

  def __init__(self):
    self.child = os.fork()
    if self.child == 0:
      return
    else:
      self.watch()

  def watch(self):
    try:
      os.wait()
    except KeyboardInterrupt:
      print("KeyBoardInterrupt")
      self.kill()
    sys.exit()

  def kill(self):
    try:
      os.kill(self.child, signal.SIGKILL)
    except OSError: pass


def main():
  if len(sys.argv) < 2:
    print("Usage: %s <apk list> <output directory>" % (sys.argv[0]))
    sys.exit(1)
  else:
    apk_list = sys.argv[1]
    output_dir = sys.argv[2]

  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  temp_dir = output_dir + os.sep + "temp"
  if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
  Watcher()
  threads = []
  work_queue = Queue.Queue()
  for i in range(NUM_THREAD):
    t = Downloader(work_queue, output_dir, apk_list)
    t.daemon = True
    t.start()
    threads.append(t)
  monitor_thread = Monitor(threads)
  monitor_thread.daemon = True
  monitor_thread.start()

  import_work(work_queue, apk_list)
  exit_flag = 0
  while exit_flag < 2:
    if work_queue.empty():
      exit_flag += 1
    else:
      exit_flag = 0
    while not work_queue.empty():
      time.sleep(10)
  for t in threads:
    t.exit()
  monitor_thread.exit()
  shutil.rmtree(temp_dir)


if __name__ == '__main__':
  main()

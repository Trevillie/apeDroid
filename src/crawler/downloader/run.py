#!/usr/bin/python
# -*- coding:utf8 -*-

import os
import subprocess as sp


def main():
  store_base_path = "../../../apps/"
  index_base_path = "../apks/"
  names = os.listdir(index_base_path)

  for name in names:
    index_path = index_base_path + name
    store_path = store_base_path + name
    sp.call(["./downloader.py", index_path, store_path])


if __name__ == "__main__":
  main()

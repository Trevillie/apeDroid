#!/usr/bin/python
# -*- coding:utf8 -*-  
# written by trevillie

from __future__ import print_function
from bs4 import BeautifulSoup  
import urllib2
import re


def get_next_page_url(url):
  r1 = re.compile('\d+_hot')
  r2 = re.compile('\d+')
  page_num = int(r2.search(r1.search(url).group()).group()) + 1
  return re.sub(r1, str(page_num)+'_hot', url)


def main():
  categories_file_path = "../categories/categories.list"
  apk_list_path = "../../apks/"
  apk_list_extension = ".list"
  url_head = "http://www.anzhi.com/dl_app.php?s="
  url_tail = "&n=5"
  page_count = 67
  apk_count = 1000
  count = 0
  dot = "^"

  with open(categories_file_path) as tasks:
    for line in tasks:
      count = 0
      [category_name, category_url] = line.strip().split()
      print("processing category " + category_name + " from " + category_url)

      list = apk_list_path + category_name + apk_list_extension
      with open(list, 'w') as f:
        for n in range(page_count):

          page_raw = urllib2.urlopen(category_url)
          page = BeautifulSoup(page_raw)
          apps = page.findAll('li')

          for app in apps[8:]:
            app_name = app.find('span', 'app_name').getText().encode('utf-8')
            app_version = app.find('span', 'app_version l') \
                             .getText()[3:].rstrip('.').encode('utf-8')
            app_num = app.find('span', 'app_downnum l') \
                         .getText()[3:].encode('utf-8')
            app_token = app.find('div', 'app_down').find('a')['onclick'][9:16]
            app_link = url_head + app_token + url_tail
            app_rank = str(count + 1).zfill(3)

            print(dot.join([app_rank, app_name, app_version,
                            app_num, app_link]), file=f)
            count += 1
            if count >= apk_count:
              break

          print(category_url)
          category_url = get_next_page_url(category_url)


if __name__ == "__main__":
  main()

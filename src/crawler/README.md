## ad-hoc apk crawler

#### What it does:
Download top 100 apks and their related information from a variant of categories on http://www.anzhi.com.

#### Just to mention:
The crawler is single threaded.
The downloader is multi-threaded.
The crawler is constructed with two crawlers and one downloader. One of the crawlers is yet not implemented.

#### How to use:
First, run sub.py in ./crawler/sub/ to update app list.
Then, run run.py in ./crawler/downloader/ to download marked apps.

#!/bin/bash
jarsigner -storepass kuranyi -keystore ../mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar apk_res.apk $1 mdy-manual
rm $1

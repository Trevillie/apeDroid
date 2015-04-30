#!/bin/bash 

cd reactor

apktool b apk -o apk.apk
rm apk-signed.apk
jarsigner -storepass kuranyi -keystore ../mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar apk-signed.apk apk.apk mdy-manual
rm apk.apk

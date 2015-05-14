#!/bin/bash 
# written by trevillie

apktool b man -o man.apk
jarsigner -storepass kuranyi -keystore ./mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar man_signed.apk man.apk mdy-manual
rm man.apk
rm -rf man
mv man_signed.apk man.apk

apktool b res -o res.apk
jarsigner -storepass kuranyi -keystore ./mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar res_signed.apk res.apk mdy-manual
rm res.apk
rm -rf res
mv res_signed.apk res.apk

apktool b sma -o sma.apk
jarsigner -storepass kuranyi -keystore ./mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar sma_signed.apk sma.apk mdy-manual
rm sma.apk
rm -rf sma
mv sma_signed.apk sma.apk

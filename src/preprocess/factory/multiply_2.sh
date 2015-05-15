#!/bin/bash 
# written by trevillie
# assume only apk.apk in the folder, multiply it for three times

### 
### inject.py
###

cd multiplier

rm apk.apk
apktool b apk -o apk.apk
jarsigner -storepass kuranyi -keystore ../mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar apk_inj_signed.apk apk.apk mdy-manual
zipalign 4 apk_inj_signed.apk apk_inj.apk
echo "apk_inj.apk ready..."

rm apk.apk
rm apk_inj_signed.apk
rm -rf apk
echo "all cleared"

cd ..

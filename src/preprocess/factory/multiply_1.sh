#!/bin/bash 
# written by trevillie
# assume only apk.apk in the folder, multiply it for three times

cd multiplier

# apk_ori.apk
cp apk.apk apk_ori.apk
echo "apk_ori.apk readying..."

# apk_res.apk
zip apk.apk -d "/META-INF/*"
jarsigner -storepass kuranyi -keystore ../mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar apk_res.apk apk.apk mdy-manual
echo "apk_res.apk ready..."

# apk_inj.apk
apktool d apk.apk

cd ..

### 
### inject.py
###


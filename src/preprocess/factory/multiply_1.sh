#!/bin/bash 
# assume only apk.apk in the folder, multiply it for three times

cd multiplier

# apk_ori.apk
echo "apk_ori.apk readying..."
cp apk.apk apk_ori.apk

# apk_res.apk
echo "apk_res.apk ready..."
jarsigner -storepass kuranyi -keystore ../mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar apk_res.apk apk.apk mdy-manual

# apk_inj.apk
apktool d apk.apk

cd ..

### 
### inject.py
###


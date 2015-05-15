#!/bin/bash

rename "s/\.apk//g" *
apks=$(ls -I *.sh)

for apk in $apks
do
  apk_arr=(${apk//_/ })
  brand=${apk_arr[0]}
  operation=${apk_arr[1]}

  echo "Signing $apk..."
  signed_name="apk_${operation}_${brand}.apk"
  temp_name=.tempapk

  jarsigner -storepass kuranyi -keystore ../mdy-manual.keystore -digestalg SHA1 -sigalg MD5withRSA -signedjar $temp_name $apk mdy-manual
  echo "$signed_name signed..."

  zipalign 4 $temp_name $signed_name
  echo "zipalign finished..."

  rm $apk
  rm $temp_name
  echo "$apk is removed..."

  echo "--------------------"
done

echo "all signed..."
echo "quiting..."
echo

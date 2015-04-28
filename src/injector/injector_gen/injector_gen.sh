#!/bin/bash

javac -cp android.jar Injector.java
dx --dex --output=Injector.dex Injector.class
java -jar baksmali.jar -o Injector.smali Injector.dex

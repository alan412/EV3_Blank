#!/bin/bash
python generateProject.py
result=${PWD##*/}
EV3=".ev3"
fn=$result$EV3
rm ../$fn
zip ../$fn -x"README.md" -x"*.ev3" -x"*.svg" -x"*.py" -x"*.sh" *
cp ../$fn  robot.ev3

#!/bin/sh
cd '.\plugin.video.bgcameras'
git checkout master
git add .
git commit -am "Regular update"
git push
echo Press Enter...
read
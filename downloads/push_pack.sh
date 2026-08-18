#!/bin/sh
# This script zips up the resourcepack and uploads it to the server under a deterministic name
# the script has to be run inside of the resourcepacks folder, on your own machine
# dont run it on the server

# where the pack lives on the server
host="cry@crystalized.cc"
dir="/var/www/html/downloads/resourcepacks/"

# zip up the pack
zip -r pack.zip *

# name the zip after its sha1 hash
sha1="$(sha1sum pack.zip | cut -d' ' -f1)"
mv pack.zip "$sha1.zip"

# push the zip to the server
scp "$sha1.zip" "$host:$dir"

# point latest.zip at the new zip
ssh "$host" "ln -sf $sha1.zip $dir/crystalized-latest.zip"

# delete old zips on the server (older than 30 days)
ssh "$host" "find $dir -maxdepth 1 -type f -mtime +30 -delete"

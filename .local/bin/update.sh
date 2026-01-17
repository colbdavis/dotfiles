#!/bin/sh

# Just updates my arch system with paru and flatpak, and local opencode 
# (if you have open Code installed with paru, npm, bun or others change this)
# By C. B. Davis

echo "(1) Update with paru
"

paru

echo "
(2) Update Flatpaks
"

flatpak update

echo "
(3) Update Open Code
"

opencode upgrade

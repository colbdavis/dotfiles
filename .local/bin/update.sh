#!/bin/sh

# Just updates arch with paru and flatpak
# By C. B. Davis

echo "(1) Update with paru
"

paru

echo "
(2) Update Flatpaks
"

flatpak update

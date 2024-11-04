#!/bin/bash

PARAMS=('-m 6 -q 70 -mt -af -progress')

if [ $# -ne 0 ]; then
	PARAMS=$@;
fi

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to that directory
cd "$DIR"

shopt -s nullglob nocaseglob extglob

echo "Starting WebP conversion..."

# Search current directory and subdirectories, but only within the starting directory
find . -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.tif" -o -iname "*.tiff" \) | while read FILE; do
    echo "Converting: $FILE"
    cwebp $PARAMS "$FILE" -o "${FILE%.*}".webp
done

echo "Conversion complete! Press any key to exit..."
read -n 1 -s
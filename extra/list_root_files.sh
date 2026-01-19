#!/bin/sh

#####################################
# PART 1 – ALL FILES, ALL ROOT DIRS #
#####################################

#OUTPUT_1="/config/extra/root_files_1.txt"
#
#: > "$OUTPUT_1"
#
#COUNT_1=0
#SIZE_1=0
#
#for dir in /*; do
#  if [ -d "$dir" ]; then
#    {
#      echo "=============================="
#      echo "Folder: $dir"
#      echo "------------------------------"
#
#      find "$dir" -type f 2>/dev/null | while read -r file; do
#        echo "$file"
#        COUNT_1=$((COUNT_1 + 1))
#        FILE_SIZE=$(stat -c %s "$file" 2>/dev/null || echo 0)
#        SIZE_1=$((SIZE_1 + FILE_SIZE))
#      done
#
#      echo
#    } >> "$OUTPUT_1"
#  fi
#done
#
#{
#  echo "=============================="
#  echo "TOTAL FILES: $COUNT_1"
#  echo "TOTAL SIZE : $SIZE_1 bytes"
#} >> "$OUTPUT_1"
#
#echo "Done. Output saved to $OUTPUT_1"

#########################################
# PART 2 – FILTERED DIRS + FILE TYPES   #
#########################################

OUTPUT_2="/config/extra/root_files_filtered_2.txt"

ROOT_DIRS="/config /backup /media"
EXTENSIONS="jpg mp4"

: > "$OUTPUT_2"

COUNT_2=0
SIZE_2=0

for dir in $ROOT_DIRS; do
  [ -d "$dir" ] || continue

  {
    echo "=============================="
    echo "Folder: $dir"
    echo "------------------------------"

    for ext in $EXTENSIONS; do
      find "$dir" -type f -name "*.$ext" 2>/dev/null | while read -r file; do
        echo "$file"
        COUNT_2=$((COUNT_2 + 1))
        FILE_SIZE=$(stat -c %s "$file" 2>/dev/null || echo 0)
        SIZE_2=$((SIZE_2 + FILE_SIZE))
      done
    done

    echo
  } >> "$OUTPUT_2"
done

{
  echo "=============================="
  echo "TOTAL FILES: $COUNT_2"
  echo "TOTAL SIZE : $SIZE_2 bytes"
} >> "$OUTPUT_2"

echo "Done. Output saved to $OUTPUT_2"

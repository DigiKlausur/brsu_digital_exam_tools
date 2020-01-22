#!/bin/bash
#title           :remove_bulk_users.sh
#description     :This script will remove users in the generated student lists
#author          :Mohammad Wasil
#contributors    :Mohammad Wasil, Alex Mitrevski
#Copyright 2019, DigiKlausur project, Bonn-Rhein-Sieg University
#==============================================================================

SESSION=""
INPUT_LIST=""
SKIP_INPUT_HEADER=1
OUTPUT_DIR=""

if [ $# -eq 0 ]
then
  echo "Usage: sh create_bulk_users.sh"
  echo " "
  echo "options:"
  echo "-h, --help                      show brief help"
  echo "-input_list  (str)              the input file of a complete student list in csv"
  echo "-skip_header (0 or 1)           whether the input file contains a header line that should be skipped (default 1)"
  exit 0
fi

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "Usage: sh create_bulk_users.sh"
      echo " "
      echo "options:"
      echo "-h, --help                      show brief help"
      echo "-input_list                     the input file of a complete student list in csv"
      echo "-skip_header (0 or 1)           whether the input file contains a header line that should be skipped (default 1)"
      exit 0
      ;;
    -input_list)
      INPUT_LIST="$2"
      shift
      shift
      ;;
    -skip_header)
      SKIP_INPUT_HEADER=$2
      shift
      shift
      ;;
    *)
      break
      ;;
  esac
done

echo "Given arguments"
echo "Input list: $INPUT_LIST"
echo "Skip input header: $SKIP_INPUT_HEADER"
echo "--------------------------------------------------"

# Check all arguments are supplied, exit otherwise

if [ -z "$INPUT_LIST" ]
  then
    echo "No student input list supplied"
    echo "use argument -h to show brief help"
  exit 0
fi

# Check input_list exists
if [ -f "$INPUT_LIST" ];
  then
    echo ""
  else
    echo "$INPUT_LIST does not exist"
    exit 0
fi

# Write header to the output list (overwrite the file if it already exists)

#Start generating users
{
    if [ $SKIP_INPUT_HEADER = 1 ];
      then
        read -r header
        echo "Skipping header $header"
    fi

    while IFS=, read -r col1 col2 col3 col4 col5 col6 col7 col8 || [ -n "$col6" ]
    do
      STUDENT_NAME="$col1"
      STUDENT_ID="$col2"
      USERNAME="$col3"
      PASSWORD="$col4"
      MATRIKEL="$col5"
      RAUM="$col6"
      PLATZ="$col7"
      DATE="$col8"
      
      echo "Removing account $USERNAME"
      userdel $USERNAME
      echo "Removing /home/$USERNAME"
      rm -rf /home/$USERNAME

    done
} < $INPUT_LIST
echo "-----------------Done---------------------"

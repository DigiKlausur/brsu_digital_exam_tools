#!/bin/bash
#title           :create_bulk_users.sh
#description     :This script will generate multiple Linux users from an input CSV file with entries for
#                :student name, FB02UID, enrollment number, room, sitting place, and exam date
#                :(one row per student)
#author          :Mohammad Wasil
#contributors    :Mohammad Wasil, Alex Mitrevski
#Copyright 2019, DigiKlausur project, Bonn-Rhein-Sieg University
#==============================================================================

COURSE_NAME=""
INPUT_LIST=""
SKIP_INPUT_HEADER=1
OUTPUT_LIST=""

if [ $# -eq 0 ]
then
  echo "Usage: sh create_bulk_users.sh"
  echo " "
  echo "options:"
  echo "-h, --help                      show brief help"
  echo "-course_name (str)              course name information to give a prefex of the username"
  echo "-input_list  (str)              the input file of a complete student list in csv"
  echo "-skip_header (0 or 1)           whether the input file contains a header line that should be skipped (default 1)"
  echo "-output_list (str)              the output file of the generated username and password in csv"
  exit 0
fi

while test $# -gt 0; do
  case "$1" in
    -h|--help)
      echo "Usage: sh create_bulk_users.sh"
      echo " "
      echo "options:"
      echo "-h, --help                      show brief help"
      echo "-course_name                    course name information to give a prefex of the username"
      echo "-input_list                     the input file of a complete student list in csv"
      echo "-skip_header (0 or 1)           whether the input file contains a header line that should be skipped (default 1)"
      echo "-output_list                    the output file of the generated username and password in csv"
      exit 0
      ;;
    -course_name)
      COURSE_NAME="$2"
      shift
      shift
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
    -output_list)
      OUTPUT_LIST="$2"
      shift
      shift
      ;;
    *)
      break
      ;;
  esac
done

echo "Given arguments"
echo "Course name: $COURSE_NAME"
echo "Input list: $INPUT_LIST"
echo "Skip input header: $SKIP_INPUT_HEADER"
echo "Output list: $OUTPUT_LIST"
echo "--------------------------------------------------"

# Check all arguments are supplied, exit otherwise
if [ -z "$COURSE_NAME" ]
  then
    echo "No course name supplied"
    echo "use argument -h to show brief help"
  exit 0
fi

if [ -z "$INPUT_LIST" ]
  then
    echo "No student input list supplied"
    echo "use argument -h to show brief help"
  exit 0
fi

if [ -z "$OUTPUT_LIST" ]
  then
    echo "No student output list supplied"
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
echo "Name,FB02UID,Username,Password,Matrikel,Raum,Platz,Date" > $OUTPUT_LIST

#Start generating users
{
    if [ $SKIP_INPUT_HEADER = 1 ];
      then
        read -r header
        echo "Skipping header $header"
    fi

    while IFS=, read -r col1 col2 col3 col4 col5 col6 || [ -n "$col6" ]
    do
      STUDENT_NAME="$col1"
      STUDENT_ID=$(echo "$col2" | xargs)     #xargs will remove whitespace
      MATRIKEL="$col3"
      RAUM="$col4"
      PLATZ="$col5"
      DATE="$col6"

      # Generate username with course_name as a prefix e.g. nn-username2s
      STUDENT_USERNAME=$(echo "$COURSE_NAME-$STUDENT_ID")

      # Create user without password
      adduser $STUDENT_USERNAME --gecos "$STUDENT_USERNAME, RoomNumber, WorkPhone, HomePhone" --disabled-password

      # Generate random password
      RAND_PASSWD=$(shuf -i 10000-100000 -n 1)
      echo "$STUDENT_USERNAME:$RAND_PASSWD" | chpasswd
      echo "$STUDENT_USERNAME: $RAND_PASSWD"

      # Restrict user to their own home dir only
      #setfacl --modify user:$STUDENT_USERNAME:0 /home/$STUDENT_USERNAME
      #echo "Student $STUDENT_USERNAME is given special permission"
      #getfacl /home/$STUDENT_USERNAME

      # You can skip this permission setup
      # by changing default mode in /etc/adduser.conf
      # DIR_MODE = 0750

      # Save username and password to csv
      echo "$STUDENT_NAME, $STUDENT_ID,$STUDENT_USERNAME, $RAND_PASSWD, $MATRIKEL, $RAUM, $PLATZ, $DATE" >> $OUTPUT_LIST
    done
} < $INPUT_LIST
echo "-----------------Done---------------------"

#title           :remove_bulk_users.sh
#description     :This script will remove multi Linux users
#author		       :Mohammad Wasil
#Copyright 2019, DigiKlausur project, Bonn-Rhein-Sieg University
#==============================================================================
for username in $(< dellist.txt)
  do
    echo "$username"
    echo "/home/$username"
    echo "Removing $username"
    userdel $username
    echo "Removing /home/$username"
    rm -rf /home/$username
  done

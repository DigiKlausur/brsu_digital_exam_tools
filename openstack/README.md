## OpenStack tools

* `osc_volume_backup.py`: a script to backup openstack volumes given a list of the volumes to back up `volume_to_backup_list.yaml`.
  This script requires [python-openstackclient](https://opendev.org/openstack/python-openstackclient).
  
  This can be run along with cronjob, for example:
  ```
  # Create a new backup every thursday
  0 1 * * 4 /home/debian/miniconda3/bin/python /home/debian/openstack_volume_backup/osc_volume_backup.py --create_backup --volume_list /home/debian/openstack_volume_backup/volume_to_backup_list.yaml --logdir /home/debian/openstack_volume_backup/logs/ 
  
  # Remove the oldest backup every Friday
  0 1 * * 5 /home/debian/miniconda3/bin/python /home/debian/openstack_volume_backup/osc_volume_backup.py --remove_backup --volume_list /home/debian/openstack_volume_backup/volume_to_backup_list.yaml --logdir /home/debian/openstack_volume_backup/logs/
  ```
  
  The script will not create a new backup if the number of backups of the corresponding volume == max_backups + 1.
  
  Also, it will not remove any backup if the number of backups == max_backups.
  
  
  Note:
  In the volume backup list file, `volume_to_backup_list.yaml`, it is required to:
  * Name the backup volume should follow: <name_of_instance>-<disk_id> e.g. `e2x-nfs-server-01-disk-01`, where `e2x-nfs-server-01`
    is the name of the instance, and `disk-01` is the disk id (mount name)
  * Provide id of the volume. You can check it via `openstack volume list`
  * Max number of backups
  

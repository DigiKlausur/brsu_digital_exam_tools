import os
import sys
import subprocess
import yaml
import pandas as pd
import numpy as np
from datetime import datetime
import time
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--create_backup', action='store_true', help='Create one new backup')
parser.add_argument('--remove_backup', action='store_true', help='Remove the oldest backup')
parser.add_argument('--volume_list', default=None, help='List of volumes to backup')
parser.add_argument('--logdir', default=None, help='Log directory to store logs and backup information')
FLAGS = parser.parse_args()

class OpenStackBackup(object):
    '''
    Perform backup on OpenStack volumes and delete old backups.
    This will call openstack client via subprocess.
    '''
    
    def __init__(self):
        self.init_logger()
    
    def init_logger(self):
        self.log = logging.getLogger()
        self.log.setLevel(logging.DEBUG)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
        consoleHandler.setFormatter(formatter)
        self.log.addHandler(consoleHandler)

    def create_backup(self, path_to_backup_list, logdir="/tmp"):
        # load volumes to backup
        with open(path_to_backup_list) as stream:
            volumes = yaml.safe_load(stream)

        current_vol_backup_path = self.get_curr_backup_list(logdir)

        # Perform backup
        for vol in volumes["volumes"]:
            vol_name = vol["name"]
            vol_id = vol["id"]
            max_backups = vol["max_backups"]
            if os.path.exists(current_vol_backup_path):
                volume_backup_df = pd.read_csv(current_vol_backup_path)
                volume_backup_list = {}
                num_of_backups = 0
                for i,backup_name in enumerate(volume_backup_df.Name):
                    if vol_name in backup_name:
                        num_of_backups += 1

                # Create a new backup if the curr numb backups does not exceed max
                self.log.info(f"Max backups: {max_backups}, curr backup: {num_of_backups}")
                if num_of_backups <= max_backups:
                    now = datetime.now()
                    current_date = now.strftime("%d.%m.%Y.%H:%M:%S")

                    new_backup_name = vol_name + "-" + current_date
                    self.log.info(f"Creating backup {new_backup_name}")
                    
                    log_backup_path = os.path.join(logdir, f'{new_backup_name}.yaml')
                    try:
                        with open(log_backup_path, 'w') as f:
                            process = subprocess.check_call(['openstack', 
                                                    'volume', 
                                                    'backup', 
                                                    'create',
                                                    '-f',
                                                    'yaml',
                                                    '--name', 
                                                    str(new_backup_name),
                                                    '--force',
                                                    str(vol_id)], stdout=f)

                        # wait for 3s until it finishes sending cmd
                        time.sleep(3)
                    except subprocess.CalledProcessError:
                        self.log.error("There an error when performing backup")

                    current_backup = None
                    if os.path.exists(log_backup_path):
                        with open(log_backup_path) as stream:
                            current_backup = yaml.safe_load(stream)

                    if current_backup:
                        if "name" in current_backup:
                            if current_backup["name"] == new_backup_name:
                                self.log.info("Backup successful...")
                        else:
                            self.log.warning(f"No backup performed: Backup name not found in {log_backup_path}")
                    else:
                        self.log.warning("Backup was not performed: No current backup file")
                else:
                    self.log.info("Current backup > max backups. Not performing backup!")
                
    def get_curr_backup_list(self, logdir):
        # update current backup list
        current_vol_backup_path = os.path.join(logdir, "current_volume_backup_list.csv")
        with open(current_vol_backup_path, 'w') as f:
            process = subprocess.Popen(['openstack', 
                                        'volume', 
                                        'backup', 
                                        'list',
                                        '-f',
                                        'csv'], stdout=f)
        # wait for 5s
        time.sleep(5)
        return current_vol_backup_path    

    def delete_backup(self, path_to_backup_list, logdir="/tmp"):
        # Delete old backup
        with open(path_to_backup_list) as stream:
            volumes = yaml.safe_load(stream)

        # get updated backup list
        current_vol_backup_path = self.get_curr_backup_list(logdir)

        if os.path.exists(current_vol_backup_path):
            volume_backup_df = pd.read_csv(current_vol_backup_path)
            volume_backup_list = {}

            for vol in volumes["volumes"]:
                vol_name = vol["name"]
                max_backups = vol["max_backups"]
                for i,backup_name in enumerate(volume_backup_df.Name):
                    if vol_name in backup_name:
                        bk_split = backup_name.split("-")
                        backup_date = bk_split[-1]
                        backup_vol_id = volume_backup_df.ID[i]
                        backup_vol_size = volume_backup_df.Size[i]

                        #print(vol_name, backup_date, backup_vol_id, backup_vol_size)

                        if vol_name not in volume_backup_list:
                            volume_backup_list[vol_name] = {}
                            volume_backup_list[vol_name]["dates"] = []
                            volume_backup_list[vol_name]["backup_vol_id"] = []
                            volume_backup_list[vol_name]["backup_date"] = []
                            volume_backup_list[vol_name]["max_backups"] = max_backups

                        date_format = "%d.%m.%Y.%H:%M:%S"
                        date_object =  datetime.strptime(backup_date, date_format)
                        volume_backup_list[vol_name]["dates"].extend([date_object])
                        volume_backup_list[vol_name]["backup_vol_id"].append(backup_vol_id)
                        volume_backup_list[vol_name]["backup_date"].append(backup_date)
                        
            # check if there is one need to be deleted.
            # if the number of backups is less than max backup number, skipp
            vol_backup_to_remove = []
            if volume_backup_list:
                for i,backup_name in enumerate(volume_backup_list.keys()):
                    if len(volume_backup_list[backup_name]["dates"]) > volume_backup_list[vol_name]["max_backups"]:
                        min_date_idx = np.argmin(volume_backup_list[backup_name]["dates"])
                        min_vol_id = volume_backup_list[backup_name]["backup_vol_id"][min_date_idx]
                        min_date = volume_backup_list[backup_name]["backup_date"][min_date_idx]
                        self.log.info(f"To remove: {backup_name}  {min_vol_id} ({min_date})")
                        vol_backup_to_remove.append(min_vol_id)
                    else:
                        self.log.info("Number of backups <= max backup limits. Nothing to remove")
            else:
                self.log.info("No existing volume backups. Nothing to remove")

            # Delete old backup
            if vol_backup_to_remove:
                for vol_to_remove in vol_backup_to_remove:
                    self.log.info(f"Removing backup volume id {vol_to_remove}")
                    process = subprocess.Popen(['openstack', 
                                                'volume', 
                                                'backup', 
                                                'delete',
                                                str(vol_to_remove)])
        else:
            self.log.error("Current backup list is not available")

if __name__ == '__main__':
  create_backup = FLAGS.create_backup
  remove_backup = FLAGS.remove_backup
  path_to_backup_list = FLAGS.volume_list
  logdir = FLAGS.logdir

  osb = OpenStackBackup()
  
  if create_backup:
      osb.log.info("Creating a new backup")
      osb.create_backup(path_to_backup_list, logdir)

  if remove_backup:
      osb.log.info("Removing the oldest backup")
      osb.delete_backup(path_to_backup_list, logdir)
    

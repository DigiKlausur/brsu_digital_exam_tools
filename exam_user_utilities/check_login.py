import os
import argparse
import yaml
import requests
import pandas as pd
import warnings
import time
import progressbar

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='', help='The jupyterhub server')
parser.add_argument('--user_list', default='', help='The list of the users in csv')
parser.add_argument('--user', default=None, help='Specify particular user (must be listed in the user_list)')

FLAGS = parser.parse_args()
SERVER = FLAGS.server
USER_LIST = FLAGS.user_list
USER = FLAGS.user

def check_login(login_url, username, password, timeout=45):
    try:
        response = requests.post(login_url, 
                            data={'username': username, 'password': password}, 
                            timeout=timeout, verify=True)
    except requests.ReadTimeout:
        print("timeout after {} seconds when trying to log in user '{}' at URL '{}'".format(timeout, username, login_url))
        return False
    
    if response.status_code != 200:
        print("failed to send POST request for user '{}' to URL '{}'".format(username, login_url))
        return False

    if response.text.find('Invalid username or password') > -1:
        return False
    
    return True

def main(server, csv_student_list, user):
    print('checking logins at server: ' + server)
    student_list = pd.read_csv(csv_student_list, encoding='UTF-8')
    login_url = os.path.join(server, 'hub', 'login?next=')
   
    if user is not None:
        if user in student_list.Username.tolist():
            idx = student_list.index[student_list['Username'] == user].tolist()
            username = student_list.Username[idx].tolist()[0]
            password = student_list.Password[idx].tolist()[0]
            password = str(password).strip()
            print(username, password)
            if check_login(login_url, username, password):
                print("login successful: '{}'".format(username))
            else:
                print("login failed: '{}'".format(username))
        else:
            print("{} is not in the list".format(user))
    else:
        bar = progressbar.ProgressBar(maxval=len(student_list), widgets=[progressbar.Bar('', ' ', ' '), '', progressbar.Percentage()])
        bar.start()
        for i in range(len(student_list)):
            bar.update(i+1)
            name = student_list.Name[i]
            fb02uid = student_list.FB02UID[i]
            username = student_list.Username[i]
            password = str(student_list.Password[i]).strip()
            
            if check_login(login_url, username, password):
                print("{}/{} login successful: '{}'".format(i,len(student_list),username))
            else:
                print("login failed: '{}'".format(username))
            
            time.sleep(3.0)

            #put 20s delay each 10 logins
            if i > 0 and i % 10 == 0:
                print("Login paused for 15s")
                time.sleep(5)
            
            if i > 0 and i % 20 == 0:
                print("Login paused for 30s")
                time.sleep(30) 

            if i > 0 and i % 60 == 0:
                print("Login paused for 60s")
                time.sleep(60) 

        bar.finish()

    print ("Login check is done")

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    main(SERVER, USER_LIST, USER)

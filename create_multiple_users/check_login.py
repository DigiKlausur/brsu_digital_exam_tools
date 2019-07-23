import os
import argparse
import yaml
import requests
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='', help='The jupyterhub server')
parser.add_argument('--user_list', default='', help='The list of the users in csv')

FLAGS = parser.parse_args()
SERVER = FLAGS.server
USER_LIST = FLAGS.user_list

def check_login(login_url, username, password, timeout=5.0):
    try:
        response = requests.post(login_url, data={'username': username, 'password': password}, timeout=timeout)
    except requests.ReadTimeout:
        print("timeout after {} seconds when trying to log in user '{}' at URL '{}'".format(timeout, username, login_url))
        return False

    if response.status_code != 200:
        print("failed to send POST request for user '{}' to URL '{}'".format(username, login_url))
        return False

    if response.text.find('Invalid username or password') > -1:
        return False

    return True

def main():
    if SERVER is '':
        print ("No jupyterhub server specified")
        return
    
    if USER_LIST is '':
        print ("No student list specified specified")
        return

    print('checking logins at server: ' + SERVER)
    student_list = pd.read_csv(USER_LIST)
    login_url = os.path.join(SERVER, 'hub', 'login?next=')
    for i in range(len(student_list)):
        username = student_list.Username[i]
        password = student_list.Password[i]
        
        if check_login(login_url, username, password):
            print("login successful: '{}'".format(username))
        else:
            print("login failed: '{}'".format(username))

    print ("Login check is done")

if __name__ == '__main__':
    main()
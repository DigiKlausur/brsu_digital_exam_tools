import os
import argparse
import requests
import pandas as pd
import warnings
import time
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--server', default='', help='The jupyterhub server')
parser.add_argument('--verify_request', default=False, help='Verify https request (default: False)')
parser.add_argument('--user_list', default='', help='The list of the users in csv')
parser.add_argument('--user', default=None, help='Specify particular user (must be listed in the user_list)')
parser.add_argument('--range', type=int, nargs='+', default=None, help='A list containing min and max: e.g. [0,100]')

FLAGS = parser.parse_args()
SERVER = FLAGS.server
USER_LIST = FLAGS.user_list
USER = FLAGS.user
RANGE = FLAGS.range

def check_login(login_url, username, password, timeout=45):
    try:
        response = requests.post(login_url, 
                            data={'username': username, 'password': password}, 
                            timeout=timeout, verify=False)
    except requests.ReadTimeout:
        print("timeout after {} seconds when trying to log in user '{}' at URL '{}'".format(timeout, username, login_url))
        return False
    
    if response.status_code != 200:
        print("failed to send POST request for user '{}' to URL '{}'".format(username, login_url))
        return False

    if response.text.find('Invalid username or password') > -1:
        return False
    
    return True

def main(server, csv_student_list, user, range_number):
    print('checking logins at server: ' + server)
    student_list = pd.read_csv(csv_student_list, encoding='UTF-8')
    login_url = os.path.join(server, 'hub', 'login?next=')
    start_time = time.time()
    print("range number: ", range_number)

    # update student list, check whether range is given
    if range_number is not None:
        student_list = student_list[range_number[0],
                                    range_number[1]]
    success_login = []
    fail_login = []
    if user is not None:
        if user in student_list.Username.astype(str).values.tolist():
            idx = student_list.index[student_list['Username'].astype(str) == user].tolist()
            username = student_list.Username[idx].tolist()[0]
            password = student_list.Password[idx].tolist()[0]
            password = str(password).strip()
            print(username, password)
            if check_login(login_url, username, password):
                success_login.append(username)
            else:
                fail_login.append(username)
        else:
            print("{} is not in the list".format(user))
    else:
        for i in tqdm(range(len(student_list))):
            fb02uid = student_list.FB02UID[i]
            username = student_list.Username[i]
            password = str(student_list.Password[i]).strip()

            if "Url" in student_list.columns:
                login_url = os.path.join(student_list.Url[i], 'hub', 'login?next=')

            if check_login(login_url, username, password):
                # print("{}/{} login successful: '{}'".format(i+1,range_number[1],username))
                success_login.append(username)
            else:
                # print("login failed: '{}'".format(username))
                fail_login.append(username)

            #put 15s delay each 10 logins
            if i > 0 and i % 10 == 0:
                # print("Login paused for 15s")
                time.sleep(15)

    finish_time = time.time()
    print("Login check is done")
    print("Success: ", len(success_login), success_login)
    print("Fail: ", len(fail_login), fail_login)
    print("Time: {} minutes".format(int((finish_time-start_time) / 60)))

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    main(SERVER, USER_LIST, USER, RANGE)

import grp
import pwd
import os
import shutil
import stat
import argparse
from distutils import dir_util

parser = argparse.ArgumentParser()
parser.add_argument('--assignment_id', default='', help='Assignment id')
parser.add_argument('--student_id', default='', help='Student id')
#parser.add_argument('--student_group', default='mrc-student-group', help='Student group name')
#parser.add_argument('--student_fb_dir', default='feedback', help='Student feeback directory')
parser.add_argument('--feedback_dir', default='', help='Feeback directory root')
parser.add_argument('--from_nbgrader', action='store_true', help='Is the feedback directory nbgrader-like structured? Default is True')
parser.add_argument('--course_dir', default='', help='Course directory root if from nbgrader is enabled')

FLAGS = parser.parse_args()
ASSIGNMENT_ID = FLAGS.assignment_id
STUDENT_ID = FLAGS.student_id
FEEDBACK_DIR = FLAGS.feedback_dir
FROM_NBGRADER = FLAGS.from_nbgrader
COURSE_DIR = FLAGS.course_dir
#STUDENT_GROUP = FLAGS.student_group
#STUDENT_FB_DIR = FLAGS.student_fb_dir

course_root = './'
submitted_dir = "submitted"
autograded_dir = "autograded"
release_dir = "release"
feedback_dir = "feedback"

# Check whether directory existance for submitted, autograded and feedback
# e.g. check if all student submitted assigments: check_dir_exist(submitted_dir, assignment_id)
# e.g. check if all student autograded assigments: check_dir_exist(autograded_dir, assignment_id)
def check_dir_exist(directory, assignment_id):
    print ("Checking all submissions...")
    for student in group.gr_mem:    
        if not os.path.exists(os.path.join(course_root, directory, student, assignment_id)):
            print (directory,"or", assignment_id, " does not exist")
            return False
        else:
            print (os.path.join(course_root, directory, student, assignment_id), " exist...")
            return True

def set_permissions(path, uid, gid):
    '''
    Set permission of a directory to read only
    '''
    os.chown(path, uid, gid)
    if os.path.isdir(path):
        os.chmod(path, stat.S_IRUSR | stat.S_IRGRP | stat.S_IXUSR | stat.S_IXGRP)
    else:
        os.chmod(path, stat.S_IRUSR | stat.S_IRGRP)
        
# Case 2: if we put the feedback to a single directory
def check_and_release_feedback_from_directory(feedback_root, student, assignment_id, target_feedback_dir='feedback'):
    if os.path.exists(os.path.join(feedback_root, student, assignment_id)):
        assignment_fb_dir = os.path.join(feedback_root, student, assignment_id)
        student_fb_dir =  os.path.join("/home", student, target_feedback_dir, assignment_id)
        
        # copy feedback to /home/student/feedback/assignment_id
        dir_util.copy_tree(assignment_fb_dir,student_fb_dir)
        
        print ("src: ",assignment_fb_dir)
        print ("des: ",student_fb_dir)
        print ("======Done returning feedback to : {} ======".format(student_fb_dir))
        
        if os.path.exists(student_fb_dir):
            print ("Setting feedback permission to read only")
            pwinfo = pwd.getpwnam(student)
            uid = pwinfo.pw_uid
            gid = pwinfo.pw_gid
            set_permissions(student_fb_dir, uid, gid)
            print ("Setting permission: ", student_fb_dir)
            for dirname, dirnames, filenames in os.walk(student_fb_dir):
                for f in (dirnames + filenames):
                    path = os.path.join(dirname, f)
                    set_permissions(student_fb_dir, uid, gid)
                    print ("Setting permission: ", path)
            
            return 1
        else:
            print ("Failed to find the target feedback")
            return 0
    else:
        print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print ("Feedback not available for student: ", student, ", assignment: ", assignment_id)
        print ("Do <nbgrader feedback assignment_id> in terminal and check if the student submitted the assignment")
        print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        return 0
    

# If student_id is not specified, release feedback to all students
def release_feedback(feedback_root, assignment_id, student_id, student_uname_list):  
    if student_id == "":
        count = 0
        for student in student_uname_list:
            count += check_and_release_feedback_from_directory(feedback_root, student, assignment_id)
            
        print ("==============================================")
        print ("Done releasing feedback for", count)
    else:
        # release fb to student_id only
        check_and_release_feedback_from_directory(feedback_root, student, assignment_id)
        
def main():
    if ASSIGNMENT_ID == "":
	    print ("Please specify assignment id")
	    return
    
    if STUDENT_ID == "":
	    print ("No student_id specified, will be applied to all students if the feedbacks exist in the course dir")
            
    if FROM_NBGRADER:
        if COURSE_DIR == "":
            print ("Please specify the COURSE directory")
            return
        else:
            print ("Using nbgrader feedback root style")
            feedback_root = os.path.join(COURSE_DIR,feedback_dir)
    else:
        if FEEDBACK_DIR == "":
            print ("Please specify the feedback directory")
            return
        else:
            print ("Using specified feedback dir")
            feedback_root = FEEDBACK_DIR
    
    if not os.path.exists(feedback_root):
        print ("Feedback directory does not exist")
        return
    
    student_uname_list = os.listdir(feedback_root)
    release_feedback(feedback_root, ASSIGNMENT_ID, STUDENT_ID, student_uname_list)
    
if __name__ == '__main__':
    main()    

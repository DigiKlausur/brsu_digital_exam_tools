This directory contains codes for generating bulk Linux users, jupyterhub login verification and student id card generation. </br>
* Requirements
  * A student list in a csv file where the columns of the list should contain the following (see example: exam_complete_list.csv)
    * Name
    * FB02UID (i.e. mwasil2s)
    * Matrikel nummer
    * Room number
    * Platz
    * Date <br>
  Note: This list may contain a *single-line* header

| Name        | FB02UID | Matrikelnummer | Room | Sitting place |  Exam date |
|-------------|---------|----------------|------|---------------|------------|
| Test User 0 | test02s |      012345    | C175 |       0       | 22.03.2019 |
| Test User 1 | test12s |      123456    | C175 |       1       | 22.03.2019 |
| Test User 2 | test22s |      234567    | C175 |       2       | 22.03.2019 |
| Test User 3 | test32s |      345678    | C175 |       3       | 22.03.2019 |

* Linux user generation
  * Arguments required
    * course_name: the abbreviation of the course name e.g. nn for a neural network course. This username prefix helps us to differentiate among courses.
    * input_list: the list of students registered for the exam and the list should follow the structure as in point one (e.g. exam_complete_list.csv).
    * skip_header (0 or 1): whether the input file contains a header line that should be skipped (default 1)
    * output_list: the generated list with the username and password for each student (e.g. exam_complete_list_output.csv).
  * Start creating bulk linux users
    ```
    sudo bash create_bulk_users.sh -course_name wus -input_list examples/exam_complete_list.csv -output_list examples/exam_complete_list_output.csv -skip_header 1
    ```
  * Example of the generated list

| Name        | FB02UID | Username    | Password | Matrikel | Raum | Platz | Date       |
|-------------|---------|-------------|----------|----------|------|-------|------------|
| Test User 0 | test02s | wus-test02s | 84392    | 012345   | C175 | 0     | 22.03.2019 |
| Test User 1 | test12s | wus-test12s | 22261    | 012345   | C175 | 1     | 22.03.2019 |
| Test User 2 | test22s | wus-test22s | 63945    | 012345   | C175 | 2     | 22.03.2019 |
| Test User 3 | test32s | wus-test32s | 57806    | 012345   | C175 | 3     | 22.03.2019 |

* Add generated users to whitelist of the jupyterhub config
  * Load the generated user list to the jupyterhub_config.py using pandas
    ```
    import pandas as pd
    whitelist = {'user2m','admin2m'} #default whitelist
    students_list_path = 'examples/exam_complete_list_output.csv'
    user_pd = pd.read_csv(students_list_path)
    for username in user_pd.Username:
        whitelist.add(username)
    c.Authenticator.whitelist = whitelist
    ```
* Students login verification
  * Once the student username has been added to jupyterhub config, we need to verify them. Run the following code to verify them automatically once the jupyterhub is running.
  * Arguments:
    * server: the jupyterhub server e.g. http://localhost:7777
    * user_list: the list of users generated from automatic user creation
  ```
  python check_login --server=http://localhost:7777 --user_list=examples/exam_complete_list_output.csv
  ```
* Exam sheet generation
  * Once we have the list of users with their password and verified the user login on the jupyterhub server, we can generate a pdf file containing their login access. This will be the id of the student and will be handed to students by the Prüfung Aufsicht or invigilator.
  * The student id card also contains the hashcode which will be written by the student once they submitted their work and the timestamp
  * Arguments:
    * csv_file: a csv file containing a list of students' information
    * pdf_file: the path to the generated pdf file
    * course name: the name of the course
  ```
  python3 generate_student_exam_sheets.py -i exam_user_utilities/examples/exam_complete_list_output.csv -o exam_user_utilities/examples/exam_complete_list_output.csv -c 'My awesome course' -s 'Sommersemester 2019'
  ```
  * The sample of the generated exam sheet

![test02s_user_id](https://github.com/DigiKlausur/brsu_digital_exam_tools/blob/master/exam_user_utilities/figures/exam_sheet_sample.png)

* Removing bulk user
  * Remove user account and their home directory from the server (**sudo** required)
    ```
    bash remove_bulk_users.sh -input_list examples/exam_complete_list.csv -output_list -skip_header 1
    ```
      
  

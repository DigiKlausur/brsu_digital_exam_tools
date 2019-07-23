This directory contains codes for generating bulk Linux users, jupyterhub login verification and student id card generation. </br>
* Requirements
  * A student list in a csv file where the columns of the list should contain the following (see example: exam_complete_list.csv)
    * Name
    * FB02UID (i.e. mwasil2s)
    * Matrikel nummer
    * Room number
    * Platz
    * Date
  Note: this list should not contain a header

| Test User 0 | test02s | 012345 | C175 | 0 | 22.03.2019 |
|-------------|---------|--------|------|---|------------|
| Test User 1 | test12s | 012345 | C175 | 1 | 22.03.2019 |
| Test User 2 | test22s | 012345 | C175 | 2 | 22.03.2019 |
| Test User 3 | test32s | 012345 | C175 | 3 | 22.03.2019 |

* Linux user generation
  * Arguments required
    * course_name : the abbreviation of the course name e.g. nn for a neural network course. This username prefix helps us to differentiate between courses.
    * input_list : the list of students registered for the exam and the list should follow the structure as in point one (e.g. exam_complete_list.csv).
    * output_list : the generated list with the username and password for each student (e.g. exam_complete_list_output.csv).
  * Start creating bulk linux users
    ```
    sudo bash create_bulk_users.sh -course_name wus -input_list samples/exam_complete_list.csv -output_list samples/exam_complete_list_output.csv
    ```
  * Example of the generated list

| Name        | FB02UID | Username    | Password | Matrikel | Raum | Platz | Date       |
|-------------|---------|-------------|----------|----------|------|-------|------------|
| Test User 0 | test02s | wus-test02s | 84392    | 012345   | C175 | 0     | 22.03.2019 |
| Test User 1 | test12s | wus-test12s | 22261    | 012345   | C175 | 1     | 22.03.2019 |
| Test User 2 | test22s | wus-test22s | 63945    | 012345   | C175 | 2     | 22.03.2019 |
| Test User 3 | test32s | wus-test32s | 57806    | 012345   | C175 | 3     | 22.03.2019 |

* Add generated users to jupyterhub config
  ![jupyterhub config whitelist](https://github.com/DigiKlausur/brsu_digital_exam_tools/tree/master/create_multiple_users/figures/jupyterhub_config_sample.png)
* Students login verification
  * Once the student username has been added to jupyterhub config, we need to verify them. Run the following code to verify them automatically once the jupyterhub is running.
  * Arguments:
    * server: the jupyterhub server e.g. http://localhost:7777
    * user_list: the list of users generated from automatic user creation 
  ```
  pyrhon check_login --server=http://localhost:7777 --user_list=samples/exam_complete_list_output.csv
  ```
* Student id card generation
  * Once we have the list of users with their password and verified the user login on the jupyterhub server, we can generate a pdf file containing their login access. This will be the id of the student and will be handed to students by the Prüfung Aufsicht or invigilator.
  * Arguments:
    * csv_file: a csv file containing a list of students' information
    * pdf_file: the path to the generated pdf file
  ```
  python convert_student_list_to_pdf.py --csv_file=samples/exam_complete_list_output.csv --pdf_file=samples/exam_complete_list_output.pdf
  ```
  * The sample of the generated student id cards
  ![test02s_user_id](https://github.com/DigiKlausur/brsu_digital_exam_tools/tree/master/create_multiple_users/figures/test02s_user_id.png)
* Removing bulk user
  * Create a dellist containing usernames to delete
  * run remove_bulk_users.bash with sudo
    * sudo bash remove_bulk_users.bash

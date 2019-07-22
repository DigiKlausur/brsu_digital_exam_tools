This repository contains codes for generating bulk Linux users, jupyterhub login verification and student id card generation. </br>
* Requirements
  * A student list in a csv file where the columns of the list should contain the following (see example: exam_complete_list.csv)
    * Name
    * FB02UID (i.e. mwasil2s)
    * Matrikel nummer
    * Room number
    * Platz
    * Date
    Note: this list should not contain a header

* Linux user generation
  * Arguments required
    * course_name : the abbreviation of the course name e.g. nn for a neural network course. This username prefix helps us to differentiate between courses.
    * input_list : the list of students registered for the exam and the list should follow the structure as in point one (e.g. exam_complete_list.csv).
    * output_list : the generated list with the username and password for each student (e.g. exam_complete_list_output.csv).
  * Start creating bulk linux users
    ```
    sudo bash create_bulk_users.sh -course_name wus -input_list exam_complete_list.csv -output_list exam_complete_list_output.csv
    ```

* Add generated users to jupyterhub config
* Students login verification
  * Once the student username has been added to jupyterhub config, we need to verify them. Run the following code to verify them automatically once the jupyterhub is running.
  ```
  ```
* Student id card generation
  * Once we have the list of users with their password, we can generate a pdf file containing their login access. This will be the id of the student and will be handed to students by the Prüfung Aufsicht or invigilator.
  * Arguments:
    * csv_file: a csv file containing a list of students' information
    * pdf_file: the path to the generated pdf file
  ```
  python convert_student_list_to_pdf.py --csv_file=./exam_complete_list_output.csv --pdf_file=exam_complete_list_output.pdf
  ```
* Removing bulk user
  * Create a dellist containing usernames to delete
  * run remove_bulk_users.bash with sudo
    * sudo bash remove_bulk_users.bash

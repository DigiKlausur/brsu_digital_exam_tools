"""
@author: Mohammad Wasil
@contributors: Mohammad Wasil, Alex Mitrevski
@email: mwasil@outlook.co.id

Copyright 2019, DigiKlausur project, Bonn-Rhein-Sieg University

Generates a PDF file with exam sheets for all students.
The PDF file is generated using data from csv_student_list_file,
whose header is given as

    Name,FB02UID,Username,Password,Matrikel,Raum,Platz,Date

and has a separate entry for each student.
Each row in the list is converted to a single pdf page; Thus, the number of pages
of the output file is the same as the number of rows in the list (i.e. same as
the number of students).
"""

from typing import Sequence
import os
import pandas as pd
import numpy as np
import six
import imageio
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import argparse

def generate_exam_sheet(data: pd.core.frame.DataFrame,
                        info:pd.core.frame.DataFrame,
                        course_name: str=None,
                        semester: str =None,
                        col_width: float=9.5,
                        row_height: float=6.925,
                        font_size: float=28,
                        header_color: str='#dddddd',
                        row_colors: Sequence[str]=['#f1f1f2', 'w'],
                        edge_color: str='w',
                        bbox: Sequence[float]=[0., 0., 0.9, 1.],
                        header_columns: int=0,
                        axes: Sequence=None,
                        **kwargs) -> matplotlib.figure.Figure:
    '''Returns a matplotlib figure that displays an exam sheet.
    The sheet includes:
        * the university logo on top,
        * the name of the course and the semester in which the exam is conducted
        * the student name and login information
        * information about the date and location of the exam for the student
        * an empty space for the exam submission hash code
        * an empty space for the exam submission time stamp
    '''
    if axes is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, axes = plt.subplots(6,1, figsize=size)
        for i in range(6):
            axes[i].axis('off')

    script_path = os.path.dirname(os.path.abspath(__file__))

    # we add the university logo on top of the exam sheet
    axes[0].imshow(imageio.imread(os.path.join(script_path, 'figures/hbrs_logo.png')))

    tables = dict()
    tables['course'] = axes[1].table(cellText=[[semester]],
                                     bbox=bbox, colLabels=[course_name],
                                     cellLoc='center', **kwargs)
    tables['user_data'] = axes[2].table(cellText=data.values, bbox=bbox,
                                        colLabels=data.columns,
                                        cellLoc='center', **kwargs)
    tables['exam_info'] = axes[3].table(cellText=info.values, bbox=bbox,
                                        colLabels=info.columns,
                                        cellLoc='center', **kwargs)
    tables['hashcode'] = axes[4].table(cellText=[['']], bbox=bbox,
                                       colLabels=[u'Hashcode'],
                                       cellLoc='center', **kwargs)
    tables['timestamp'] = axes[5].table(cellText=[['']], bbox=bbox,
                                        colLabels=[u'Timestamp'],
                                        cellLoc='center', **kwargs)

    for table_name in tables:
        tables[table_name].auto_set_font_size(False)
        tables[table_name].set_fontsize(font_size)

    for table_name in tables:
        for k, cell in six.iteritems(tables[table_name]._cells):
            cell.set_edgecolor(edge_color)
            if k[0] == 0 or k[1] < header_columns:
                cell.set_text_props(weight='bold', color='black')
                cell.set_facecolor(header_color)
    return fig

def generate_exam_sheets(course_name: str, semester: str,
                         csv_student_list_file: str,
                         exam_sheet_file: str) -> None:
    '''Generates a PDF file (saved as exam_sheet_file)
    with exam sheets for each student.

    The PDF file is generated using data from csv_student_list_file,
    whose header is given as

        Name,FB02UID,Username,Password,Matrikel,Raum,Platz,Date

    and has a separate entry for each student.

    Keyword arguments:
    course_name: str -- name of the course
    semester: str -- semester of the exam
    csv_student_list_file: str -- name of a CSV file containing
                                  student data
    exam_sheet_file: str -- name of the output PDF file
                            with the exam sheets

    '''
    student_list = pd.read_csv(csv_student_list_file)
    pp = PdfPages(exam_sheet_file)
    for i in range(len(student_list)):
        print('Generating exam sheet {0}/{1}'.format(i+1, len(student_list)))

        name = student_list.Name[i]
        fb02uid = student_list.FB02UID[i]
        username = student_list.Username[i]
        password = student_list.Password[i]

        matrikelnummer = student_list.Matrikel[i]
        raum = student_list.Raum[i]
        platz = student_list.Platz[i]
        date = student_list.Date[i]

        session = None
        if 'Session' in student_list.index:
            session = student_list.Session[i]

        data_df = pd.DataFrame([[name,fb02uid,username,password]],
                               columns=['Name', 'FB02UID', 'Username', 'Password'])

        room_str = '{0} ({1})'.format(raum, str(session)) if session else raum
        info_df = pd.DataFrame([[matrikelnummer, room_str, platz,date]],
                               columns=['Matrikelnummer', 'Raum', 'Platz', 'Datum'])

        pp.savefig(generate_exam_sheet(data_df, info_df,
                                       course_name=course_name,
                                       semester=semester))
    pp.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', default='', help='Input CSV file with student data')
    parser.add_argument('-o', '--output_file', default='', help='Output PDF file with all exam sheets')
    parser.add_argument('-c', '--course', default='', help='Name of the course')
    parser.add_argument('-s', '--semester', default='', help='Semester of the exam')

    args = parser.parse_args()
    csv_student_list_file = args.input_file
    exam_sheet_file = args.output_file
    course_name = args.course
    semester = args.semester

    if not csv_student_list_file:
        raise ValueError("No CSV input file specified")

    if not exam_sheet_file:
        raise ValueError("No PDF output file specified")

    if not course_name:
        raise ValueError('course has to be set to a value')

    if not semester:
        raise ValueError('semester has to be set to a value')

    print('Generating exam sheets...')
    generate_exam_sheets(course_name, semester,
                         csv_student_list_file,
                         exam_sheet_file)
    print('Exam sheets saved in {0}'.format(exam_sheet_file))

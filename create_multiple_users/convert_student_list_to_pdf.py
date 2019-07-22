"""
@author: Mohammad Wasil
@email: mwasil@outlook.co.id

Copyright 2019, DigiKlausur project, Bonn-Rhein-Sieg University

A converter from a csv list to a pdf. 
Each row in the list is converted to a single pdf page. 
Thus the number of page of the output is the same as the number of rows in the list. 
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import six
from matplotlib.backends.backend_pdf import PdfPages
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--csv_file', default='', help='CSV input file')
parser.add_argument('--pdf_file', default='', help='PDF output file')

FLAGS = parser.parse_args()
CSV_STUDENT_LIST = FLAGS.csv_file
PDF_STUDENT_LIST = FLAGS.pdf_file

def render_mpl_table(header, data, col_width=9.5, row_height=6.925, font_size=28,
                     header_color='#bdbdbd', row_colors=['#f1f1f2', 'w'], edge_color='w',
                     bbox=[0.0,0.0, 0.9, 1], header_columns=0, ax=None, **kwargs):
    """
    Returns a rendered pdf page
    data: the header of the table
    info: the student information such as their username and password

    Note: the size of data and info should be the same
    """
    if ax is None:
        size = (np.array(header.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(5,1, figsize=size)
        ax[0].axis('off')
        ax[1].axis('off')
        ax[2].axis('off')
        ax[3].axis('off')
        ax[4].axis('off')
      
    mpl_table0 = ax[0].table(cellText=header.values, bbox=bbox, colLabels=data.columns, **kwargs)  
    mpl_table0.auto_set_font_size(False)
    mpl_table0.set_fontsize(font_size)
    
    mpl_table1 = ax[1].table(cellText=header.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table1.auto_set_font_size(False)
    mpl_table1.set_fontsize(font_size)
    
    mpl_table1 = ax[2].table(cellText=[['']], bbox=bbox, colLabels=[u'Hashcode'], **kwargs)
    mpl_table1.auto_set_font_size(False)
    mpl_table1.set_fontsize(font_size)
    
    mpl_table2 = ax[3].table(cellText=[['']], bbox=bbox, colLabels=[u'Timestamp'], **kwargs)
    mpl_table2.auto_set_font_size(False)
    mpl_table2.set_fontsize(font_size)
    
    mpl_table2 = ax[4].table(cellText=[[u'Hochschule Bonn-Rhein-Sieg']], bbox=bbox, 
                             colLabels=[u'Wahrscheinlichkeitstheorie und Statistik WS 18/19'], 
                             cellLoc='center')
    mpl_table2.auto_set_font_size(False)
    mpl_table2.set_fontsize(font_size)
    
    for k, cell in  six.iteritems(mpl_table0._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='black')
            cell.set_facecolor(header_color)
        else:
            cell.set_text_props(weight='bold', color='black')
            
    return fig

def main():
    if CSV_STUDENT_LIST is '':
        print ("No csv input specified")
        return
    else:
        pp = PdfPages(PDF_STUDENT_LIST)

    if PDF_STUDENT_LIST is '':
        print ("No pdf output specified")
        return
    else:
        student_list = pd.read_csv(CSV_STUDENT_LIST)
    
    for i in range(len(student_list)):
        name = student_list.Name[i]
        fb02uid = student_list.FB02UID[i]
        username = student_list.Username[i]
        password = student_list.Password[i]
        
        matrikel = student_list.Matrikel[i]
        raum = student_list.Raum[i]
        platz = student_list.Platz[i]
        date = student_list.Date[i]
        #session = student_list.Session[i]
        session = 1

        data_df = pd.DataFrame([[name,fb02uid,username,password]], 
                  columns=['Name','FB02UID', 'Username','Password'])
        raum_and_session = str(raum)+"("+str(session)+")"
        info_df = pd.DataFrame([[matrikel,raum,platz,date]], 
                  columns=['Matrikel','Raum', 'Platz','Date'])

        pp.savefig(render_mpl_table(data_df, info_df))
    pp.close()

if __name__ == '__main__':
    main()
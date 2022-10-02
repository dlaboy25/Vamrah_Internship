import fitz
import pandas as pd 
from operator import itemgetter
import camelot.io as camelot
import tkinter

class Annotation:

    def __init__(self, type, coords, data):
        self.tl_x = coords[0]
        self.tl_y = coords[1]
        self.data_type = "annotation"
        self.type = type
        self.x0 = coords[0]
        self.y0 = coords[1]
        self.x1 = coords[2]
        self.y1 = coords[3]
        self.data = data

    def __repr__(self):
        return ("Type: " + self.type + ", x0,y0: " + "(" + str(self.x0) + "," + str(self.y0) + "), "\
            "x1,y1: " + "(" + str(self.x1) + "," + str(self.y1) + ")" + ", Data: " + str(self.data))


class Table: 
    
    def __init__(self, coords, data):
        self.tl_x = coords[0]
        self.tl_y = 792 - coords[3]
        self.data_type = "table"
        self.x0 = coords[0]
        self.y0 = 792 - coords[3]
        self.x1 = coords[2]
        self.y1 = 792 - coords[1]
        self.height = len(data[0])
        self.width = len(data)              #order first by y0 coordinate. order from top to bottom. then use x0 coordinate to order from left to right
        self.data = data                   

    def __repr__(self):
        return ("Table Height: " + str(self.height) + ", Table Width: " + str(self.width) + ", x0,y0: " + "(" + str(self.x0) + "," + str(self.y0) + "), "\
            "x1,y1: " + "(" + str(self.x1) + "," + str(self.y1) + ")")

class Header:

    def __init__(self, coords, data):
        self.data_type = "header"
        self.num_blocks = len(coords)
        self.data = data
        first = True
        p = eval(coords[0])
        self.tl_x = p[0]
        self.tl_y = p[1]
        for i in range(len(coords)):
            if first:
                s = eval(coords[0])
                self.x0 = [s[0]]
                self.y0 = [s[1]]
                self.x1 = [s[2]]
                self.y1 = [s[3]]
                first = False
            else:
                p = eval(coords[i])
                self.x0 += [p[0]]
                self.y0 += [p[1]]
                self.x1 += [p[2]]
                self.y1 += [p[3]]
            

    def __repr__(self):
        return ("Header Lines: " + str(self.num_blocks) + ", x0,y0: " + "(" + str(self.x0) + "," + str(self.y0) + "), "\
            "x1,y1: " + "(" + str(self.x1) + "," + str(self.y1) + ")" + "Data: " + str(self.data))
 

class Paragraph:
    
    def __init__(self, coords, data):
        self.data_type = "para"
        self.num_blocks = len(coords)
        self.data = data
        first = True
        p = eval(coords[0])
        self.tl_x = p[0]
        self.tl_y = p[1]
        for i in range(len(coords)):
            if first:
                s = eval(coords[0])
                self.x0 = [s[0]]
                self.y0 = [s[1]]
                self.x1 = [s[2]]
                self.y1 = [s[3]]
                first = False
            else:
                p = eval(coords[i])
                self.x0 += [p[0]]
                self.y0 += [p[1]]
                self.x1 += [p[2]]
                self.y1 += [p[3]]

    def __repr__(self):
        return ("Paragraph Lines: " + str(self.num_blocks) + ", x0,y0: " + "(" + str(self.x0) + "," + str(self.y0) + "), "\
            "x1,y1: " + "(" + str(self.x1) + "," + str(self.y1) + ", Data: " + str(self.data))

def create_annots(annot_list):
    annot_objects = []
    for annot in annot_list:
        temp = Annotation(annot[0], annot[1], annot[2])
        annot_objects.append(temp)
    return annot_objects

def create_tables(table_list):
    table_objects = []
    for table in table_list:
        temp = Table(table[1],table[2])
        table_objects.append(temp)
    return table_objects

def create_headers(header_list):    
    header_objects = []
    for header in header_list:
        temp = Header(header[1],header[2])
        header_objects.append(temp)
    return header_objects

def create_paras(para_list):    
    para_objects = []
    for para in para_list:
        temp = Paragraph(para[1],para[2])
        para_objects.append(temp)
    return para_objects

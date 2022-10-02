import fitz
import pandas as pd 
from operator import itemgetter
import camelot.io as camelot
import tkinter
from classes import* 
# after all functions are defined, create new function that calls all the others and organizes them. Define in PDF class.


class PDF:
    
    def __init__(self,pdf):
        self.doc = fitz.open(pdf)
        self.tables = camelot.read_pdf(pdf)

    def make_text(self,words): #helper function
        line_dict = {} 
        words.sort(key=lambda w: w[0])
        for w in words:  
            y1 = round(w[3], 1)  
            word = w[4] 
            line = line_dict.get(y1, [])  
            line.append(word)  
            line_dict[y1] = line  
        lines = list(line_dict.items())
        lines.sort()  
        return "n".join([" ".join(line[1]) for line in lines])
    
    def annot_extract(self):
        for page in self.doc:
            words = page.get_text("words")
            first_annot = []
            rec = page.first_annot.rect
            rec.x0 -= .6
            rec.y0 -= .6
            rec.x1 += .5
            rec.y1 += .5
            mywords = [w for w in words if fitz.Rect(w[:4]) in rec]
            all_annots = []
            for annot in page.annots():
                if annot!=None:
                    temp = []
                    rec = annot.rect
                    rec.x0 -= .6
                    rec.y0 -= .6
                    rec.x1 += .5
                    rec.y1 += .5
                    mywords = [w for w in words if fitz.Rect(w[:4]) in rec]
                    ann = self.make_text(mywords)
                    temp.append(annot.type[1])
                    temp.append(rec)
                    temp.append(ann)
                    all_annots.append(temp)
        return all_annots

    def table_extract(self):
        if len(self.tables) == 0:
            print('No tables found')
            return False
        all_tables = []
        count = 0
        num_table = 1
        for table in self.tables:
            table_dia = table.df
            #print(table.df.to_numpy())
            #try to restructure function to work around table.df instead of creating arrays.
            num_cols = 0
            for x in table_dia:
                num_cols += 1
            temp_table = [None] * 3
            temp_table[0] = "table " + str(num_table)
            num_table += 1
            temp_table[1] = self.tables[count]._bbox
            temp2 = []
            for i in range(num_cols):
                temp = []
                for l in table_dia[i]:
                    temp.append(l)
                temp2.append(temp)
            temp_table[2] = temp2
            all_tables.append(temp_table)
            count += 1
        return all_tables

    def header_para(self):
        styles = {}
        font_counts = {}
        granularity = False
        for page in self.doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                    #print(b['bbox'])
                if b['type'] == 0:  # block contains text
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if granularity:
                                identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'],)
                                styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                  'color': s['color']}
                            else:
                                identifier = "{0}".format(s['size'])
                                styles[identifier] = {'size': s['size'], 'font': s['font']}

                            font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

        font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

        if len(font_counts) < 1:
            raise ValueError("Zero discriminating fonts found!")

        '--------------------------------------------------------------------'
        p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
        p_size = p_style['size']  # get the paragraph's size

        # sorting the font sizes high to low, so that we can append the right integer to each tag 
        font_sizes = []
        for (font_size, count) in font_counts:
            font_sizes.append(float(font_size))
        font_sizes.sort(reverse=True)

            # aggregating the tags for each font size
        size_tag = {}
        for size in font_sizes:
            
            if size == p_size:
                size_tag[size] = '<p>'
            if size > p_size:
                size_tag[size] = '<h>'
            elif size < p_size:
                size_tag[size] = '<s>'
        '--------------------------------------------------------------------'
        header_para = []  # list with headers and paragraphs
        first = True  # boolean operator for first header
        previous_s = {}  # previous span
        same = False

        for page in self.doc:
                blocks = page.get_text("dict")["blocks"]
                for b in blocks:  # iterate through the text blocks
                    if b['type'] == 0:  # this block contains text

                # REMEMBER: multiple fonts and sizes are possible IN one block

                        block_string = ""  # text found in block
                        #rect = b['bbox'] # store coordinates of block in rect
                        for l in b["lines"]:  # iterate through the text lines
                            for s in l["spans"]:  # iterate through the text spans
                                rect = s['bbox']
                                if s['text'].strip():  # removing whitespaces:
                                    if first:
                                        previous_s = s
                                        first = False
                                        block_string = size_tag[s['size']] + s['text'] #+ str(rect) #concatonate rect to block_string
                                    else:
                                        if s['size'] == previous_s['size']:
                                            same = True
                                            if block_string and all((c == "|") for c in block_string): 
                                        # block_string only contains pipes
                                                block_string = size_tag[s['size']] + s['text']
                                        
                                            if block_string == "":
                                        # new block has started, so append size tag
                                                block_string = size_tag[s['size']] + s['text']
                                            else:  # in the same block, so concatenate strings
                                                block_string += " " + s['text'] 

                                        else:
                                            header_para.append(block_string)
                                            block_string = size_tag[s['size']] + s['text']

                                #block_string += str(rect) #concatonate rect to block_string
                                        previous_s = s
                                

                            # new block started, indicating with a pipe
                            block_string += "|"
                            block_string += str(rect) #concatonate rect to block_string
                    
                        header_para.append(block_string)
        return header_para
        '--------------------------------------------------------------------'

    def header_extract(self):
        last_close = None
        all_headers = []
        for header in self.header_para(): #iterate through lines in header_para
            indv_header = [None,[None],[None]]
            count = 0 
            if '<h>' in header: #if line is a header
                indv_header[0] = "header"

                for i in range(3,len(header)): #iterate through header string starting after decoration
                    if header[i] == ")": #figure out index where first set of rect coords ends
                        last_close = i

                    if header[i] == "|" and header[i+1] == "(": #find index of start of coords
        
                        count += 1 #keeps track of how many lines are in the header

                        if count == 1:    #if its the first header
                            text = header[3:i - 1]    #store text
                            indv_header[2] = [text] #append to main list
                            for l in range(i,len(header)):  #start where it left off
                                if header[l] == ")": #identify end of last parenthesis to figure out where the rectangle ends
                                    end_rect = l + 1
                                    last_close = l + 1
                                    break
                            rect = header[i+1:l+1]
                            indv_header[1] = [rect]
                        else:               #if its not the first header
                            text = header[last_close + 2:i - 1]       #index out the text of header using the index of the last known closing parenthesis
                            indv_header[2] += [text]
                            for l in range(i,len(header)): #look for closing parenthesis again
                                if header[l] == ")":
                                    end_rect = l + 1
                                    last_close = l + 1
                                    break
                            rect = header[i+1:l+1]
                            indv_header[1] += [rect]
                all_headers.append(indv_header)

        return all_headers

    def para_extract(self):
        last_close = None
        all_paras = []
        for para in self.header_para(): #iterate through lines in header_para
            indv_para = [None,[None],[None]]
            count = 0 
            if '<p>' in para: #if line is a header
                indv_para[0] = "paragraph"

                for i in range(3,len(para)): #iterate through header string starting after decoration
                    if para[i] == ")": #figure out index where first set of rect coords ends
                        last_close = i

                    if para[i] == "|" and para[i+1] == "(": #find index of start of coords
        
                        count += 1 #keeps track of how many lines are in the header

                        if count == 1:    #if its the first header
                            text = para[3:i - 1]    #store text
                            indv_para[2] = [text] #append to main list
                            for l in range(i,len(para)):  #start where it left off
                                if para[l] == ")": #identify end of last parenthesis to figure out where the rectangle ends
                                    end_rect = l + 1
                                    last_close = l + 1
                                    break
                            rect = para[i+1:l+1]
                            indv_para[1] = [rect]
                        else:               #if its not the first header
                            text = para[last_close + 2:i - 1]       #index out the text of header using the index of the last known closing parenthesis
                            indv_para[2] += [text]
                            for l in range(i,len(para)): #look for closing parenthesis again
                                if para[l] == ")":
                                    end_rect = l + 1
                                    last_close = l + 1
                                    break
                            rect = para[i+1:l+1]
                            indv_para[1] += [rect]
                all_paras.append(indv_para)

        return all_paras
    

    def my_sort(self):
        all_data = []
        for item in create_annots(self.annot_extract()):
            all_data.append(item)
        for item in create_tables(self.table_extract()):
            all_data.append(item)
        for item in create_headers(self.header_extract()):
            all_data.append(item)
        for item in self.filtered_para():
            all_data.append(item)

        all_data.sort(key=lambda x: x.tl_y)
        return all_data

    def filtered_para(self):
        new_paras = []
        table_list = create_tables(self.table_extract())
        para_list = create_paras(self.para_extract())
        for table in table_list:
            table_rect = fitz.Rect(table.x0, table.y0, table.x1, table.y1)
            for para in para_list:
                para_rect = fitz.Rect(para.x0[0], para.y0[0], para.x1[0], para.y1[0])
                if not table_rect.intersects(para_rect):
                    new_paras.append(para)
        return new_paras
           


    #can sift through the html data to extract what I need
    #create new conda environment with both camelot, pymupdf, fitz, ghostscript?
    #follow instructions from Pattu's email to restructure annotation extract function 
    #figure out how to extract coordinates of headers
    #figure out how to extract paragraphs and their respective coordinates.

"""
annotation = Annotation("Strikeout", ("104.7760009765625, 434.2879943847656, 356.8580017089844, 446.4519958496094") ,\
    "Sit beatae ipsa eos quia praesentium ut vero autem.")
table = Table((72.0, 535.4399999999999, 521.52, 623.04), [['Lorem ipsum', 'praesentium', 'a dolorum \nmagni'], ['dolor sit amet', 'Aut optio \nipsam', \
    'ut fugit \narchitecto'], ['ea accusantium \nomnis', 'ea inventore \nlibero', 'sit porro enim'], ['et quisquam \ntemporibus', 'ut sint omnis', \
        'Eos architecto'], ['ea mollitia \nsuscipit', 'Qui galisum \nlaudantium', 'sit corrupti \nomnis']])
"""

test = PDF("/Users/dereklaboy/Desktop/new_repo/Lorem Ipusm.pdf") #create PDF object
"""
print("Extracting Annotations:")
print()

print(test.annot_extract())
print()

print("--------------------------------------------------")
print()

for item in test.annot_extract():
    print(item)
    print()

print("--------------------------------------------------")
print()

print("Extracting Table Data:")
print()

lst = test.table_extract()
for x in lst:
    print(x)
    print()
"""
my_annot = create_annots(test.annot_extract())
for x in my_annot:
    print(x)
print()

my_header = create_headers(test.header_extract())
for x in my_header:
    print(x)
print()
 
my_table = create_tables(test.table_extract())
for x in my_table:
    print(x)
print()

my_para = create_paras(test.para_extract())
for x in my_para:
    print(x)
print()

"""
print()
for x in (test.annot_extract()):
    print(x)
    print()

for x in (test.header_extract()):
    print(x)
    print()
print()
"""
print("----------------------------------------------------------------------------")
print()
x = test.my_sort()
for item in x:
    print(item)
    print()


#test code to compare the before and after of paragraph filter method
"""
print("----------------------------------------------------------------------------") 
my_para = create_paras(test.para_extract())
for x in my_para:
    print(x)
    print()

print("----------------------------------------------------------------------------")
for x in test.filter_para():
    print(x)
    print()
"""

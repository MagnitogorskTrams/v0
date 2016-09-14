import curl,re
import os, os.path, platform

default_folder = '/home/ant/Документы/МГТ/raspisanie/2016-08-21/'

h = [b'unost.xls']

import xlrd

fld = default_folder
#ins = 'INSERT INTO import_xaxa."raw"(stop_id, stop_name, next_stops, route, workday, "time") VALUES (%s, \'%s\', \'%s\', \'%s\', %s, \'%02d:%02d+05:00\');\n'
csv = '[%d\t%d]\t%s;\'%s\';\'%s\';\'%s\';%s;\'%02d:%02d+05:00\''
for f in h:
    fn = f.strip().decode('utf-8')

    rb = xlrd.open_workbook(fld + fn,formatting_info=True)

    for sheet in rb.sheets(): # по всем листам
        ref = re.match(r'\d+', sheet.name).group(0)
        # получаем значение первой ячейки A1 - val = sheet.row_values(0)[0]
        # print (val)
        #vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)] # получаем список значений из всех записей
        workday = None
        route = None
        for rownum in range(sheet.nrows):
            row = sheet.row_values(rownum)
            #print (row)
            # if len(row[0])+len(str(row[1])) < 1 : break
            for colnum in range(len(row)) :
                cell = sheet.cell(rownum, colnum)
                if cell.value == '№ Маршрута' : break
                if cell.value == 'Рабочие дни':
                    workday = True
                    break
                if cell.value == 'Выходные дни':
                    workday = False
                    break
                if cell.ctype == xlrd.XL_CELL_BLANK or cell.ctype == xlrd.XL_CELL_EMPTY : continue
                if colnum == 0:
                    if rownum == 0:
                        stop_groups = re.match(r'Остановка "(["№,-\/\w\.\s\\]+)"\s?в сторону [\w\.\s\\]*(.*)', cell.value)
                        stop_name = stop_groups.group(1) #.findall(r'"(.*)"').group(0))
                        stop_direction = stop_groups.group(2).strip()
                        #print ('[%s]\t%s -> %s' % (ref,stop_name,stop_direction))
                        break
                    else:
                        if cell.ctype == xlrd.XL_CELL_NUMBER:
                            route = str(int(cell.value))
                        elif cell.ctype == xlrd.XL_CELL_TEXT:
                            route = cell.value
                        continue
                if cell.ctype == xlrd.XL_CELL_DATE:
                    t = round(cell.value, 9)
                    if t >= 1 : t = t - int(t)
                    (y, mo, d, h, mi, sec) = xlrd.xldate.xldate_as_tuple(t, 0)
                elif cell.ctype == xlrd.XL_CELL_TEXT:
                    (h, mi) = re.match(r'(\d+)[\.:](\d+)', cell.value).groups()
                    #print (h, mi)
                #print (ins % (ref,stop_name,stop_direction, route, workday, h, mi))
                #curins = ins % (ref,stop_name,stop_direction, route, workday, h, mi) #).decode('utf-8')
                curcsv = csv % (rownum,colnum,ref,stop_name,stop_direction, route, workday, int(h), int(mi))
                print(curcsv, t, cell.ctype)
    #break

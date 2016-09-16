import curl,re
import sys, os, os.path, platform

if platform.system() == 'Windows':
	default_folder = 'd:\\Works\\DOCs\\транспортный эмулятор\\raspisanie\\2016-08-21\\'
	os.environ['HTTP_PROXY']="http://161.8.100.200:8080"
	os.environ['HTTPS_PROXY']="http://161.8.100.200:443"
else:
	default_folder = '/home/ant/Документы/МГТ/raspisanie/2016-08-21/'

bu="http://www.maggortrans.ru/raspisanie/"
r=curl.Curl(bu)
r.get()
b=r.body()
#print (b)
h=re.findall(b'href="(\w+.xls)"', b)
if h is None:
    print ('No matches')
    exit()
else:
    for f in h:
        print(bu+f.strip().decode('utf-8'))
        break

cnt = 0
for f in h:
    fn = f.strip().decode('utf-8')
    if os.path.isfile(default_folder+fn) :
        print (fn)
        continue
    r=curl.Curl(bu+fn)
    r.get()
    fh = open(default_folder+fn,'wb')
    fh.write(r.body())
    fh.close()
    print(fn)
    cnt = cnt + 1
print (cnt,"file(-s) saved")

import xlrd

fld = input("Enter dir name: ")
if len(fld) == 0 : fld = default_folder
#ins = 'INSERT INTO import_xaxa."raw"(stop_id, stop_name, next_stops, route, workday, "time") VALUES (%s, \'%s\', \'%s\', \'%s\', %s, \'%02d:%02d+05:00\');\n'
csv = '%s;\'%s\';\'%s\';\'%s\';%s;\'%02d:%02d+05:00\'\n'
#outf = open(default_folder+'insert_raw.sql','w')
outf = open(default_folder+'raw.csv','w')
rdict = dict()
try:
    #outf.write('CREATE TABLE IF NOT EXISTS import_xaxa."raw"(stop_id text,stop_name text,next_stops text,route text,workday boolean,"time" time with time zone) WITH (OIDS=FALSE);\n')
    #outf.write('ALTER TABLE IF EXISTS import_xaxa."raw" OWNER TO postgres;\n')
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
                    if cell.ctype == xlrd.XL_CELL_TEXT and len(cell.value.strip()) == 0 : continue
                    try:
                        if colnum == 0:
                            if rownum == 0:
                                stop_groups = re.match(r'Остановка "(["№,-\/\w\.\s\\]+)"\s?в сторону [\w\.\s\\]*(.*)', cell.value)
                                stop_name = stop_groups.group(1) #.findall(r'"(.*)"').group(0))
                                stop_direction = stop_groups.group(2).strip()
                                #NB! убрать кавычки и поделить на части
                                #print ('[%s]\t%s -> %s' % (ref,stop_name,stop_direction))
                                break
                            else:
                                if cell.ctype == xlrd.XL_CELL_NUMBER:
                                    route = str(int(cell.value))
                                elif cell.ctype == xlrd.XL_CELL_TEXT:
                                    route = cell.value.strip()
                                    if route == 'Депо 1' : continue
                                    # вырезать пробелы в середине
                                    (route, var) = re.match(r'(\d+)\s*(.*)', route).groups()
                                    if var in ['Депо 1','д-1','Д -1','Д-1'] : var = 'в Депо-1'
                                    if var in ['в депо3','в депо 3'] : var = 'в Депо-3'
                                    if var in ['А','Б'] : route = route + var
                                    else : route = route + ' ' + var
                                continue
                        (t, h, mi) = (None,None,None)
                        if cell.ctype == xlrd.XL_CELL_DATE:
                            t = round(cell.value, 9)
                            if t >= 1 : t = t - int(t)
                            (y, mo, d, h, mi, sec) = xlrd.xldate.xldate_as_tuple(t, 0)
                        elif cell.ctype == xlrd.XL_CELL_TEXT:
                            (h, mi) = re.match(r'(\d+)[\.:](\d+)', cell.value).groups()
                            #print (h, mi)
                        elif cell.ctype == xlrd.XL_CELL_ERROR:
                            raise
                        #print (ins % (ref,stop_name,stop_direction, route, workday, h, mi))
                        #curins = ins % (ref,stop_name,stop_direction, route, workday, h, mi) #).decode('utf-8')
                        curcsv = csv % (ref,stop_name,stop_direction, route, workday, int(h), int(mi))
                    except:
                        print (sys.exc_info())
                        print(ref,stop_name,stop_direction, route, workday, h, mi)
                        sys.exit('In the file %s occurred error on cell [%d,%d] of "%s" sheet' % (fn, rownum, colnum, sheet.name))
                    outf.write(curcsv)
        #break
finally:
    outf.close()

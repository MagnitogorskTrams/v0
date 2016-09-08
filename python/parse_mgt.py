import curl,re

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

import os.path

default_folder = '/home/ant/Документы/МГТ/raspisanie/2016-08-21/'
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
for f in h:
    fn = f.strip().decode('utf-8')

    rb = xlrd.open_workbook(fld + fn,formatting_info=True)

    for sheet in rb.sheets(): # по всем листам
        val = sheet.row_values(0)[0] # получаем значение первой ячейки A1
        # print (val)
        try:
            stop_groups = re.match(r'Остановка "(["№,-\/\w\.\s\\]+)"\s?в сторону [\w\.\s\\]*(.*)', val) # "(\w+)"(\w+)).
            stop_name = stop_groups.group(1) #.findall(r'"(.*)"').group(0))
            stop_direction = stop_groups.group(2)
        except:
            stop_direction = '----------'
        vals = [sheet.row_values(rownum) for rownum in range(sheet.nrows)] # получаем список значений из всех записей
        print ('[%s]\t%s -> %s: %d' % (re.match(r'\d+', sheet.name).group(0),stop_name,stop_direction,len(vals)))


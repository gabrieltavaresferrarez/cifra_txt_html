import os

str_pathFolder = os.path.dirname(__file__)

str_pathHeader = os.path.join(str_pathFolder, 'header.html')
file_header = open(str_pathHeader, 'r')
str_header = file_header.read()
file_header.close()

str_pathBottom = os.path.join(str_pathFolder, 'bottom.html')
file_bottom = open(str_pathBottom, 'r')
str_bottom = file_bottom.read()
file_bottom.close()

list_cifras = os.listdir('cifras out')
list_cifras = [cifra for cifra in list_cifras if '.html' in cifra]

str_options = ''

for str_cifra in list_cifras:
  str_cifraNome = str_cifra.replace('_',' ').replace('.html', '')
  str_options += f'<option value="cifras/{str_cifra}">{str_cifraNome}</option>\n'


str_pathIndex = os.path.join(str_pathFolder, 'index.html')
file_index = open(str_pathIndex, 'w')
file_index.write(str_header)
file_index.write(str_options)
file_index.write(str_bottom)
file_index.close()
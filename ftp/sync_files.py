from ftplib import FTP
import os

# esse script adiciona cifras ao site caso a cifra não exista lá
print('\n#### SYNC START ####\n')

str_host = 	'ftpupload.net'
str_user = 'if0_35290732'
file_password = open('ftp/password.txt', 'r')
str_password = file_password.read()
file_password.close()

list_localFiles = os.listdir('cifras out')
list_localFiles = [file for file in list_localFiles if '.html' in file or '.ico' in file] # filter only htmls

print('Entering FTP Server : ' + str_host)
with FTP(str_host) as ftp:
  print('SUCCESS\n\n')

  print('Login in FTP Server')
  ftp.login(user=str_user, passwd=str_password)
  print('SUCCESS\n\n')

  print('Listing Server files')
  list_filesServer = ftp.nlst('htdocs/cifras')
  print('Server files listed. Comparing to local files\n')

  list_filesUpload = []
  for str_file in list_localFiles:
    if not(str_file in list_filesServer):
      list_filesUpload.append(str_file)

  print('{} files to upload : \n{}'.format(len(list_filesUpload), "\n".join(list_filesUpload)))

  for str_file in list_filesUpload:
    print('Uploading ' + str_file)
    with open('cifras out/' + str_file, 'rb') as file:
      ftp.storbinary('STOR ' + 'htdocs/cifras/' + str_file, file)
  print('\nSUCCESS : All files Uploaded\n')

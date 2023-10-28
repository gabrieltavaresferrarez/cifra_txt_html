import os
import codecs
from cifra import Cifra
import re
from unidecode import unidecode

# Mudanças de tom da cifra devem ter a primeira linha com o formato
# @ TOM + N
# @ TOM - N

# Nome da musica deve estar no titula do arquivo e não no conteudo

header_filename = './text_sources/header.html'
botton_filename = './text_sources/botton.html'

for filename in os.listdir('cifras in'):
   nome_musica = filename.replace('.txt', '')

   with codecs.open(header_filename, 'r', 'utf-8') as file:
      header_html = file.read().replace('[MUDAR TITULO]', nome_musica)
   with codecs.open(botton_filename, 'r', 'utf-8') as file:
      botton_html = file.read()

   string_fileName = r'cifras in/'+ str(filename)
   with codecs.open(string_fileName, 'r', 'utf-8') as file:
      cifra_linhas = file.read()
      primeira_linha = cifra_linhas.split('\n')[0]
      if len(primeira_linha) > 0 and '@' in primeira_linha[0] and 'TOM' in primeira_linha: #primeira linha tem modulação de tom
         if '+' in primeira_linha:
            modulacao =int(re.findall(r'\d+', primeira_linha)[0])
            cifra_linhas = cifra_linhas.replace(primeira_linha+'\n', '')
            cifra = Cifra(cifra_linhas, nome_musica)
            cifra += modulacao
         elif '-' in primeira_linha:
            modulacao = int(re.findall(r'\d+', primeira_linha)[0])
            cifra_linhas = cifra_linhas.replace(primeira_linha+'\n', '')
            cifra = Cifra(cifra_linhas, nome_musica)
            cifra -= modulacao
      else:
         cifra = Cifra(cifra_linhas, nome_musica)
         

   cifra_out_filename = 'cifras out/' + filename.replace('.txt', '.html')
   with codecs.open(unidecode(cifra_out_filename), 'w', 'utf-8') as file:
      file.write(header_html)
      file.write(cifra.export_html())
      file.write(botton_html)
from .acordes import Acorde
import re
from .utils import *
import codecs
from .errors import ConstructorError
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Uma cifra é composta por uma lista de linhas
#     Cada linha é uma lista de Elementos
#         Esses Elementos podem String ou Acorde

# ex.  A   B   2x -> [Acorde<A>, '   ', Acorde<B>, '   ', '2x']
#   Ele vive -> ['Ele', ' ', 'vive',]
class Cifra:
    '''Objeto Cifra guarda uma cifra em formato de lista

    * Argumentos:
        - nome_musica (str) : é o nome da música
        - text (str) : é um contrutor no formato de texto que não pode estar vazio
        - text_file (str) : é um construtor que indica o caminho de um arquivo de texto da cifra
        - xml_file (str) : é um construtor que indica o caminho de um arquivo xml da cifra
        - xml_content (str) : é um contrutor no formato de texto que não pode estar vazio
        - list_lines (list) : é um construtor que já passa uma lista de elementos de texto e Acorde. (é usado quando vamos criar uma cifra a partir de outra)

    * Argumentos opcionais: 
        - reshape (bool)[default=True] : Indica se a cifra deve passar por um reshape no tamanho das linhas ou não
        - maxSizeLinha (int)[default=30] : É o número máximo de caracteres que uma linha pode ter antes de ser cortada
    '''
    def __init__(self, nome_musica:str, text:str='', text_file:str='', xml_file:str= '', xml_content:str='', list_lines=[], maxSizeLinha:int = 30, reshape=True):
        # inicializa atributos da cifra -------------------
        self.__str_nome = nome_musica # private attribute
        self.__list_linhas = [] # privata attribute
        self.__int_maxSizeLinha = maxSizeLinha
        
        
        # verifica qual é o construtor da cifra -------------------
        bool_text_constructor = len(text)>0
        bool_text_file_constructor = len(text_file)>0
        bool_xml_file_constructor = len(xml_file)>0
        bool_xml_content_constructor = len(xml_content)>0
        bool_list_lines_constructor = len(list_lines)>0
        int_numConstrutores = int(bool_text_file_constructor) + bool(bool_text_constructor) + int(bool_xml_file_constructor) + int(bool_xml_content_constructor) + int(bool_list_lines_constructor)
        
        str_listConstructors = 'text, text_file, xml_file, xml_content, list_lines'
        if int_numConstrutores == 0:
            raise ConstructorError(f'É necessário usar um construtor válido entre {str_listConstructors}')
        if int_numConstrutores > 1:
            raise ConstructorError(f'É necessário usar apenas 1 construtor válido entre {str_listConstructors}')

        # Chama o construtor da cifras
        if bool_text_constructor: # constrói cifra a aprtir de um texto
            self.__constructor_text(text)
        elif bool_text_file_constructor: # constrói cifra a partir de um arquivo de texto
            self.__constructor_text_file(text_file)
        elif bool_xml_file_constructor: # constrói cifra a partir de um arquivo xml
            self.__constructor_xml_file(xml_file)
        elif bool_xml_content_constructor: # constrói cifra a partir de um texto xml
            self.__constructor_xml_content(xml_content)
        elif bool_list_lines_constructor: # constrói cifra a partir de um objeto de linhas de python -> usado para criar cifras a partir de outra
            self.__constructor_list_lines(list_lines)

        # após gerar uma cifra, reordena as linhas para terem um limite de caracteres por linha
        if reshape:
            self.reshape_lines(self.__int_maxSizeLinha)
    
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------- METODOS DE CONSTRUCAO ----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------
    
    def __constructor_text(self, str_text):
        listStr_linhasCifra = str_text.split('\n')
        modulacao = self.__get_modulation(listStr_linhasCifra[0]) # verifica se há modulação no texto
        if modulacao != 0:
            listStr_linhasCifra = listStr_linhasCifra[1:] # se tiver modulacao, remove a primeira linha do texto
        

        # passa por cada linha
        for str_linha in listStr_linhasCifra:
            str_linha = str_linha.replace('\r\n', '').replace('\n', '') # da uma limpada nas linhas pros diferentes editores de texto
            # separa as palavras e espaços de cada linha
            str_patternEspacos = r'(\s+|\S+)'
            list_palavras = re.findall(str_patternEspacos, str_linha)
            list_elementosMix = [] # lista a ser adicionada com palavras e acordes
            list_elementoPalavrasApenas = [] # lista apenas com palavras

            # verifica se as palavras são palavras ou acordes
            for str_palavra in list_palavras:
                acorde_palavra = Acorde(str_palavra)
                list_elementoPalavrasApenas.append(str_palavra)
                if acorde_palavra.is_acorde():
                    list_elementosMix.append(acorde_palavra)
                else:
                    list_elementosMix.append(str_palavra)
            
            #verifica se maior parte da linha é palavra ou acorde
            razao_acorde_palavras = 1/4
            list_acordesApenas = [elemento for elemento in list_elementosMix if type(elemento) == Acorde]
            if len(list_elementoPalavrasApenas)> 0 and len(list_acordesApenas)/len(list_elementoPalavrasApenas) <= razao_acorde_palavras: # poucos acordes por linha
                self.__list_linhas.append(list_elementoPalavrasApenas) # adiciona a lista de apenas palavras na lista de linhas
            else:
                self.__list_linhas.append(list_elementosMix) # adiciona a lista de palavras e acordes na lista de linhas

        if modulacao != 0:
            self.modulate(modulacao)

    '''Constroi a cifra a partir de um arquivo de texto
    '''
    def __constructor_text_file(self, str_textFileName):
        with codecs.open(str_textFileName, 'r', 'utf-8') as file:
            str_cifraLinhas = file.read()
            if len(str_cifraLinhas) == 0:
                raise ConstructorError(f'Arquivo {str_textFileName} está vazio')
            primeira_linha = str_cifraLinhas.split('\n')[0]
            modulacao = self.__get_modulation(primeira_linha)

            str_cifraLinhas = str_cifraLinhas.replace(primeira_linha+'\n', '') #remove a primeira linha da modulação
            self.__constructor_text(str_cifraLinhas) # constroi o list_linhas
            if modulacao != 0:
                self.modulate(modulacao)

    def __constructor_xml_file(self, str_textFileName):
        with codecs.open(str_textFileName, 'r', 'utf-8') as file:
            str_cifraXML = file.read()
            if len(str_cifraXML) == 0:
                raise ConstructorError(f'Arquivo {str_textFileName} está vazio')
            self.__constructor_xml_content(str_cifraXML) # constroi o list_linhas

    def __constructor_xml_content(self, str_text):
        xmlElement_cifra = ET.fromstring(str_text)
        list_elementosValidos = {'cifra', 'linha', 'acorde', 'texto'}
        # valida se xml está na estrutura correta ======
        for xmlElement in xmlElement_cifra.iter():
            if xmlElement.tag not in list_elementosValidos:
                raise ConstructorError(f'Erro na leitura do XML da cifra. Apenas as tags {list_elementosValidos} são válidas, mas foi encontrada a tag {xmlElement.tag}')

        # constrói lista a partir de xml
        modulacao = 0
        for atributo, valor in xmlElement_cifra.attrib.items():
            if atributo == 'modulacao' and valor.isnumeric:
                modulacao = int(valor)

        for xmlElement_linha in xmlElement_cifra:
            list_newLine = []
            for xmlElement_elemento in xmlElement_linha:
                if xmlElement_elemento.tag == 'acorde':
                    elemento = Acorde(xmlElement_elemento.text)
                elif xmlElement_elemento.tag == 'texto':
                    elemento = xmlElement_elemento.text
                list_newLine.append(elemento)
            self.__list_linhas.append(list_newLine)
        
        if modulacao != 0:
            self.modulate(modulacao)




    def __constructor_list_lines(self, list_lines):
        # verifica se a lista tem apenas Acordes e textos
        for i, list_linha in enumerate(list_lines):
            if type(list_linha) != list :
                raise ConstructorError(f'Linha {i} da lista não é um objeto de lista.')
            for j, elemento in enumerate(list_linha):
                if type(elemento) not in [Acorde, str]:
                    raise ConstructorError(f'Linha {i} - palavra {j} da lista não é um objeto de str ou Acorde.')
        self.__list_linhas = list_lines
    

    @staticmethod
    def __get_modulation(str_text):
        # identifica @ TOM + 1 na linha
        modulacao = 0
        if len(str_text) > 0 and str_text[0] == '@' and 'TOM' in str_text: #primeira linha tem modulação de tom
            if '+' in str_text:
                modulacao = + int(re.findall(r'\d+', str_text)[0])
            elif '-' in str_text:
                modulacao = - int(re.findall(r'\d+', str_text)[0])
        return modulacao

    
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------- METODOS DE REPRESENTAÇAO ----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------
    
    def __str__(self):
        str_text = '[' + self.__str_nome+']\n\n'
        for linha in self.__list_linhas:
            for elemento in linha:
                str_text += str(elemento)
            str_text += '\n'
        return str_text

    def __repr__(self):
        return self.__str__()
    
    def get_list(self):
        return self.__list_linhas.copy()
        
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------- METODOS DE MODULAÇAO ----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def __add__(self, value):
        if type(value) == int:
            return self.modulate(value, itSelf=False)
        else:
            raise ValueError(f'Soma apenas com inteiros e não {type(value)}')
        
    def __sub__(self, value):
        if type(value) ==  int:
            return self.modulate(-value, itSelf=False)
        else:
            raise ValueError(f'Subtração apenas com inteiros e não {type(value)}')
    
    '''Modula a cifra para alterar o tom dela

    * Argumento opcional
        - itSelf (bool)[default=True] : Altera o valor da própria cifra. Se for False, retorna um novo objeto cifra alterado
    '''
    def modulate(self, int_modulacao:int, itSelf:bool = True):
        list_linhasNew = []
        for linha in self.__list_linhas:
            linha_new = []
            for element in linha:
                if type(element) == Acorde:
                    linha_new.append(element + int_modulacao)
                else:
                    linha_new.append(element)
            list_linhasNew.append(linha_new)
        if itSelf:
            self.__list_linhas = list_linhasNew
            return None
        else:
            return Cifra(self.__str_nome, list_lines=list_linhasNew)

    
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------- METODOS DE EXPORTAÇAO ----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------
    def get_title(self, int_maxSize = 15):
        str_title = ''
        list_nomeMusica = self.__str_nome.split(' ')

        str_line = ''
        while len(list_nomeMusica) > 0:
            if len(str_line) + len(list_nomeMusica[0]) < int_maxSize:
                str_line += list_nomeMusica.pop(0) + ' '
            elif len(list_nomeMusica[0]) > int_maxSize: # palavra muito grande no titulo
                if len(str_line) == 0:
                    str_title = list_nomeMusica.pop(0) + '\n' # adiciona a palavra grande quando a linha estiver vazia
            else:
                str_title = str_title + str_line[:-1] + '\n'
                str_line = ''
        
        str_title = str_title + str_line[:-1]
        return str_title
    

    '''
    returns a string of the html file conatining the cifra
    '''
    def export_html(self):
        html = '<div class="cifra">\n'
        html += '\t<pre class="cifra">\n'
        html += '<strong class="title">' + self.get_title() + '</strong>\n\n'
        for linha in self.list_linhas:
            for elemento in linha:
                if type(elemento) == Acorde:
                    html += '<strong class="acorde">'+str(elemento)+"</strong> "
                else:
                    html += elemento
            html += '\n'
        html += '\t</pre>\n'
        html += '</div>\n'
        
        return html
    
    def export_xml(self, str_pathOut:str = 'cifra.xml', formatted:bool = True, exportFile:bool = False, filename:str = 'cifra.xml'):
        xmlElement_cifra = ET.Element("cifra")
        xmlElement_cifra.attrib['nome'] = self.__str_nome
        for list_linha in self.__list_linhas:
            xmlElement_linha = ET.SubElement(xmlElement_cifra, "linha")
            for elemento in list_linha:
                if type(elemento) == Acorde:
                    xmlElement_acorde = ET.SubElement(xmlElement_linha, "acorde")
                    xmlElement_acorde.text = str(elemento)
                if type(elemento) == str:
                    xmlElement_texto = ET.SubElement(xmlElement_linha, "texto")
                    xmlElement_texto.text = str(elemento)

        xmlTree_cifra = ET.ElementTree(xmlElement_cifra)
        strXml_cifra = ET.tostring(xmlElement_cifra, encoding='utf-8', method='xml')
        if formatted:
            strXml_cifraFormatted = minidom.parseString(strXml_cifra).toprettyxml(indent="  ")
        else:
            strXml_cifraFormatted = strXml_cifra

        if exportFile:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(strXml_cifraFormatted)

        return strXml_cifraFormatted
        
    
    # ------------------------------------------------------------------------------------------------------------------------------------------
    # ---------------------------------------------- METODOS DE TRANSFORMAÇAO ----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------------------------------

    def reshape_lines(self, max_letters):
        list_linhasCifra = self.__list_linhas
        int_maxLinha = max_letters
        list_novaCifra = []

        int_linhaIndex = 0

        while int_linhaIndex < len(list_linhasCifra): # varre todas as linhas

            if is_linha_acordes(list_linhasCifra[int_linhaIndex]) and is_linha_texto(list_linhasCifra[int_linhaIndex+1]):    # par de linhas de acorde e texto
                int_linhaAcordeIndex = int_linhaIndex
                int_linhaIndex += 1
                int_linhaTextoIndex = int_linhaIndex

                while len(list_linhasCifra[int_linhaAcordeIndex]) >0 or len(list_linhasCifra[int_linhaTextoIndex]): # roda loop até encerrar as duas linhas
                    if size_linha(list_linhasCifra[int_linhaAcordeIndex]) > int_maxLinha and size_linha(list_linhasCifra[int_linhaTextoIndex]) > int_maxLinha: # ambas as linhas estão maior que MAX
                        pass
                        # extrai MAX das duas linhas
                        list_novaLinhaTexto =[]
                        while size_linha(list_novaLinhaTexto) + len(list_linhasCifra[int_linhaTextoIndex][0]) < int_maxLinha: # verifica se adicionar mais um elemento estoura o tamanho
                            list_novaLinhaTexto.append(list_linhasCifra[int_linhaTextoIndex][0])
                            list_linhasCifra[int_linhaTextoIndex] = list_linhasCifra[int_linhaTextoIndex][1:] # remove o primeiro elemento da lista 1 por 1
                            if len(list_linhasCifra) == 0:
                                break
                            
                        list_novaLinhaAcorde=[]
                        while True:
                            if size_linha(list_novaLinhaAcorde) + len(str(list_linhasCifra[int_linhaAcordeIndex][0])) < size_linha(list_novaLinhaTexto): # verifica se adicionar o proximo elemento inteiro esoura linha
                                # se não estoura, adiciona na lista nova e atualiza a lista original de acordes
                                list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0])
                                list_linhasCifra[int_linhaAcordeIndex] = list_linhasCifra[int_linhaAcordeIndex][1:] # remove o primeiro elemento da lista 1 por 1
                            else:
                                # se estourar o tamanho da linha de acorde verifica
                                if type(list_linhasCifra[int_linhaAcordeIndex][0]) == Acorde: # se for acorde, adiciona o acorde todo
                                    list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0]) # adiciona o elemento na linha
                                    list_linhasCifra[int_linhaAcordeIndex] = list_linhasCifra[int_linhaAcordeIndex][1:] # remove o primeiro elemento da lista 1 por 1
                                    break
                                else: # se for texto, corta o texto no meio
                                    int_numeroCaracteresAdicionar = size_linha(list_novaLinhaTexto) - size_linha(list_novaLinhaAcorde)
                                    list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0][:int_numeroCaracteresAdicionar])
                                    list_linhasCifra[int_linhaAcordeIndex][0] = list_linhasCifra[int_linhaAcordeIndex][0][int_numeroCaracteresAdicionar:] # remove os caracteres que foram adicionados na linha nova da linha original
                                    break
                
                        # adiciona duas linhas na cifra nova
                        list_novaCifra.append(list_novaLinhaAcorde)
                        list_novaCifra.append(list_novaLinhaTexto)
                        # exit()
                    elif size_linha(list_linhasCifra[int_linhaAcordeIndex]) > int_maxLinha and size_linha(list_linhasCifra[int_linhaTextoIndex]) <= int_maxLinha: # apenas linha de acorde maior que MAX
                        # estrai linha completa de texto
                        list_novaLinhaTexto = list_linhasCifra[int_linhaTextoIndex] # agora toda linha de acorde é usada (não é maior que MAX)
                        list_linhasCifra[int_linhaTextoIndex] = [] #esvazia linha original
                        
                        # extrai MAX da linha de acordes
                        list_novaLinhaAcorde=[]
                        while True:
                            if size_linha(list_novaLinhaAcorde) + len(str(list_linhasCifra[int_linhaAcordeIndex][0])) < int_maxLinha: # verifica se adicionar o proximo elemento inteiro esoura linha
                                # se não estoura, adiciona na lista nova e atualiza a lista original de acordes
                                list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0])
                                list_linhasCifra[int_linhaAcordeIndex] = list_linhasCifra[int_linhaAcordeIndex][1:] # remove o primeiro elemento da lista 1 por 1
                            else:
                                # se estourar o tamanho da linha de acorde verifica
                                if type(list_linhasCifra[int_linhaAcordeIndex][0]) == Acorde: # se for acorde, adiciona o acorde todo
                                    list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0]) # adiciona o elemento na linha
                                    list_linhasCifra[int_linhaAcordeIndex] = list_linhasCifra[int_linhaAcordeIndex][1:] # remove o primeiro elemento da lista 1 por 1
                                    break
                                else: # se for texto, corta o texto no meio
                                    int_numeroCaracteresAdicionar = int_maxLinha - size_linha(list_novaLinhaAcorde)
                                    list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0][:int_numeroCaracteresAdicionar])
                                    list_linhasCifra[int_linhaAcordeIndex][0] = list_linhasCifra[int_linhaAcordeIndex][0][int_numeroCaracteresAdicionar:] # remove os caracteres que foram adicionados na linha nova da linha original
                                    break
                        
                        # adiciona linha de acorde
                        list_novaCifra.append(list_novaLinhaAcorde)
                        # se len(linha texto)>0 adiciona
                        if len(list_novaLinhaTexto) > 0: # não acabou os acordes
                            list_novaCifra.append(list_novaLinhaTexto)

                    elif size_linha(list_linhasCifra[int_linhaAcordeIndex]) <= int_maxLinha and size_linha(list_linhasCifra[int_linhaTextoIndex]) > int_maxLinha: # apenas linha de texti maior que MAX
                        # extrai MAX da linha de texto
                        list_novaLinhaTexto =[]
                        while size_linha(list_novaLinhaTexto) + len(list_linhasCifra[int_linhaTextoIndex][0]) < int_maxLinha: # verifica se adicionar mais um elemento estoura o tamanho
                            list_novaLinhaTexto.append(list_linhasCifra[int_linhaTextoIndex][0])
                            list_linhasCifra[int_linhaTextoIndex] = list_linhasCifra[int_linhaTextoIndex][1:] # remove o primeiro elemento da lista 1 por 1
                            if len(list_linhasCifra) == 0:
                                break

                        # estrai linha completa de acorde
                        list_novaLinhaAcorde = list_linhasCifra[int_linhaAcordeIndex] # agora toda linha de acorde é usada (não é maior que MAX)
                        list_linhasCifra[int_linhaAcordeIndex] = [] #esvazia linha original

                        # se len(linha acorde)>0 adiciona
                        if len(list_novaLinhaAcorde) > 0: # não acabou os acordes
                            list_novaCifra.append(list_novaLinhaAcorde)
                        # adiciona linha de texto
                        list_novaCifra.append(list_novaLinhaTexto)
                        pass
                    elif size_linha(list_linhasCifra[int_linhaAcordeIndex]) <= int_maxLinha and size_linha(list_linhasCifra[int_linhaTextoIndex]) <= int_maxLinha: # ambas as linhas menores que MAX
                        # estrai linha completa de acorde
                        list_novaLinhaAcorde = list_linhasCifra[int_linhaAcordeIndex] # agora toda linha de acorde é usada (não é maior que MAX)
                        list_linhasCifra[int_linhaAcordeIndex] = [] #esvazia linha original

                        # estrai linha completa de texto
                        list_novaLinhaTexto = list_linhasCifra[int_linhaTextoIndex] # agora toda linha de acorde é usada (não é maior que MAX)
                        list_linhasCifra[int_linhaTextoIndex] = [] #esvazia linha original
                
                        # se len(linha acorde)>0 adiciona
                        if len(list_novaLinhaAcorde) > 0: # não acabou os acordes
                            list_novaCifra.append(list_novaLinhaAcorde)
                        # se len(linha texto)>0 adiciona
                        if len(list_novaLinhaTexto) > 0: # não acabou os acordes
                            list_novaCifra.append(list_novaLinhaTexto)
                        
                        # indexLinha += 1
                        int_linhaIndex += 1

            elif is_linha_acordes(list_linhasCifra[int_linhaIndex]) : # adiciona linha de acorde sozinha
                # extrai MAX da linha de acordes
                int_linhaAcordeIndex = int_linhaIndex
                list_novaLinhaAcorde=[]

                # linha menor que MAX
                if size_linha(list_linhasCifra[int_linhaAcordeIndex]) < int_maxLinha:
                    # estrai linha completa de acorde
                    list_novaLinhaAcorde = list_linhasCifra[int_linhaAcordeIndex] # agora toda linha de acorde é usada (não é maior que MAX)
                    list_linhasCifra[int_linhaAcordeIndex] = [] #esvazia linha original
                
                # linha maior que MAX
                else:
                    while len(list_linhasCifra[int_linhaAcordeIndex]) > 0:
                        if size_linha(list_novaLinhaAcorde) + len(str(list_linhasCifra[int_linhaAcordeIndex][0])) < int_maxLinha: # verifica se adicionar o proximo elemento inteiro esoura linha
                            # se não estoura, adiciona na lista nova e atualiza a lista original de acordes
                            list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0])
                            list_linhasCifra[int_linhaAcordeIndex] = list_linhasCifra[int_linhaAcordeIndex][1:] # remove o primeiro elemento da lista 1 por 1
                        else:
                            # se estourar o tamanho da linha de acorde verifica
                            if type(list_linhasCifra[int_linhaAcordeIndex][0]) == Acorde: # se for acorde, adiciona o acorde todo
                                list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0]) # adiciona o elemento na linha
                                list_linhasCifra[int_linhaAcordeIndex] = list_linhasCifra[int_linhaAcordeIndex][1:] # remove o primeiro elemento da lista 1 por 1
                            elif is_spaces(list_linhasCifra[int_linhaAcordeIndex][0]): # se for texto, corta o texto no meio
                                int_numeroCaracteresAdicionar = int_maxLinha - size_linha(list_novaLinhaAcorde)
                                list_novaLinhaAcorde.append(list_linhasCifra[int_linhaAcordeIndex][0][:int_numeroCaracteresAdicionar])
                                list_linhasCifra[int_linhaAcordeIndex][0] = list_linhasCifra[int_linhaAcordeIndex][0][int_numeroCaracteresAdicionar:] # remove os caracteres que foram adicionados na linha nova da linha original
                            
                            # adiciona linha de acorde
                            # se len(linha acorde)>0 adiciona
                            if len(list_novaLinhaAcorde) > 0: # não acabou os acordes
                                list_novaCifra.append(list_novaLinhaAcorde)

                            list_novaLinhaAcorde=[] # zera nova linha para adicionar mais elementos
                
                # adiciona linha de acorde
                # se len(linha acorde)>0 adiciona
                if len(list_novaLinhaAcorde) > 0: # não acabou os acordes
                    list_novaCifra.append(list_novaLinhaAcorde)
                int_linhaIndex += 1

            elif is_linha_texto(list_linhasCifra[int_linhaIndex]): # adiciona linha de texto sozinha
                # extrai MAX de texto
                int_linhaTextoIndex = int_linhaIndex
                list_novaLinhaTexto =[]

                # linha menor que MAX
                if size_linha(list_linhasCifra[int_linhaTextoIndex]) < int_maxLinha:
                    # estrai linha completa de texto
                    list_novaLinhaTexto = list_linhasCifra[int_linhaTextoIndex] # agora toda linha de acorde é usada (não é maior que MAX)
                    list_linhasCifra[int_linhaTextoIndex] = [] #esvazia linha original
                else:
                    while len(list_linhasCifra[int_linhaTextoIndex]) > 0:
                        if size_linha(list_novaLinhaTexto) + len(list_linhasCifra[int_linhaTextoIndex][0]) < int_maxLinha: # verifica se adicionar mais um elemento estoura o tamanho
                            list_novaLinhaTexto.append(list_linhasCifra[int_linhaTextoIndex][0])
                            list_linhasCifra[int_linhaTextoIndex] = list_linhasCifra[int_linhaTextoIndex][1:] # remove o primeiro elemento da lista 1 por 1
                        else:
                            # adiciona linha nova na cifra
                            if len(list_novaLinhaTexto) > 0 :
                                list_novaCifra.append(list_novaLinhaTexto)
                            list_novaLinhaTexto = [] # zera linha para adicionar resto do texto

                if len(list_novaLinhaTexto) > 0 :
                    list_novaCifra.append(list_novaLinhaTexto)
                int_linhaIndex += 1
            else: # provavelmente linha vazia
                list_novaCifra.append(list_linhasCifra[int_linhaIndex])
                int_linhaIndex += 1
        
        self.__list_linhas = list_novaCifra
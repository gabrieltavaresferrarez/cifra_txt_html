from .acordes import Acorde
import re
from .utils import *

# Uma cifra é composta por uma lista de linhas
#     Cada linha é uma lista de Elementos
#         Esses Elementos podem String ou Acorde

# ex.  A   B   2x -> [Acorde<A>, '   ', Acorde<B>, '   ', '2x']
class Cifra:
    int_maxSizeLinha:int = 30

    def __init__(self, cifra_linhas, nome_musica:str):
        if type(cifra_linhas) == str:
            self.list_linhas = []
            self.str_nomeMusica = nome_musica
            listStr_linhasCifra = cifra_linhas.split('\n')

            # passa por cada linha
            for str_linha in listStr_linhasCifra:
                str_linha = str_linha.replace('\r\n', '').replace('\n', '') # da uma limpada nas linhas pros diferentes editores de texto

                # separa as palavras e espaços de cada linha
                str_patternPalavras = r'(\s+|\S+)'
                list_palavras = re.findall(str_patternPalavras, str_linha)
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
                list_acordesApenas = [elemento for elemento in list_elementosMix if type(elemento) == Acorde ]
                if len(list_elementoPalavrasApenas)> 0 and len(list_acordesApenas)/len(list_elementoPalavrasApenas) <= 1/4: # poucos acordes por linha
                    self.list_linhas.append(list_elementoPalavrasApenas) # adiciona a lista de apenas palavras na lista de linhas
                else:
                    self.list_linhas.append(list_elementosMix) # adiciona a lista de palavras e acordes na lista de linhas

        elif type(cifra_linhas) == list:
            self.str_nomeMusica = nome_musica
            self.list_linhas = cifra_linhas
        else:
            raise ValueError(f'cifra_linhas deve ser uma cifra em string ou uma lista de elementos de cifra')
        

        # após gerar uma cifra, reordena as linhas para terem um limite de caracteres por linha
        self.reshape_lines(self.int_maxSizeLinha)

        # Essa parte é um alerta de atenção para verificar se as músicas tem acordes de alerta que podem ser que não sem acordes
        #   e. Em -> pode ser acorde ou palavra
        list_acordesAtencao = [Acorde('Em'), Acorde('E')]
        list_acordesAlertaExistente = []
        for linha in self.list_linhas:
            for acorde in list_acordesAtencao:
                if acorde in linha:
                    if not(acorde in list_acordesAlertaExistente):
                        list_acordesAlertaExistente.append(acorde)
        if len(list_acordesAlertaExistente):
            print(f'[ATENÇÃO: a musica <{self.str_nomeMusica}> contem acorde {list_acordesAlertaExistente}]. Verifique se está certo todas as vezes')
            
    
    def __str__(self):
        str_text = '[' + self.str_nomeMusica+']\n\n'
        for linha in self.list_linhas:
            for elemento in linha:
                str_text += str(elemento)
            str_text += '\n'
        return str_text

    def __repr__(self):
        return self.__str__()
        
    def __add__(self, value):
        list_linhasNew = []
        if type(value) == int:
            for linha in self.list_linhas:
                linha_new = []
                for element in linha:
                    if type(element) == Acorde:
                        linha_new.append(element + value)
                    else:
                        linha_new.append(element)
                list_linhasNew.append(linha_new)
            return Cifra(list_linhasNew, self.str_nomeMusica)
        else:
            raise ValueError(f'Soma apenas com inteiros e não {type(value)}')
        
    def __sub__(self, value):
        if type(value) ==  int:
            return self + (-value)
        else:
            raise ValueError(f'Subtração apenas com inteiros e não {type(value)}')

    
    
    def get_title(self, int_maxSize = 15):
        str_title = ''
        list_nomeMusica = self.str_nomeMusica.split(' ')

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
    
    def reshape_lines(self, max_letters):
        list_linhasCifra = self.list_linhas
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
        
        self.list_linhas = list_novaCifra
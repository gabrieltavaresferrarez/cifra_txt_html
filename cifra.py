from acordes import Acorde
import re


# Uma cifra é composta por uma lista de linhas
#     Cada linha é uma lista de Elementos
#         Esses Elementos podem String ou Acorde

# ex.  A   B   2x -> [Acorde<A>, '   ', Acorde<B>, '   ', '2x']
class Cifra:
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
                list_elementos = []

                # verifica se as palavras são palavras ou acordes
                for str_palavra in list_palavras:
                    acorde_palavra = Acorde(str_palavra)
                    if acorde_palavra.is_acorde():
                        list_elementos.append(acorde_palavra)
                    else:
                        list_elementos.append(str_palavra)
                
                self.list_linhas.append(list_elementos) # adiciona a lista de elementos na lista de linhas
        elif type(cifra_linhas) == list:
            self.str_nomeMusica = nome_musica
            self.list_linhas = cifra_linhas
        else:
            raise ValueError(f'cifra_linhas deve ser uma cifra em string ou uma lista de elementos de cifra')
        
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

    '''
    returns a string of the html file conatining the cifra
    '''
    def export_html(self):
        html = '<div class="cifra">\n'
        html += '\t<pre class="cifra">\n'
        html += '<strong class="title">' + self.str_nomeMusica + '</strong>\n\n'
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
dict_notes = {
    'A' : 0,
    'A#': 1,
    'B' : 2,
    'C' : 3,
    'C#': 4,
    'D' : 5,
    'D#': 6,
    'E' : 7,
    'F' : 8,
    'F#': 9,
    'G' : 10,
    'G#': 11,
}
dict_notesValue = {
    0 : 'A' ,
    1 : 'Bb',
    2 : 'B' ,
    3 : 'C' ,
    4 : 'C#',
    5 : 'D' ,
    6 : 'D#',
    7 : 'E' ,
    8 : 'F' ,
    9 : 'F#',
    10 : 'G' ,
    11 : 'G#',
}

def circulate(int_value, lims : list = [0,11]):
    max = lims[1]
    min = lims[0]
    range = max-min +1
    if int_value > max:
        delta = int_value - max
        if delta % range == 0:
            return max
        else :
            return min + (delta % range ) -1
        return min + int_value%(max - min) -1
    elif int_value < min: # ta errado pra valor grande
        delta = min-int_value
        if delta % range == 0:
            return min
        else:
            return max - (delta%range)+1
    else:
        return int_value
    
def has_number(lista):
    for number in range(0,10):
        for elemento in lista:
            if type(elemento) == str and str(number) in elemento:
                return True
    return False

def has_symbol(lista, list_texto):
    for char in lista:
        for texto in list_texto:
            if char in str(texto):
                return True
    return False


# Acorde é formado por notas e complementos. Os complementos são imutáveis e as notas são mutáveis
# ex :  C#m/D -> [4, 'm/', 5]
#   Essa estrutura de dado está armazenada em list_elementos

class Acorde:    
    def __init__(self, input):
        if type(input) == str: # está recebendo texto do acorde ex C#m
            self.list_elementos = []
            str_textoOriginal = input
            i = 0
            while i < len(str_textoOriginal):
                letra = str_textoOriginal[i]
                
                if letra in dict_notes: #achou nota
                    tom = dict_notes[letra]
                    if i < len(str_textoOriginal) - 1 and str_textoOriginal[i+1] == '#': # verifica se é sustenido
                        tom += 1
                        i += 1
                    elif i < len(str_textoOriginal) - 1 and str_textoOriginal[i+1] == 'b':  # verifica se é bemol
                        tom -= 1
                        if tom < 0:
                            tom = len(dict_notes) + tom
                        i += 1
                    i += 1
                    tom = circulate(tom) # circula o numero caso passe do intervalo [0:11]
                    self.list_elementos.append(tom)
                else: #achou complemento
                    ini_comp = i
                    while i < len(str_textoOriginal) and not(str_textoOriginal[i] in dict_notes): # continua rodando até acabar complemento
                        i+=1
                    comp = str_textoOriginal[ini_comp:i]
                    self.list_elementos.append(comp)
        elif type(input) == list: # está recebendo uma lista de elementos já certa
            self.list_elementos = input
        else:
            raise ValueError(f'Acorde input mus be str ou list only, but received {type(input)}')
        
    
    def __str__(self):
        texto = ''
        for elemento in self.list_elementos:
            if type(elemento) == int: #nota
                texto += dict_notesValue[elemento]
            else: # complemento
                texto += elemento
        return texto
    
    def __repr__(self):
        return self.__str__()
    
    def __add__(self, int_numSemitom): 
        list_tempElementos = []
        for elemento in self.list_elementos:
            if type(elemento) == int:
                elemento = circulate(elemento + int_numSemitom)
            list_tempElementos.append(elemento) 
        
        return Acorde(list_tempElementos)
    
    def __sub__(self, int_numSemitom):
        return self + (-int_numSemitom)
    
    def __eq__(self, value):
        if type(value) != Acorde:
            return False
        return self.list_elementos ==  value.list_elementos
            
    def is_acorde(self):
        if len(self.list_elementos) < 1: # lista vazia
            return False
        if not(self.list_elementos[0] in dict_notesValue): #verifica se a primeira letra é nota
            return False
        # daqui pra baixo, a primeira letra é uma nota
        if len(self.list_elementos) == 1 : # acorde só com uma letra ex D, C, F
            return True
        if has_symbol(['#', '/', '+', '°'], self.list_elementos) or has_number(self.list_elementos): #verifica se tem sustenido ou numero na lista de elementos
            return True
        if len(self.list_elementos) == 2 and  'm' in self.list_elementos: # acordes com 2 letras ex. Em, Dm Bb
            return True
        return False
    



if __name__ == '__main__':
    print('Teste de acordes')
    str_acorde1 = 'C'
    acorde_1 = Acorde(str_acorde1)

    str_acorde2 = 'C#m7+/E'
    acorde_2 = Acorde(str_acorde2)

    str_acorde3 = 'Em'
    acorde_3 = Acorde(str_acorde3)

    str_acorde4 = 'A#'
    acorde_4 = Acorde(str_acorde4)

    str_acorde5 = 'Gb'
    acorde_5 = Acorde(str_acorde5)

    print(f'Acorde {str_acorde1} : {acorde_1}')
    print(f'Acorde {str_acorde2} : {acorde_2}')
    print(f'Acorde {str_acorde3} : {acorde_3}')
    print(f'Acorde {str_acorde4} : {acorde_4}')
    print(f'Acorde {str_acorde5} : {acorde_5}')
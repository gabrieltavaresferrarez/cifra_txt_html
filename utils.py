from acordes import Acorde

def size_linha(list_linha:list):
  int_size = 0
  for element in list_linha:
    int_size+= len(str(element))
  return int_size

def is_linha_acordes(list_linha:list):
  if len(list_linha) == 0:
     return False
  for element in list_linha:
    if type(element) == Acorde:
      return True
  return False

def is_linha_texto(list_linha:list):
  if len(list_linha) == 0:
     return False
  for element in list_linha:
    if type(element) != str:
      return False
  return True
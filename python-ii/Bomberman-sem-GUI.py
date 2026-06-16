import os       # Para limpar a tela do terminal
import json     # Para manipular arquivos JSON
import random   # Para criar aleatoriedade
import time     # Para controlar o tempo


# CONFIGURAÇÕES

LARGURA_MAPA = 15
ALTURA_MAPA = 10
ARQUIVO_ESTADO = "estado.json"
JOGADOR = "J"
INIMIGO = "X"
BOMBA = "B"
PAREDE = "#"
BLOCO = "*"
VAZIO = " "


# ESTADO GLOBAL

class EstadoGlobal:
   def __init__(self):
       self.partidas = 0
       self.media_turnos = 0
       self.media_bombas = 0
       self.ultima_causa = ""
       self.ultimo_turno = 0
       self.taxa_destruicao = 0

   def carregar(self):
       if not os.path.exists(ARQUIVO_ESTADO):
           return
       try:
           with open(ARQUIVO_ESTADO, "r") as arquivo:
               dados = json.load(arquivo)
           self.__dict__.update(dados)
       except:
           print("Erro ao carregar estado.")

   def salvar(self):
       with open(ARQUIVO_ESTADO, "w") as arquivo:
           json.dump(self.__dict__, arquivo, indent=4)

   def atualizar(self, turnos, bombas, causa, destruidos, total_blocos):
       self.partidas += 1
       self.media_turnos = (
           (self.media_turnos * (self.partidas - 1)) + turnos
       ) / self.partidas
       self.media_bombas = (
           (self.media_bombas * (self.partidas - 1)) + bombas
       ) / self.partidas
       self.ultima_causa = causa
       self.ultimo_turno = turnos
       if total_blocos > 0:
           self.taxa_destruicao = destruidos / total_blocos


# ENTIDADES

class Jogador:
   def __init__(self, x, y):
       self.x = x
       self.y = y
       self.bombas_usadas = 0

class Inimigo:
   def __init__(self, x, y):
       self.x = x
       self.y = y

   def mover(self, jogo):
       dx, dy = random.choice([
           (0,1),(0,-1),(1,0),(-1,0)
       ])
       novo_x = self.x + dx
       novo_y = self.y + dy
       if jogo.esta_livre(novo_x, novo_y):
           self.x = novo_x
           self.y = novo_y

class Bomba:
   def __init__(self, x, y, tempo, alcance):
       self.x = x
       self.y = y
       self.tempo = tempo
       self.alcance = alcance


# JOGO

class Jogo:
   def __init__(self, estado):
       self.estado = estado
       # Dificuldade dinâmica
       self.max_turnos = 50 + int(estado.media_turnos // 5)
       self.alcance_bomba = 2 + int(estado.taxa_destruicao * 2)
       self.tempo_bomba = max(2, 5 - int(estado.media_turnos // 20))
       self.frequencia_inimigos = max(5, 15 - int(estado.media_turnos // 3))
       self.inimigos = []
       self.bombas = []
       self.turno = 0
       self.blocos_destruidos = 0
       self.gerar_mapa()
       self.criar_jogador()
       self.criar_inimigos()


   # MAPA

   def gerar_mapa(self):
       self.mapa = [
           [VAZIO for _ in range(LARGURA_MAPA)]
           for _ in range(ALTURA_MAPA)
       ]
       self.total_blocos = 0
       for y in range(ALTURA_MAPA):
           for x in range(LARGURA_MAPA):
               if random.random() < 0.15:
                   self.mapa[y][x] = PAREDE
               elif random.random() < 0.25 + self.estado.taxa_destruicao:
                   self.mapa[y][x] = BLOCO
                   self.total_blocos += 1

   def criar_jogador(self):
       while True:
           x = random.randint(1, LARGURA_MAPA-2)
           y = random.randint(1, ALTURA_MAPA-2)
           if self.mapa[y][x] == VAZIO:
               livres = 0
               for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                   if self.esta_livre(x+dx, y+dy):
                       livres += 1
               if livres > 0:
                   break
       self.jogador = Jogador(x,y)

   def criar_inimigos(self):
       base = 2 + int(self.estado.media_turnos // 20)
       for _ in range(base):
           self.criar_inimigo()

   def criar_inimigo(self):
       while True:
           x = random.randint(0, LARGURA_MAPA-1)
           y = random.randint(0, ALTURA_MAPA-1)
           if self.esta_livre(x,y):
               self.inimigos.append(Inimigo(x,y))
               break

   
   # AUXILIARES
   
   def esta_livre(self, x, y):
       if x < 0 or y < 0:
           return False
       if x >= LARGURA_MAPA or y >= ALTURA_MAPA:
           return False
       return self.mapa[y][x] == VAZIO

   def renderizar(self):
       os.system("clear" if os.name=="posix" else "cls")
       temp = [linha[:] for linha in self.mapa]
       temp[self.jogador.y][self.jogador.x] = JOGADOR
       for i in self.inimigos:
           temp[i.y][i.x] = INIMIGO
       for b in self.bombas:
           temp[b.y][b.x] = BOMBA
       print("="*30)
       print(f"Turno: {self.turno}/{self.max_turnos}")
       print(f"Bombas: {self.jogador.bombas_usadas}")
       print(f"Tempo de ativação (Bombas): {self.tempo_bomba}  |  Alcance (Bombas): {self.alcance_bomba}")
       print("="*30)
       for linha in temp:
           print("".join(linha))

   
   # JOGADAS
   
   def acao_jogador(self):
       comando = input("WASD = mover | B = bomba | Q = sair: ").lower()
       dx = dy = 0
       if comando == "w": dy = -1
       if comando == "s": dy = 1
       if comando == "a": dx = -1
       if comando == "d": dx = 1

       if dx != 0 or dy != 0:
           novo_x = self.jogador.x + dx
           novo_y = self.jogador.y + dy
           if self.esta_livre(novo_x, novo_y):
               self.jogador.x = novo_x
               self.jogador.y = novo_y

       if comando == "b":
           self.bombas.append(
               Bomba(
                   self.jogador.x,
                   self.jogador.y,
                   self.tempo_bomba,
                   self.alcance_bomba
               )
           )
           self.jogador.bombas_usadas += 1

       if comando == "q":
           return False
       return True

   
   # BOMBAS
   
   def atualizar_bombas(self):
       explodidas = []
       for b in self.bombas:
           b.tempo -= 1
           if b.tempo <= 0:
               explodidas.append(b)

       for b in explodidas:
           self.explodir(b)
           self.bombas.remove(b)

   def explodir(self, bomba):
       pontos = [(bomba.x, bomba.y)]
       for i in range(1, bomba.alcance+1):
           pontos += [
               (bomba.x+i, bomba.y),
               (bomba.x-i, bomba.y),
               (bomba.x, bomba.y+i),
               (bomba.x, bomba.y-i)
           ]

       for x,y in pontos:
           if 0 <= x < LARGURA_MAPA and 0 <= y < ALTURA_MAPA:
               if self.mapa[y][x] == BLOCO:
                   self.mapa[y][x] = VAZIO
                   self.blocos_destruidos += 1

       self.inimigos = [
           i for i in self.inimigos
           if (i.x, i.y) not in pontos
       ]

       if (self.jogador.x, self.jogador.y) in pontos:
           raise Exception("explosao")

   
   # INIMIGOS
   
   def atualizar_inimigos(self):
       for i in self.inimigos:
           i.mover(self)
           if i.x == self.jogador.x and i.y == self.jogador.y:
               raise Exception("inimigo")

       if self.turno % self.frequencia_inimigos == 0:
           self.criar_inimigo()


   # LOOP PRINCIPAL

   def executar(self):
       try:
           while self.turno < self.max_turnos:
               self.renderizar()
               if not self.acao_jogador():
                   break
               self.atualizar_bombas()
               self.atualizar_inimigos()
               self.turno += 1
               time.sleep(0.1)

           causa = "vitoria"

       except Exception as e:
           if str(e) == "explosao":
               causa = "explosao"
           elif str(e) == "inimigo":
               causa = "inimigo"
           else:
               causa = "erro"

       self.finalizar(causa)


   # FINAL

   def finalizar(self, causa):
       print("\nFim de jogo!")
       print("Causa:", causa)
       print("Turnos:", self.turno)

       self.estado.atualizar(
           self.turno,
           self.jogador.bombas_usadas,
           causa,
           self.blocos_destruidos,
           self.total_blocos
       )
       self.estado.salvar()
       input("\nPressione ENTER para sair...")


# MAIN

def main():
   estado = EstadoGlobal()
   estado.carregar()
   jogo = Jogo(estado)
   jogo.executar()

if __name__ == "__main__":
   main()
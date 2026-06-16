import tkinter as tk
import random
import json
import os

LARGURA_MAPA = 15
ALTURA_MAPA = 10
TAMANHO_BASE = 40
ARQUIVO_ESTADO = "estado.json"

PAREDE = "#"
BLOCO = "*"
VAZIO = " "

class EstadoGlobal:
    def __init__(self):
        self.partidas = 0
        self.media_turnos = 0
        self.media_bombas = 0
        self.ultima_causa = ""
        self.ultimo_turno = 0
        self.taxa_destruicao = 0

    def carregar(self):
        if os.path.exists(ARQUIVO_ESTADO):
            with open(ARQUIVO_ESTADO) as f:
                self.__dict__.update(json.load(f))

    def salvar(self):
        with open(ARQUIVO_ESTADO, "w") as f:
            json.dump(self.__dict__, f, indent=4)

    def atualizar(self, turnos, bombas, causa, destruidos, total):
        self.partidas += 1
        self.media_turnos = ((self.media_turnos*(self.partidas-1))+turnos)/self.partidas
        self.media_bombas = ((self.media_bombas*(self.partidas-1))+bombas)/self.partidas
        self.ultima_causa = causa
        self.ultimo_turno = turnos
        if total > 0:
            self.taxa_destruicao = destruidos / total

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
        dx, dy = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
        nx = self.x + dx
        ny = self.y + dy
        if jogo.esta_livre(nx, ny):
            self.x, self.y = nx, ny

class Bomba:
    def __init__(self, x, y, tempo, alcance):
        self.x = x
        self.y = y
        self.tempo = tempo
        self.alcance = alcance

class Jogo:
    def __init__(self, estado):
        self.estado = estado
        self.turno = 0
        self.max_turnos = 50
        self.tempo_bomba = 3
        self.alcance_bomba = 2

        self.inimigos = []
        self.bombas = []

        self.blocos_destruidos = 0
        self.gerar_mapa()
        self.criar_jogador()
        self.criar_inimigos()

    def gerar_mapa(self):
        self.mapa = [[VAZIO for _ in range(LARGURA_MAPA)] for _ in range(ALTURA_MAPA)]
        self.total_blocos = 0
        for y in range(ALTURA_MAPA):
            for x in range(LARGURA_MAPA):
                if random.random() < 0.15:
                    self.mapa[y][x] = PAREDE
                elif random.random() < 0.25:
                    self.mapa[y][x] = BLOCO
                    self.total_blocos += 1

    def criar_jogador(self):
        self.jogador = Jogador(1,1)

    def criar_inimigos(self):
        for _ in range(3):
            while True:
                x = random.randint(0, LARGURA_MAPA-1)
                y = random.randint(0, ALTURA_MAPA-1)
                if self.esta_livre(x,y):
                    self.inimigos.append(Inimigo(x,y))
                    break

    def esta_livre(self, x, y):
        return 0 <= x < LARGURA_MAPA and 0 <= y < ALTURA_MAPA and self.mapa[y][x] == VAZIO

    def acao_jogador(self, comando):
        dx = dy = 0
        if comando == "UP": dy = -1
        if comando == "DOWN": dy = 1
        if comando == "LEFT": dx = -1
        if comando == "RIGHT": dx = 1

        if dx or dy:
            nx = self.jogador.x + dx
            ny = self.jogador.y + dy
            if self.esta_livre(nx, ny):
                self.jogador.x = nx
                self.jogador.y = ny

        if comando == "b":
            self.bombas.append(Bomba(self.jogador.x, self.jogador.y, self.tempo_bomba, self.alcance_bomba))
            self.jogador.bombas_usadas += 1

    def atualizar(self):
        self.turno += 1

        for b in self.bombas[:]:
            b.tempo -= 1
            if b.tempo <= 0:
                self.explodir(b)
                self.bombas.remove(b)

        for i in self.inimigos:
            i.mover(self)
            if i.x == self.jogador.x and i.y == self.jogador.y:
                return "inimigo"

        return None

    def explodir(self, bomba):
        pontos = [(bomba.x, bomba.y)]
        for i in range(1, bomba.alcance+1):
            pontos += [(bomba.x+i, bomba.y),(bomba.x-i, bomba.y),
                       (bomba.x, bomba.y+i),(bomba.x, bomba.y-i)]

        for x,y in pontos:
            if 0 <= x < LARGURA_MAPA and 0 <= y < ALTURA_MAPA:
                if self.mapa[y][x] == BLOCO:
                    self.mapa[y][x] = VAZIO
                    self.blocos_destruidos += 1

        self.inimigos = [i for i in self.inimigos if (i.x, i.y) not in pontos]

        if (self.jogador.x, self.jogador.y) in pontos:
            raise Exception("explosao")

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PIG GUI")

        self.estado = EstadoGlobal()
        self.estado.carregar()

        self.frame = tk.Frame(root)
        self.frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.painel = tk.Frame(self.frame, width=220)
        self.painel.pack(side="right", fill="y")

        self.label_status = tk.Label(self.painel, text="", justify="left")
        self.label_status.pack(pady=10)

        self.label_info = tk.Label(self.painel, text="")
        self.label_info.pack()

        self.root.bind("<Key>", self.tecla)
        self.root.bind("<Configure>", self.redimensionar)

        self.tamanho = TAMANHO_BASE
        self.pausado = False
        self.fim_de_jogo = False
        self.mensagem_fim = ""

        self.menu()

    def redimensionar(self, event):
        largura = self.canvas.winfo_width()
        altura = self.canvas.winfo_height()
        self.tamanho = min(largura // LARGURA_MAPA, altura // ALTURA_MAPA)
        if hasattr(self, "jogo"):
            self.draw()

    def limpar_botoes(self):
        for attr in ["btn_pause", "btn_restart", "btn_jogar", "btn_sair"]:
            if hasattr(self, attr):
                getattr(self, attr).destroy()
                delattr(self, attr)

    def menu(self):
        self.canvas.delete("all")
        self.limpar_botoes()

        self.btn_jogar = tk.Button(self.painel,text="Novo Jogo",command=self.start)
        self.btn_jogar.pack(pady=5)

        self.btn_sair = tk.Button(self.painel,text="Sair",command=self.root.quit)
        self.btn_sair.pack(pady=5)

        # AGORA STATUS MOSTRA ESTADO PERSISTENTE
        status_texto = (
            f"Partidas: {self.estado.partidas}\n"
            f"Média Turnos: {self.estado.media_turnos:.1f}\n"
            f"Média Bombas: {self.estado.media_bombas:.1f}\n"
            f"Última causa: {self.estado.ultima_causa}"
        )

        self.label_status.config(text=status_texto)
        self.label_info.config(text="")

    def start(self):
        self.limpar_botoes()

        self.jogo = Jogo(self.estado)
        self.fim_de_jogo = False
        self.pausado = False
        self.mensagem_fim = ""

        self.btn_pause = tk.Button(self.painel, text="Pausar", command=self.toggle_pause)
        self.btn_pause.pack(pady=5)

        self.draw()
        self.atualizar_status()

    def toggle_pause(self):
        self.pausado = not self.pausado
        self.atualizar_status()

    def atualizar_status(self):
        if self.fim_de_jogo:
            texto = "Finalizado"
        elif self.pausado:
            texto = "Pausado"
        else:
            texto = "Em execução"
        self.label_status.config(text=f"Status: {texto}")

    def draw(self):
        self.canvas.delete("all")

        for y in range(ALTURA_MAPA):
            for x in range(LARGURA_MAPA):
                cor = "white"
                if self.jogo.mapa[y][x] == PAREDE:
                    cor = "black"
                elif self.jogo.mapa[y][x] == BLOCO:
                    cor = "gray"

                self.canvas.create_rectangle(
                    x*self.tamanho, y*self.tamanho,
                    (x+1)*self.tamanho, (y+1)*self.tamanho,
                    fill=cor
                )

        j = self.jogo.jogador
        self.canvas.create_rectangle(
            j.x*self.tamanho, j.y*self.tamanho,
            (j.x+1)*self.tamanho, (j.y+1)*self.tamanho,
            fill="blue"
        )

        for i in self.jogo.inimigos:
            self.canvas.create_rectangle(
                i.x*self.tamanho, i.y*self.tamanho,
                (i.x+1)*self.tamanho, (i.y+1)*self.tamanho,
                fill="red"
            )

        for b in self.jogo.bombas:
            self.canvas.create_rectangle(
                b.x*self.tamanho, b.y*self.tamanho,
                (b.x+1)*self.tamanho, (b.y+1)*self.tamanho,
                fill="purple"
            )

        if self.fim_de_jogo:
            largura = self.canvas.winfo_width()
            altura = self.canvas.winfo_height()

            x = largura // 2
            y = altura // 2

            self.canvas.create_rectangle(
                x - 150, y - 60,
                x + 150, y + 60,
                fill="white",
                outline="black"
            )

            self.canvas.create_text(
                x,
                y,
                text=self.mensagem_fim,
                font=("Arial", 20, "bold"),
                fill="black"
            )

        self.label_info.config(
            text=f"Turnos: {self.jogo.turno}\nInimigos: {len(self.jogo.inimigos)}"
        )

    def tecla(self, event):
        if not hasattr(self, "jogo") or self.fim_de_jogo or self.pausado:
            return

        tecla = event.keysym

        comando = None
        if tecla in ["Up","Down","Left","Right"]:
            comando = tecla.upper()
        if event.char == "b":
            comando = "b"

        if not comando:
            return

        try:
            self.jogo.acao_jogador(comando)
            self.draw()

            fim = self.jogo.atualizar()

            self.draw()

            if fim:
                self.end(fim)
            elif self.jogo.turno >= self.jogo.max_turnos:
                self.end("vitoria")

        except Exception as e:
            self.end(str(e))

    def end(self, causa):
        self.fim_de_jogo = True
        self.mensagem_fim = f"FIM DE JOGO\n{causa}"

        self.estado.atualizar(
            self.jogo.turno,
            self.jogo.jogador.bombas_usadas,
            causa,
            self.jogo.blocos_destruidos,
            self.jogo.total_blocos
        )
        self.estado.salvar()

        self.atualizar_status()
        self.limpar_botoes()

        self.btn_restart = tk.Button(self.painel, text="Jogar Novamente", command=self.restart)
        self.btn_restart.pack(pady=5)

        self.draw()

    def restart(self):
        self.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
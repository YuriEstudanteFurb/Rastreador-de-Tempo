import tkinter as tk
from pynput import mouse
import time
import threading
import pygetwindow as gw

# Variáveis globais
tempo_total = 0
tempo_inicial = None
movendo_mouse = False
rastreamento_ativo = False
janela_alvo = "Google Chrome"
listener = None
thread_mouse = None

# Detecta se a janela ativa é a desejada
def janela_ativa_eh_alvo():
    try:
        janela_ativa = gw.getActiveWindow()
        if janela_ativa and janela_alvo.lower() in janela_ativa.title.lower():
            return True
    except:
        pass
    return False

# Listener do mouse
def on_move(x, y):
    global tempo_inicial, movendo_mouse
    if janela_ativa_eh_alvo():
        if not movendo_mouse:
            tempo_inicial = time.time()
            movendo_mouse = True

def on_click(x, y, button, pressed):
    global tempo_total, tempo_inicial, movendo_mouse
    if not pressed and movendo_mouse:
        tempo_total += time.time() - tempo_inicial
        movendo_mouse = False

# Iniciar listener em thread separada
def iniciar_listener():
    global listener
    listener = mouse.Listener(on_move=on_move, on_click=on_click)
    listener.start()
    listener.join()

# Atualizar o tempo na interface
def atualizar_tempo():
    if rastreamento_ativo:
        total = tempo_total
        if movendo_mouse:
            total += time.time() - tempo_inicial

        minutos = int(total // 60)
        segundos = int(total % 60)

        tempo_label.config(
            text=f"Tempo total ativo: {minutos} min {segundos} s ({round(total, 1)} segundos)"
        )
    janela.after(1000, atualizar_tempo)

# Iniciar rastreamento
def iniciar_rastreamento():
    global rastreamento_ativo, thread_mouse
    if not rastreamento_ativo:
        rastreamento_ativo = True
        status_label.config(text="Rastreamento Ativo", fg="green")
        thread_mouse = threading.Thread(target=iniciar_listener)
        thread_mouse.daemon = True
        thread_mouse.start()

# Parar rastreamento
def parar_rastreamento():
    global rastreamento_ativo, listener, movendo_mouse
    rastreamento_ativo = False
    movendo_mouse = False
    if listener:
        listener.stop()
        listener = None
    status_label.config(text="Parado", fg="red")

# Interface Tkinter
janela = tk.Tk()
janela.title("Rastreamento de Atividade com o Mouse")
janela.geometry("350x200")

status_label = tk.Label(janela, text="Parado", fg="red", font=("Arial", 12))
status_label.pack(pady=10)

tempo_label = tk.Label(janela, text="Tempo total ativo: 0 min 0 s (0.0 segundos)", font=("Arial", 11))
tempo_label.pack(pady=10)

botao_iniciar = tk.Button(janela, text="Iniciar Rastreamento", command=iniciar_rastreamento)
botao_iniciar.pack(pady=5)

botao_parar = tk.Button(janela, text="Parar", command=parar_rastreamento)
botao_parar.pack(pady=5)

atualizar_tempo()
janela.mainloop()

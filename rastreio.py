import tkinter as tk
from pynput import mouse
import time
import threading
import pygetwindow as gw
import re

tempos_por_arquivo = {}
tempo_inicial = None
ultimo_movimento = time.time()  # Monitorar a última atividade
movendo_mouse = False
rastreamento_ativo = False
listener = None
thread_mouse = None
arquivo_atual = None

# Extrair nome do arquivo do título da janela (usando regex para pegar algo tipo "arquivo.psd")
def obter_arquivo_da_janela():
    try:
        janela = gw.getActiveWindow()
        if janela:
            titulo = janela.title
            match = re.search(r"([\w\- ]+\.(psd|ai|jpg|png|txt|docx|pdf))", titulo, re.IGNORECASE)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Erro ao obter nome da janela: {e}")
    return None

def on_move(x, y):
    global tempo_inicial, movendo_mouse, arquivo_atual, ultimo_movimento
    if rastreamento_ativo:
        nome_arquivo = obter_arquivo_da_janela()
        if nome_arquivo:
            arquivo_atual = nome_arquivo
            agora = time.time()

            # Retomar a contagem de tempo caso esteja pausado
            if not movendo_mouse:
                if agora - ultimo_movimento > 60:  # Alterado para 60 segundos (1 minuto) de inatividade
                    # Manter o tempo acumulado mesmo após 1 minuto
                    tempo_inicial = agora - tempos_por_arquivo.get(arquivo_atual, 0)
                else:
                    tempo_inicial = agora
                movendo_mouse = True

            ultimo_movimento = agora  # Atualiza o último movimento

def on_click(x, y, button, pressed):
    global tempo_inicial, movendo_mouse, tempos_por_arquivo, arquivo_atual, ultimo_movimento
    if not pressed and movendo_mouse and arquivo_atual:
        duracao = time.time() - tempo_inicial
        tempos_por_arquivo[arquivo_atual] = tempos_por_arquivo.get(arquivo_atual, 0) + duracao
        movendo_mouse = False
    ultimo_movimento = time.time()  # Atualiza o último clique

def iniciar_listener():
    global listener
    listener = mouse.Listener(on_move=on_move, on_click=on_click)
    listener.start()
    listener.join()

def atualizar_tempo():
    global movendo_mouse, tempo_inicial, ultimo_movimento
    total_texto = ""
    agora = time.time()

    for nome_arquivo, tempo in tempos_por_arquivo.items():
        total = tempo
        if movendo_mouse and nome_arquivo == arquivo_atual:
            # Pausa o cronômetro se inatividade for maior que 60 segundos (1 minuto)
            if agora - ultimo_movimento > 60:  # Alterado para 60 segundos
                movendo_mouse = False
            else:
                total += agora - tempo_inicial

        minutos = int(total // 60)
        segundos = int(total % 60)
        total_texto += f"{nome_arquivo}: {minutos} min {segundos} s ({round(total, 1)} seg)\n"

    if total_texto == "":
        total_texto = "Nenhum arquivo rastreado ainda."

    tempo_label.config(text=total_texto)
    janela.after(1000, atualizar_tempo)

def salvar_tempos():
    try:
        if tempos_por_arquivo:  # Certifique-se de que há tempos para salvar
            for nome_arquivo, tempo in tempos_por_arquivo.items():
                nome_txt = "tempo_" + nome_arquivo.replace(".", "_") + ".txt"
                with open(nome_txt, "w") as f:
                    f.write(f"Tempo total no arquivo {nome_arquivo}: {round(tempo, 2)} segundos")
                print(f"Salvando: {nome_txt}")
            status_label.config(text="Tempos salvos para todos os arquivos.", fg="blue")
        else:
            status_label.config(text="Nenhum tempo rastreado para salvar.", fg="red")
    except Exception as e:
        status_label.config(text=f"Erro ao salvar: {e}", fg="red")
        print(f"Erro ao salvar: {e}")

def salvar_tempos_periodicamente():
    salvar_tempos()
    if rastreamento_ativo:  # Só salva periodicamente se o rastreamento estiver ativo
        janela.after(60000, salvar_tempos_periodicamente)  # Salva a cada 60 segundos

def iniciar_rastreamento():
    global rastreamento_ativo, thread_mouse
    if not rastreamento_ativo:
        rastreamento_ativo = True
        status_label.config(text="Rastreamento Ativo", fg="green")
        thread_mouse = threading.Thread(target=iniciar_listener)
        thread_mouse.daemon = True
        thread_mouse.start()
        salvar_tempos_periodicamente()  # Inicia salvamento periódico

def parar_rastreamento():
    global rastreamento_ativo, listener, movendo_mouse
    rastreamento_ativo = False
    movendo_mouse = False
    if listener:
        listener.stop()
        listener = None
    salvar_tempos()

# Interface Tkinter
janela = tk.Tk()
janela.title("Rastreamento de Arquivos")
janela.geometry("450x300")

status_label = tk.Label(janela, text="Parado", fg="red", font=("Arial", 12))
status_label.pack(pady=10)

tempo_label = tk.Label(janela, text="Tempo nos arquivos aparecerá aqui", font=("Arial", 10), justify="left")
tempo_label.pack(pady=10)

botao_iniciar = tk.Button(janela, text="Iniciar Rastreamento", command=iniciar_rastreamento)
botao_iniciar.pack(pady=5)

botao_parar = tk.Button(janela, text="Parar e Salvar", command=parar_rastreamento)
botao_parar.pack(pady=5)

atualizar_tempo()
janela.mainloop()

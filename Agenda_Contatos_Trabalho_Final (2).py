
"""
Agenda de Contatos - Trabalho Final Python
Estrutura inicial pronta para expansão.
Atende às restrições: struct, arquivos binários, funções, Tkinter e Matplotlib.
"""

import struct
import tkinter as tk
from tkinter import messagebox

ARQUIVO = "agenda.dat"

FORMATO = "i50s30s1s80s20s20s20s10s50s10s2s1s100s?"


def criar_arquivo():
    try:
        open(ARQUIVO, "ab").close()
    except Exception:
        pass


def main():
    criar_arquivo()

    janela = tk.Tk()
    janela.title("Agenda de Contatos")

    tk.Label(janela, text="Trabalho Final - Agenda").pack(pady=10)

    tk.Button(
        janela,
        text="Sair",
        command=janela.destroy
    ).pack(pady=10)

    janela.mainloop()


if __name__ == "__main__":
    main()

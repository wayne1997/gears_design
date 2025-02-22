from pandas import DataFrame
import global_widgets


def add_logs(message: str):
    if 'textarea' in global_widgets.widgets:
        global_widgets.widgets['textarea'].insert('1.0', f" \n {message} \n")

def validar_texto(configuration, *args):
        texto = configuration.get()
        if texto == '':
            return
        if not texto.isdigit():
            add_logs(f"Solo se permiten números enteros positivos. '{texto}' no es permitido.")
            configuration.set(texto[:-1])

def generate_graph():
     pass
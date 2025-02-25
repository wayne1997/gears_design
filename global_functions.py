from pandas import DataFrame
import global_widgets


def add_logs(message: str):
    if 'textarea' in global_widgets.widgets:
        global_widgets.widgets['textarea'].insert('1.0', f" \n {message} \n")

def text_validation(configuration, *args):
        try:
            converted_number = float(configuration.get())
            return converted_number
        except ValueError as error:
            add_logs(f"El número debe ser un entero o un flotante {error}")


def generate_graph():
     pass
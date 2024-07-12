import flet as ft
import time
import os
import obswebsocket
from obswebsocket import obsws, events, requests

# OBS WebSocket connection settings
host = "192.168.1.40"
port = 4455
password = "9c1drmdDjx75lMYv"

# Global variables to track monitoring state and WebSocket connection
monitoring = False
ws = None

def main(page: ft.Page):
    page.title = "OBS Recording Monitor"
    page.window_width = 500
    page.window_height = 500
    page.window_resizable = False

    status_text = ft.Text("Estado: No iniciado", size=20, color=ft.colors.BLACK)
    ref_txt_nombre_archivo = ft.Ref[ft.TextField]()

    def update_status(status):
        status_text.value = f"Estado: {status}"
        page.update()

    def start_monitoring(e):
        global monitoring, ws
        monitoring = True
        update_status("Monitoreando...")
        ws = obsws(host, port, password)
        ws.connect()
        ws.register(on_record_state_changed, events.RecordStateChanged)
        page.add(ft.Text("Monitoreo iniciado"))
        while monitoring:
            time.sleep(1)

    def stop_monitoring(e):
        global monitoring, ws
        monitoring = False
        if ws:
            ws.disconnect()
        update_status("No iniciado")
        page.add(ft.Text("Monitoreo detenido"))

    def on_record_state_changed(event):
        if event.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STOPPED':
            rec_file = event.datain['outputPath']
            show_rename_dialog(rec_file)

    def show_rename_dialog(file_path):
        """
        Show a dialog to rename the recording file.

        :param file_path: The path of the recording file.
        """
        def rename_file(e):
            print('ref_txt_nombre', ref_txt_nombre_archivo)
            print(ref_txt_nombre_archivo.current)
            print()

            new_name = ref_txt_nombre_archivo.current.value
            if new_name:
                base, ext = os.path.splitext(file_path)
                new_file_path = os.path.join(os.path.dirname(file_path), new_name + ext)
                os.rename(file_path, new_file_path)
                update_status("Finalizado")
                dlg_modal.open = False
                page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Renombrar Grabación"),
            content=ft.Column(
                [
                    ft.Text("Ingrese un nuevo nombre para la grabación (sin extensión):"),
                    ft.TextField(ref=ref_txt_nombre_archivo, expand=True, autofocus=True)
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Renombrar", on_click=rename_file)
            ]
        )
        page.dialog = dlg_modal
        dlg_modal.open = True
        page.update()

    start_button = ft.ElevatedButton(text="Iniciar Monitoreo", on_click=start_monitoring)
    stop_button = ft.ElevatedButton(text="Detener Monitoreo", on_click=stop_monitoring)

    page.add(
        ft.Column(
            [
                status_text,
                start_button,
                stop_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

ft.app(target=main)

import time
import os

from dotenv import load_dotenv
import flet as ft
from obswebsocket import obsws, events


load_dotenv()

host = os.getenv("OBS_HOST")
port = os.getenv("OBS_PORT")
password = os.getenv("OBS_PASSWORD")

monitoring = False
ws = None


def main(page: ft.Page):
    """
    Main function of the app.

    :param page: The page object to add the app content to.
    """
    page.title = 'OBS Recording Monitor'
    page.window.width = 650
    page.window.height = 450
    page.window.resizable = False

    txt_status = ft.Text("Estado grabación: No iniciada", size=20, color=ft.colors.BLACK)
    ref_txt_nombre_archivo = ft.Ref[ft.TextField]()

    def update_status(status):
        """
        Update the recording status text.

        :param status: The new status to display.
        """
        txt_status.value = f"Estado gragbación: {status}"
        page.update()

    def start_monitoring(e):
        """
        Start monitoring the recording state.

        :param e: The event object.
        """
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
        """
        Stop monitoring the recording state.

        :param e: The event object.
        """
        global monitoring, ws
        monitoring = False
        if ws:
            ws.disconnect()
        update_status("No iniciada")
        page.add(ft.Text("Monitoreo detenido"))

    def on_record_state_changed(event):
        """
        Callback function to handle the recording state change event.

        :param event: The event object.
        """
        if event.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STOPPED':
            rec_file = event.datain['outputPath']
            show_rename_dialog(rec_file)

    def show_rename_dialog(file_path):
        """
        Show a dialog to rename the recording file.

        :param file_path: The path of the recording file.
        """
        def rename_file(e):
            new_name = ref_txt_nombre_archivo.current.value
            if new_name:
                base, ext = os.path.splitext(file_path)
                new_file_path = os.path.join(os.path.dirname(file_path), new_name + ext)
                os.rename(file_path, new_file_path)
                update_status("Finalizado")
                dlg_modal.open = False
                page.update()

        initial_file_name = os.path.basename(file_path)
        initial_file_name = os.path.splitext(initial_file_name)[0]

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Renombrar Grabación"),
            content=ft.Column(
                [
                    ft.Text("Ingrese un nuevo nombre para la grabación (sin extensión):"),
                    ft.TextField(ref=ref_txt_nombre_archivo, expand=True, autofocus=True, value=initial_file_name)
                ],
                tight=True
            ),
            actions=[
                ft.TextButton("Renombrar", on_click=rename_file)
            ]
        )
        page.overlay.append(dlg_modal)
        dlg_modal.open = True
        page.update()

    btn_start_monitoring = ft.ElevatedButton(text="Iniciar Monitoreo", on_click=start_monitoring)
    btn_stop_monitoring = ft.ElevatedButton(text="Detener Monitoreo", on_click=stop_monitoring)

    page.add(
        ft.Column(
            [
                txt_status,
                btn_start_monitoring,
                btn_stop_monitoring
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )


if __name__ == "__main__":
    ft.app(target=main)

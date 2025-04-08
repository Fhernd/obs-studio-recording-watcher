import time
import os
import json

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

    txt_status = ft.Text("Estado grabación: N/D", size=20, color=ft.colors.BLACK)
    
    ref_txt_nombre_archivo = ft.Ref[ft.TextField]()
    
    snb = ft.SnackBar(content=ft.Text(""))

    # Create references for settings fields
    ref_txt_host = ft.Ref[ft.TextField]()
    ref_txt_port = ft.Ref[ft.TextField]()
    ref_txt_password = ft.Ref[ft.TextField]()


    def update_recording_status(status):
        """
        Update the recording status text.

        :param status: The new status to display.
        """
        txt_status.value = f"Estado grabación: {status}"
        page.update()

    def start_monitoring(e):
        """
        Start monitoring the recording state.

        :param e: The event object.
        """
        global monitoring, ws

        btn_start_monitoring.disabled = True
        btn_stop_monitoring.disabled = False

        monitoring = True
        ws = obsws(host, port, password)
        ws.connect()
        ws.register(on_record_state_changed, events.RecordStateChanged)
        
        snb.content = ft.Text("Monitoreando iniciado")
        snb.open = True
        page.update()
        
        while monitoring:
            time.sleep(1)

    def stop_monitoring(e):
        """
        Stop monitoring the recording state.

        :param e: The event object.
        """
        global monitoring, ws
        monitoring = False

        btn_start_monitoring.disabled = False
        btn_stop_monitoring.disabled = True
        
        if ws:
            ws.disconnect()
        
        snb.content = ft.Text("Monitoreo detenido")
        snb.open = True
        page.update()

    def on_record_state_changed(event):
        """
        Callback function to handle the recording state change event.

        :param event: The event object.
        """
        if event.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STARTING':
            update_recording_status("En progreso")
        elif event.datain['outputState'] == 'OBS_WEBSOCKET_OUTPUT_STOPPED':
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
                update_recording_status("Finalizada")
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

    def on_window_event(e):
        """
        Callback function to handle the close event.

        :param e: The event object.
        """
        def handle_close(e):
            global monitoring, ws

            if e.control.text == "Yes":
                monitoring = False
                if ws:
                    ws.disconnect()
                page.window.destroy()
            else:
                page.close(dlg_modal)

        if e.type == ft.WindowEventType.CLOSE:
            dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text('Confirmación de cierre'),
                content=ft.Text('¿Está seguro que desea cerrar la aplicación?'),
                actions=[
                    ft.TextButton("Yes", on_click=handle_close),
                    ft.TextButton("No", on_click=handle_close),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            page.open(dlg_modal)

    def open_settings(e):
        """
        Open the settings modal dialog.

        :param e: The event object.
        """
        # Initialize the fields with current values
        ref_txt_host.current.value = host
        ref_txt_port.current.value = port
        ref_txt_password.current.value = password
        
        settings_dialog.open = True
        page.update()
        
    def save_settings(e):
        """
        Save the settings to the .env file.

        :param e: The event object.
        """
        global host, port, password
        
        new_host = ref_txt_host.current.value
        new_port = ref_txt_port.current.value
        new_password = ref_txt_password.current.value
        
        # Update global variables
        host = new_host
        port = new_port
        password = new_password
        
        # Save to .env file
        with open(".env", "w") as env_file:
            env_file.write(f'OBS_HOST="{new_host}"\n')
            env_file.write(f'OBS_PORT={new_port}\n')
            env_file.write(f'OBS_PASSWORD="{new_password}"\n')
        
        settings_dialog.open = False
        
        snb.content = ft.Text("Configuración guardada correctamente")
        snb.open = True
        page.update()

    btn_start_monitoring = ft.ElevatedButton(text="Iniciar Monitoreo", on_click=start_monitoring, color=ft.colors.WHITE, bgcolor=ft.colors.GREEN_500)
    btn_stop_monitoring = ft.ElevatedButton(text="Detener Monitoreo", on_click=stop_monitoring, color=ft.colors.WHITE, bgcolor=ft.colors.RED_500)
    btn_stop_monitoring.disabled = True
    
    # Create the settings icon button
    btn_settings = ft.IconButton(
        icon=ft.icons.SETTINGS,
        icon_color=ft.colors.BLUE_GREY_400,
        tooltip="Configuración",
        on_click=open_settings
    )
    
    # Create the settings dialog
    settings_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Configuración de conexión OBS"),
        content=ft.Column(
            [
                ft.Text("Configure los parámetros de conexión con OBS:"),
                ft.TextField(ref=ref_txt_host, label="Host", value=host),
                ft.TextField(ref=ref_txt_port, label="Puerto", value=port),
                ft.TextField(ref=ref_txt_password, label="Contraseña", value=password, password=True),
            ],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(settings_dialog, "open", False)),
            ft.TextButton("Guardar", on_click=save_settings),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(txt_status)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.Row(
                    [
                        ft.Container(btn_start_monitoring),
                        ft.Container(btn_stop_monitoring)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                # Add a spacer to push the settings icon to the bottom
                ft.Container(height=100),
                ft.Row(
                    [btn_settings],
                    alignment=ft.MainAxisAlignment.END
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        )
    )

    page.overlay.append(snb)
    page.overlay.append(settings_dialog)
    page.window.prevent_close = True
    page.window.on_event = on_window_event


if __name__ == "__main__":
    ft.app(target=main)

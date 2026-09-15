import flet as ft
import cv2
import asyncio
import time
import os
from pyzbar.pyzbar import decode

os.environ["GDK_BACKEND"] = "x11"


async def main(page: ft.Page):
    page.title = "Controle de Refeitório"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    texto_status = ft.Text("Aguardando leitura...", size=20, weight="bold", color="blue700")

    camera_image = ft.RawImage(
        width=600,
        height=480,
        fit=ft.BoxFit.CONTAIN,
        filter_quality=ft.FilterQuality.MEDIUM,
    )

    def gerar_relatorio(e):
        texto_status.value = "Relatório gerado com sucesso!"
        texto_status.color = "blue700"
        page.update()

    page.add(
        ft.Row(
            [ft.Icon("restaurant", size=40), ft.Text("Refeitório", size=30, weight="bold")],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        ft.Divider(),
        camera_image,
        ft.Container(height=10),
        texto_status,
        ft.Container(height=20),
        ft.Button("Gerar Relatório do Dia", icon="insert_drive_file", on_click=gerar_relatorio),
    )

    running = True

    async def atualiza_camera():
        nonlocal running

        while camera_image.page is None:
            await asyncio.sleep(0.01)

        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        if not cap.isOpened():
            texto_status.value = "Erro: não foi possível abrir a câmera."
            texto_status.color = "red700"
            page.update()
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        ultimo_codigo = ""
        tempo_ultima_leitura = 0

        while running:
            sucesso, frame = cap.read()
            if not sucesso:
                await asyncio.sleep(0.05)
                continue

            codigos = decode(frame)
            for codigo in codigos:
                texto_qr = codigo.data.decode("utf-8")
                (x, y, w, h) = codigo.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

                if texto_qr != ultimo_codigo or (time.time() - tempo_ultima_leitura) > 3:
                    ultimo_codigo = texto_qr
                    tempo_ultima_leitura = time.time()
                    texto_status.value = f"Liberado: {texto_qr}"
                    texto_status.color = "green700"
                    page.update()

            frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            try:
                await camera_image.render(frame_rgba)
            except (RuntimeError, TimeoutError):
                break

            await asyncio.sleep(0.066)

        cap.release()

    # Usar asyncio.create_task diretamente (como nos exemplos oficiais)
    asyncio.create_task(atualiza_camera())


ft.run(main, view=ft.AppView.WEB_BROWSER)
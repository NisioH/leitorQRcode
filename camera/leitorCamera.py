import cv2
from pyzbar import pyzbar


class LeitorCamera:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None

    def iniciar(self):
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def ler_frame_e_qr(self):
        if not self.cap or not self.cap.isOpened():
            return None, None

        ret, frame = self.cap.read()
        if not ret:
            return None, None

        texto_qr = None
        codigos = pyzbar.decode(frame)

        for codigo in codigos:
            texto_qr = codigo.data.decode('utf-8')

            (x, y, w, h) = codigo.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
            cv2.putText(frame, "LIDO!", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        return frame, texto_qr

    def liberar(self):
        if self.cap:
            self.cap.release()

    def alternar_camera(self):
        self.liberar()
        self.camera_id = 1 if self.camera_id == 0 else 0
        self.iniciar()
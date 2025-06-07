import qrcode
from qrcode.constants import ERROR_CORRECT_H
import io
from PIL import Image
import base64


def qr_code_creation(link):
    qr = qrcode.QRCode(
        version=10,          # Размер матрицы (от 1 до 40)
        error_correction=ERROR_CORRECT_H,  # Коррекция ошибок (от 7% до 30%)
        box_size=15,         # Размер квадратов в пикселях
        border=6             # Толщина границы (минимум 4)
    )

    qr.add_data(str(link))
    qr.make(fit=True)

    # Можно задать RGB цвета
    img = qr.make_image(fill_color=(75, 0, 75), back_color=(190, 190, 255))
    img.save('qrcode.jpg')
    # pil_image = Image.open('qrcode.jpg')
    # byte_image = io.BytesIO()
    # pil_image.save(byte_image, format='JPEG')
    # byte_image.seek(0)
    # base64_image = base64.b64encode(byte_image.read()).decode('utf-8')
    return ()
# print('qrcode.png')

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


def send_email(path):
    try:
        # Подключение через SSL
        server = smtplib.SMTP_SSL('smtp.hoster.ru', 465)
        server.ehlo()  # Идентификация
        server.login('verification@pro-metrica.ru', 'K9:&wwW%37h5B+')
        print("Подключение через SSL успешно")

        # Пример отправки письма
        msg = MIMEMultipart()
        msg['From'] = 'verification@pro-metrica.ru'
        # msg['To'] = 'zaharov@smcmera.ru'
        msg['To'] = 'engineer@pro-metrica.ru'
        msg['Bcc'] = 'sergey.mishin@pro-metrica.ru'
        msg['Subject'] = 'Данные в Аршин. Прометрика'

        # Текст письма
        body = ''
        msg.attach(MIMEText(body, 'plain'))
        all_recipients = [
            # 'zaharov@smcmera.ru',
            'engineer@pro-metrica.ru',
            'sergey.mishin@pro-metrica.ru'
        ]

        # Добавляем вложения
        files_to_attach = [path]

        for filename in files_to_attach:
            try:
                # Открываем файл в бинарном режиме
                with open(filename, "rb") as attachment:
                    # Создаем объект MIMEBase
                    part = MIMEBase('application', "octet-stream")
                    part.set_payload(attachment.read())

                    # Кодируем в base64
                    encoders.encode_base64(part)

                    # Добавляем заголовок
                    part.add_header(
                        'Content-Disposition',
                        f"attachment; filename= {os.path.basename(filename)}",
                    )

                    # Прикрепляем к сообщению
                    msg.attach(part)
            except FileNotFoundError:
                print(f"Файл {filename} не найден")
            except Exception as e:
                print(f"Ошибка при добавлении файла {filename}: {str(e)}")

        server.sendmail(
            'verification@pro-metrica.ru',
            all_recipients,
            msg.as_string()
        )

    except Exception as e:
        print(f"Ошибка подключения через SSL: {str(e)}")

    return


if __name__ == '__main__':
    send_email('files_for_verification/for_verification_2025-08-10_6.csv')

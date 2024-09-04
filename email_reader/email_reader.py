"""Инкапсулирует подулючение и выполнение действий
с почтой и сообщениями"""

import imaplib
import smtplib
import email
import os
import mimetypes
import logging


from typing import  Any
from dataclasses import dataclass

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import Message

from email.header import make_header
from email.header import decode_header


def reconnect_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error("Connect ERROR", str(e))
            args[0].connect()
            return func(*args, **kwargs)
    return wrapper

@dataclass
class EmailsPost:
    """Класс обертка для соединения и работы с электронной почтой"""

    email_login: str
    email_password: str

    imap_server: str
    imap_port: int
    smtp_server: str
    smtp_port: int

    mail_box: Any = None
    mail: Any = None

    timeout: int = 60
    counter_attempt: int = 10

    def connect(self) -> bool:
        """Соединение с почтовым ящиком"""
        counter_post = 0
        while counter_post < 10:
            try:
                counter_post += 1
                self.mail = imaplib.IMAP4_SSL(self.imap_server, timeout=60)
                break
            except Exception as e:
                logging.error("Connect ERROR", str(e))
        result = list(self.mail.login(self.email_login, self.email_password))

        if "OK" in result:
            return True
        else:
            return False

    def check_empty(self):
        """Проверяет есть ли непрочитанные сообщения"""
        if len(self.list_uid_email) == 0:
            return True
        return False

    def get_id_late_email(self):
        """Возвращает uid последнего непрочитанного сообщения"""
        try:
            return self.list_uid_email[-1]
        except Exception as e:
            print("GetIdLateEmail ERROR", str(e))

    @reconnect_decorator
    def update_email(self, filtr="UNSEEN"):
        """Обновляет список непрочитанных сообщений"""
        # counter_post = 0
        self.connect()
        # while counter_post < 10:
        #     try:
        #         counter_post += 1
        #         self.mail = imaplib.IMAP4_SSL(self.imap_server, timeout=60)
        #         break
        #     except Exception as e:
        #         logging.error("UpdateUnreadEmail ERROR:", str(e))
        #         counter_post += 1

        # self.mail.login(self.email_login, self.email_password)
        # print(self.mail.list())
        self.mail.select(self.mail_box)
        _, data = self.mail.uid("search", None, filtr)
        self.list_uid_email = data[0].split()

    def get_folders(self) -> tuple[str, bytes]:
        return self.mail.list()

    @reconnect_decorator
    def select_folders(self, folders_name: str) -> None:
        self.mail_box = folders_name
        if self.mail is None:
            self.connect()
        self.mail.select(self.mail_box)

    def get_count_unread_email(self):
        if self.list_uid_email is None:
            self.update_email()
        return len(self.list_uid_email)

    def get_email(self, id: bytes):
        """Получает сообщение по id"""
        _, data = self.mail.uid("fetch", id, "(RFC822)")
        raw_email = data[0][1]
        try:
            return email.message_from_string(raw_email)
        except TypeError:
            return email.message_from_bytes(raw_email)

    def get_from_email(self, email_message: Message):
        """Возвращает email отправителя"""
        email_address = make_header(decode_header(email_message["From"]))
        email_address = str(email_address)
        pos_left_br = email_address.find("<") + 1
        pos_rigth_br = email_address.find(">")
        if pos_rigth_br == -1:
            return email_address
        return email_address[pos_left_br:pos_rigth_br]

    def get_subject_email(self, email_message: Message):
        """Возвращает тему письма"""
        subj = email_message["Subject"]
        if str(subj) != "None":
            return make_header(decode_header(email_message["Subject"]))
        return subj

    def get_date_email(self, email_message: Message):
        """Возвращает дату письма"""
        date = email_message["date"]
        if str(date) != "None":
            return make_header(decode_header(email_message["Date"]))
        return date

    def get_file(self, email_message: Message, way_save: str):
        """Возвращает вложенный файл в письмо и сохраняет в way_save"""
        filename = ""
        for part in email_message.walk():
            if "application" in part.get_content_type():
                bffr_filename = part.get_filename()
                bffr_filename = str(make_header(decode_header(bffr_filename)))
                bffr_filename = bffr_filename.lower()
                if ".xls" in bffr_filename or ".xlsx" in bffr_filename:
                    filename = bffr_filename
                    if not (filename):
                        filename = "test.txt"
                    fp = open(os.path.join(way_save, filename), "wb")
                    fp.write(part.get_payload(decode=1))
                    fp.close
                    break
                else:
                    continue
        return filename

    def get_body(self, email_message: Message):
        """Возвращает тело письма"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                try:
                    body += part.get_payload(decode=True).decode()
                except Exception as e:
                    logging.error("GetBody ERROR: " + str(e))
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except Exception as e:
                logging.error("GetBody ERROR: " + str(e))
                body = ""
        return body

    def create_message(
        self, email_from: str, email_to: str, body: str, subject: str, filepath: str
    ):
        """Создает сообщение для отправки"""
        msg = MIMEMultipart()
        msg["From"] = email_from
        msg["To"] = email_to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        filename = os.path.basename(filepath)

        if os.path.isfile(filepath):
            ctype, encoding = mimetypes.guess_type(filepath)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            if maintype == "text":
                with open(filepath) as fp:
                    file = MIMEText(fp.read(), _subtype=subtype)
                    fp.close()
            else:
                with open(filepath, "rb") as fp:
                    file = MIMEBase(maintype, subtype)
                    file.set_payload(fp.read())
                    fp.close()
                email.encoders.encode_base64(file)
        if len(filename) and os.path.isfile(f"{filepath}"):
            file.add_header("Content-Disposition", "attachment", filename=filename)
            msg.attach(file)
        return msg

    @reconnect_decorator
    def send_email(self, msg: MIMEMultipart):
        """Отправляет сообщение"""
        counter_post = 0
        while True:
            try:
                counter_post += 1
                smpt_obj = smtplib.SMTP_SSL(
                    self.smtp_server, self.smtp_port, timeout=60
                )
                break
            except Exception as e:
                logging.error("SendEmail ERROR", str(e))
        smpt_obj.login(self.email_login, self.email_password)
        smpt_obj.send_message(msg)
        smpt_obj.close()

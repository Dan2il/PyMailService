"""Инкапсулирует подулючение и выполнение действий
с почтой и сообщениями"""

import imaplib
import smtplib
import email
import os
import mimetypes

from typing import Any
from dataclasses import dataclass

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import Message
from email.header import Header

from email.header import make_header
from email.header import decode_header

def reconnect_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            counter_post = 0
            while counter_post < args[0].counter_attempt:
                check = args[0].connect
                if check is True:
                    break
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
    list_uid_email: Any = None

    timeout: int = 60
    counter_attempt: int = 10

    @property
    def connect(self) -> bool | tuple:
        """Инициализирует соединение с почтовым ящиком

        Returns:
            object:
                True, если подключение успешно, иначе
                Кортеж, содержащий False и исключение, если оно возникло, в процессе выполнения
        """
        try:
            counter_post = 0
            while counter_post < self.counter_attempt:
                try:
                    counter_post += 1
                    self.mail = imaplib.IMAP4_SSL(self.imap_server, timeout=self.timeout)
                    break
                except Exception as e:
                    pass
                    # logging.error("Connect ERROR", str(e))
            result = self.mail.login(self.email_login, self.email_password)
            if "OK" in result:
                return True
            else:
                return False, str()
        except Exception as e:
            return False, e

    @property
    def empty(self) -> bool:
        """
        Проверяет пустая ли выбранная папка
        Returns:
            bool: истина, если папка пуста
        """
        if len(self.list_uid_email) == 0:
            return True
        return False

    def __len__(self):
        if self.list_uid_email is None:
            return 0
        return len(self.list_uid_email)

    @reconnect_decorator
    def get_uid_last_email(self) -> bytes:
        """Возвращает uid последнего непрочитанного сообщения

        Returns:
            bytes: содержит число-идентификатор сообщения
        """
        try:
            if len(self.list_uid_email):
                return self.list_uid_email[-1]
            else:
                return 0
        except Exception as e:
            print("GetIdLateEmail ERROR", str(e))

    @reconnect_decorator
    def update_email(self, fltr: str = "UNSEEN"):
        """Обновляет список сообщений, по умолчанию - непрочинанных"""
        # self.connect()
        self.mail.select(self.mail_box)
        _, data = self.mail.uid("search", None, fltr)
        self.list_uid_email = data[0].split()

    @reconnect_decorator
    def get_folders(self) -> tuple[str, list[bytes]]:
        return self.mail.list()

    @reconnect_decorator
    def select_folders(self, folders_name: str = 'inbox') -> None:
        self.mail_box = folders_name
        if self.mail is None:
            self.connect
        self.mail.select(self.mail_box)

    # def get_count_unread_email(self):
    #     if self.list_uid_email is None:
    #         self.update_email()
    #     return len(self.list_uid_email)

    def get_email(self, email_uid: bytes) -> Message:
        """Получает сообщение по id

        Args:
            email_uid: для получения см метод update_email или get_uid_last_email

        Returns:
            Message: базовый класс email из email.message
        """
        _, data = self.mail.uid("fetch", email_uid, "(RFC822)")
        raw_email = data[0][1]
        try:
            return email.message_from_string(raw_email)
        except TypeError:
            return email.message_from_bytes(raw_email)

    def get_from_email(self, email_message: Message) -> Header:
        """Возвращает email отправителя"""
        return make_header(decode_header(email_message["From"]))

    def get_subject_email(self, email_message: Message) -> Header:
        """Возвращает тему письма"""
        return make_header(decode_header(email_message["Subject"]))

    def get_date_email(self, email_message: Message) -> Header:
        """Возвращает дату письма"""
        return make_header(decode_header(email_message["Date"]))

    def get_file(self, email_message: Message, way_save: str = "") -> list[str]:
        """Сохраняет вложенный в письмо файл в way_save

        Args:
            way_save: путь, куда будут сохранены файлы

        Returns:
            object: лист с содержащий пути, куда были сохранены файлы
        """
        result = []
        if len(way_save) and way_save[-1] != '/':
            way_save += '/'
        for part in email_message.walk():
            if "application" in part.get_content_type():
                filename = way_save + str(make_header(decode_header(part.get_filename())))
                fp = open(os.path.join(way_save, way_save + filename), "wb")
                fp.write(part.get_payload(decode=True))
                fp.close()
                result.append(filename)
        return result

    def get_body(self, email_message: Message) -> str:
        """Возвращает тело письма"""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                try:
                    body += part.get_payload(decode=True).decode()
                except:
                    pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                pass
        return body

    def create_message(
            self, email_from: str, email_to: str, body: str, subject: str, filepath: str=None
    ) -> MIMEMultipart:
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
        counter_post += 1
        smpt_obj = smtplib.SMTP_SSL(
            self.smtp_server, self.smtp_port, timeout=self.timeout
        )
        smpt_obj.login(self.email_login, self.email_password)
        smpt_obj.send_message(msg)
        smpt_obj.close()

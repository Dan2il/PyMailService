# email_reader
Библиотека позволяет просматривать, получать и отправлять электронные письма

Фактически, класс является оберткой для imaplib и smtplib, позволяющий упростить их использование

Для начала работы, Вам нужно:
- почтовый ящик, к которому возможно подключиться через imap ssl и smtp ssl
- логин и пароль, от данного ящика
- знать imap и smtp сервер (например у яндека: imap.yandex.ru и smtp.yandex.ru, соответственно)
- знать imap и smtp порты (например у яндекса: 993 и 465 соответственно)

Пример создания обьекта класса:
```commandline
    post = EmailsPost(
        email_login=LOGIN_EMAIL,
        email_password=PASSWORD_EMAIL,
        imap_server="imap.yandex.ru",
        smtp_server="smtp.yandex.ru",
        imap_port=993,
        smtp_port=465,
    )
```
После инициализации, необходимо явно подключиться к почте:

```commandline
    check = post.connect()
    if check is True:
        print("success")
    else:
        print(check)
```

В случае успешного подключения, метод возвращает True,
в противном случае, кортеж вида:

```commandline
(False, error(b'[AUTHENTICATIONFAILED] LOGIN invalid credentials or IMAP is disabled sc=cDdQwR5MouQ0_051313_imap-production-468'))
```
Большинство методов, обернуто в декоратор, вида:

```commandline
def reconnect_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            args[0].connect()
            return func(*args, **kwargs)
    return wrapper
```
В связи с этим, скрипт попытается создать или восстановить соединение,
в случае если вы забыли сделать это явно, или в случае его отключения

Для получения писем, необходимо выбрать папку, из которой они будут получены:

```post.select_folders("inbox")```

по умолчанию, задана папка "inbox", поэтому вызов выше, будет аналогичен вызову:
```post.select_folders()```

Узнать наименования папок или их наличие можно вызовом:
```commandline
folders: tuple[str, list[bytes]] = post.get_folders()
```

Пример возвращаемого значения:
```
('OK', [b'(\\HasChildren \\Marked \\Drafts) "|" Drafts', b'(\\HasNoChildren \\Unmarked \\Templates) "|" "Drafts|template"', b'(\\HasNoChildren \\Marked \\NoInferiors) "|" INBOX', b'(\\HasNoChildren \\Unmarked) "|" Outbox', b'(\\HasNoChildren \\Marked \\Sent) "|" Sent', b'(\\HasNoChildren \\Unmarked \\Junk) "|" Spam', b'(\\HasNoChildren \\Marked \\Trash) "|" Trash'])
```

После выбора папки необходимо получить, если это первично, или обновить список писем в ней:
```commandline
post.update_email(fltr="UNSEEN")
```
по умолчанию, задан фильтр "UNSEEN", поэтому вызов выше, будет аналогичен вызову:
```commandline
post.update_email()
```
Данный вызов получит запишет в переменную self.list_uid_email uid всех непрочитанных сообщений в данной папке

Получить электронное письмо возможно следующим вызовом:
```commandline
email = post.get_email(uid)
```
uid можно получить:
```commandline
uid = post.get_uid_last_email()
```
Данный способ возвращает uid последнего письма или 0, в случае их отсутствия




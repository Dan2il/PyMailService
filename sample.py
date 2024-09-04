from setting import LOGIN_EMAIL, PASSWORD_EMAIL

from email_reader.email_reader import EmailsPost


def main():
    post = EmailsPost(
        email_login=LOGIN_EMAIL,
        email_password=PASSWORD_EMAIL,
        imap_server="imap.yandex.ru",
        smtp_server="smtp.yandex.ru",
        imap_port=993,
        smtp_port=465,
    )
    print(post.connect())
    post.select_folders("inbox")
    post.update_email()
    print(post.list_uid_email)


if __name__ == "__main__":
    main()

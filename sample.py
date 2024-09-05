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

    check = post.connect()
    if check is True:

        post.select_folders()
        post.update_email(fltr="UNSEEN")
        print(post.list_uid_email)

    else:
        print(check)



if __name__ == "__main__":
    main()

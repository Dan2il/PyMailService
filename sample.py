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

        uid = post.get_uid_last_email()

        email = post.get_email(uid)
        print(type(email))
        print(email)


        print(type(uid))
        print("uid_last", uid)



    else:
        print(check)



if __name__ == "__main__":
    main()

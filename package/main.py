from email_reader import EmailsPost

LOGIN_EMAIL = "daniilgr97@yandex.ru"
PASSWORD_EMAIL = "nqarxvjbavwyqpwk"


def main():
    post = EmailsPost(
        email_login=LOGIN_EMAIL,
        email_password=PASSWORD_EMAIL,
        imap_server="imap.yandex.ru",
        smtp_server="smtp.yandex.ru",
        imap_port=993,
        smtp_port=465,
    )

    check = post.connect
    if check is True:

        post.select_folders()
        post.update_email(fltr="UNSEEN")
        uid = post.get_uid_last_email()
        email = post.get_email(uid)

        from_email = post.get_from_email(email)
        subject_email = post.get_subject_email(email)
        date_email = post.get_date_email(email)
        file_way = post.get_file(email)
        body = post.get_body(email)

        print(f"from_email: {from_email}, {type(from_email)}")
        print(f"subject_email: {subject_email}, {type(subject_email)}")
        print(f"date_email: {date_email}, {type(date_email)}")
        print(f"file_way: {file_way}, {type(file_way)}")
        print(f"body: {len(str(body))}, {type(body)}")

    else:
        print(check)



if __name__ == "__main__":
    main()

from setting import LOGIN_EMAIL, PASSWORD_EMAIL

from email_reader.email_reader import emails_post



def main():
    post = emails_post(email_login=LOGIN_EMAIL, email_password=PASSWORD_EMAIL,
                       imap_server="imap.yandex.ru", smtp_server="smtp.yandex.ru",
                       imap_port=993, smtp_port=465)
    # print(post.get_count_unread_email())
    print(post.get_folders())

if __name__ == "__main__":
    main()
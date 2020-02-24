import smtplib, imaplib
import email.mime.text
import email.mime.multipart
from getpass import getpass
from os import system
import time


# Text
prompt = '''
 What would you like to do:
 1.  Compose
 2.  Read email from Inbox
 3.  Close Application

'''


# Classes
class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self):
        return self.impl()


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        return ch


# Declaring Variables
getch = _Getch()


# Functions
def time_stamp():
    return time.strftime(' Date Sent:  %a %B %d, %Y\n Time Sent:  %I:%M:%S %P\n', time.localtime())


def menu(email_user):
    system('clear')
    print(f' Login as:  {email_user}\n' + prompt)


def send_message(smtp_server, email_user):
    correct = False
    while not correct:
        system('clear')

        email_send = input(' To:  ')
        subject = input(' Subject:  ')

        system('nano email_body.txt')
        buf = input('\n Press any key to continue')

        infile = open('email_body.txt', 'rt')

        body = ''
        for each in infile:
            body += each

        infile.close()

        system('clear')
        print(f' From:     {email_user}')
        print(f' To:       {email_send}')
        print(f' Subject:  {subject}\n')

        for each in body.split('\n'):
            print(f' {each}')
        print('\n\n [Would you like to continue (y/n)]', end = '', flush = True)

        answer = False
        while not answer:
            user_input = getch()

            if user_input.isalpha():
                if user_input.lower() == 'y' or user_input.lower() == 'n':
                    answer = True
                elif user_input == chr(27) or user_input == 'q':
                    return 0

        if user_input.lower() == 'y':
            correct = True
            system('rm email_body.txt')

    message = email.mime.multipart.MIMEMultipart()
    message['From'] = email_user
    message['To'] = email_send
    message['Subject'] = subject
    message.attach(email.mime.text.MIMEText(body, 'plain'))
    text = message.as_string()

    smtp_server.sendmail(email_user, email_send, text)

    system('clear')
    print(f' From:     {email_user}')
    print(f' To:       {email_send}')
    print(f' Subject:  {subject}\n')
    print(time_stamp() + '\n')
    print(f' {body}\n', end = '', flush = True)
    buf = getch()

    return 0


def payload_loop(raw):
    if raw.is_multipart():
        return payload_loop(raw.get_payload(0))
    else:
        bytes_as_string = (raw.get_payload(None, True)).decode('utf-8')
        print('\n' + bytes_as_string + '\n')


def view_inbox(email_user, user_pwd):
    imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_server.login(email_user, user_pwd)
    imap_server.select('INBOX')

    result, data = imap_server.search(None, 'ALL')
    all_emails = data[0]
    email_list = all_emails.split()
    email_list.reverse()

    system('clear')
    print(f' Login as:  {email_user}\n ----------------------------------------  START  ----------------------------------------\n')

    if len(email_list) > 0:
        idx = 0
        isFinished = False
        while idx < len(email_list) and not isFinished:
            result, data = imap_server.fetch(email_list[idx], '(RFC822)')
            raw = email.message_from_bytes(data[0][1])
            subject = raw['subject']
            email_from = raw['From']
            date_received = raw['Date']

            print(f' From:     {email_from}')
            print(f' Subject:  {subject}')
            print(f' Date:     {date_received}')

            user_input = getch()

            if user_input == chr(27) or user_input == 'q':
                isFinished = True
            elif user_input == chr(13):
                payload_loop(raw)
                if idx < len(email_list):
                    print('\n ----------------------------------------  NEXT  ----------------------------------------\n')
                    idx += 1

                user_input = getch()

                if user_input == chr(27) or user_input == 'q':
                    isFinished = True
            else:
                if idx < len(email_list):
                    print('\n ----------------------------------------  NEXT  ----------------------------------------\n')
                    idx += 1

    print(' ----------------------------------------  END  ----------------------------------------')

    imap_server.logout()


def main():
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()

    system('clear')

    # Delcare a flag to check if login was successful
    success = False
    finished = False
    while not success and not finished:
        email_user = input(' Email:  ')
        user_pwd = getpass(' Password:  ')

        try:
            smtp_server.login(email_user, user_pwd)

            success = True
            finished = True
        except:
            print('\n Error: login failed', end = '', flush = True)
            user_input = getch()

            if user_input == chr(27) or user_input == 'q':
                finished  = True
            else:
                system('clear')

    if success:
        finished = False
        while not finished:
            menu(email_user)
            success = True

            user_input = getch()

            if user_input == chr(27) or user_input == 'q' or user_input == '3':
                finished = True
            elif user_input == '1':
                send_message(smtp_server, email_user)
            elif user_input == '2':
                view_inbox(email_user, user_pwd)

    if finished:
        smtp_server.quit()
        system('clear && printf \' Exit successfully\' && sleep 1 && clear')


if __name__ == '__main__': main()

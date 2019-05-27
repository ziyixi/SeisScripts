"""
send mails for each file in mails/
"""
from glob import glob
import subprocess


def main():
    mail_lists = glob("./mails/*")
    command = "python send_mail.py "
    for item in mail_lists:
        command += item + " "

    subprocess.call(command, shell=True)


if __name__ == "__main__":
    main()

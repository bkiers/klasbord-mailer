import requests
import time
from datetime import datetime
import sendgrid
import os
from sendgrid.helpers.mail import *
from dotenv import dotenv_values

config = dotenv_values("secrets.config")


def session():
    data = {'username': config['KLASBORD_LOGIN'], 'password': config['KLASBORD_PASSWORD']}
    r = requests.put('https://app.klasbord.nl/api/v2/users/login', data=data)
    return r.json()['session']['id']


def posts():
    s = session()
    headers = {'Cookie': f"_ga_SOMETHING=NOISE; session={s}"}
    r = requests.get('https://web.klasbord.nl/fallback_request.php?url=https://app.klasbord.nl/api/posts/all/count/10/1', headers=headers)
    return r.json()['posts']


def send_email(message):
    sg_client = sendgrid.SendGridAPIClient(api_key=config['SENDGRID_KEY']).client
    sg_email = Mail(Email(config['EMAIL_FROM']), To(config['EMAIL_TO']), 'New Klasbord message!', message)
    sg_client.mail.send.post(request_body=sg_email.get())


while True:
    print(f"Checking at {datetime.now()}...")
    try:
        for post in posts():
            uid = post['uid']
            text = post['text']
            timestamp = post['time']
            author = post['owner']['firstname']
            date_formatted = datetime.fromtimestamp(timestamp)
            file_name = f"./messages/{uid}.txt"
            delimiter = '------------------------------------------------'

            if not os.path.isfile(file_name):
                print(f'New message: {uid}')
                message = f"{date_formatted}\n\n{author}:\n{delimiter}\n{text}\n{delimiter}\n"
                with open(file_name, 'w') as f:
                    f.write(message)
                send_email(message)
    except Exception as e:
        print(f"OOPS: {e}")

    # Sleep for an hour
    time.sleep(60 * 60)

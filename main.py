import os
import requests
import argparse

import dotenv

dotenv.load_dotenv()

TOKEN = os.getenv('BITLY_TOKEN')


class ApiException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class InputException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def shorten_link(token, url):
    api_url = 'https://api-ssl.bitly.com/v4/bitlinks'

    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json'
    }

    payload = {'long_url': url}

    response = requests.post(api_url, headers=headers, json=payload)

    if response.status_code == 404:
        raise ApiException('404, api point doesnt exist')

    if response.status_code == 403:
        raise ApiException('403, forbidden')

    if 'errors' in response.json():
        raise InputException('wrong link to short')

    return response.json()['link']


def count_clicks(token, url):
    api_url = 'https://api-ssl.bitly.com/v4/bitlinks/{}/clicks/summary'.format(url)

    headers = {
        'Authorization': 'Bearer {}'.format(token)
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 404:
        raise ApiException('404, api point doesnt exist or link was not found')

    if response.status_code == 403:
        raise ApiException('403, forbidden')

    errors = ['NOT_FOUND', 'INTERNAL_ERROR']

    try:
        if any(error in response.json()['message'] for error in errors):
            raise InputException('link was not found')
    except KeyError:
        pass

    return 'Количество кликов по данной ссылке: {}'.format(response.json()['total_clicks'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', type=str, help='URL to short or bitly link to count')
    args = parser.parse_args()

    url = args.url

    if r'://bit.ly' in url:
        url = url.replace('https://', '')
        url = url.replace('http://', '')
        print(count_clicks(TOKEN, url))
        return

    elif url.startswith('bit.ly'):
        print(count_clicks(TOKEN, url))
        return

    else:
        print(shorten_link(TOKEN, url))


if __name__ == '__main__':
    main()

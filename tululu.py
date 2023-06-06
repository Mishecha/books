import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import urllib.parse
from urllib.parse import urlparse
import argparse
import logging
import time
import telegram
import json


def get_book(number):
    book_url = f'https://tululu.org/b{number}/'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)  
    return response


def check_for_redirect(cheak_file):
   if cheak_file:
       raise requests.exceptions.HTTPError


def book_comments(response):
    soup = BeautifulSoup(response.text, 'lxml')
    block_comments = soup.find_all('span', class_='black')
    comments_text = [comment.text for comment in block_comments]
    return comments_text


def book_genre(response):
    soup = BeautifulSoup(response.text, 'lxml')
    block_genre = soup.find_all('span', class_='d_book')
    genre_text = [comment.text for comment in block_genre]
    str_genre_text = (' '.join(genre_text))
    ready_genre_text = str_genre_text.replace('\xa0', '')
    return ready_genre_text


def get_book_name(response):
    soup = BeautifulSoup(response.text, 'lxml')
    name_book_author = soup.find('h1')
    name_book = name_book_author.text.replace('\xa0', '').split('::')
    heading, author = name_book
    return heading, author


def photo_name(response):
    soup = BeautifulSoup(response.text, 'lxml')
    photo_book = soup.find(class_='bookimage').find('img')['src']
    return photo_book


def get_extension(user_link):
    user_quote_link = urllib.parse.unquote(user_link,
                                           encoding='utf-8', errors='replace')
    parsed_link = urlparse(user_quote_link)
    path = parsed_link.path
    splitext = os.path.splitext(path)
    file_name, expansion = splitext
    return expansion


def download_photo(number, response):
    photo_link = urljoin('http://tululu.org/', photo_name(response))
    file_path = os.path.join('dir_images', f'{number} {get_extension(photo_link)}')
    response = requests.get(photo_link)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)
    


def download_txt(number, response):
    file_name = (f"{sanitize_filename(get_book_name(response)[1])}")
    file_path = os.path.join('dir_books', f'{number} {file_name}')
    book_url = f'https://tululu.org/txt.php'
    params = {
        'id': number
    }  
    response = requests.get(book_url, params)
    response.raise_for_status()
    check_for_redirect(response.history)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def parse_book_page(number, response):
    book = {
        'Автор' : get_book_name(response)[0],
        'Название' : get_book_name(response)[1],
        'Жанр' : book_genre(response),
        'Коментарии' : book_comments(response),
        'Скачивание Обложек' : download_photo(number, response),
        'Скачивание книг': download_txt(number, response)
    }
    return book


def main():
    os.makedirs('dir_books', exist_ok=True)
    os.makedirs('dir_images', exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', type=int, help='начало id книг', default=1)
    parser.add_argument('--end_id', type=int, help='конец id книг', default=11)
    args = parser.parse_args()
    for number in range(args.start_id , args.end_id):
        try:
            response = get_book(number)    
            parse_book_page(number, response)
        except requests.exceptions.HTTPError:
            logging.error('Ошибка при запросе к tululu')
        except requests.ConnectionError:
            time.sleep(25)
        except telegram.error.NetworkError:
            time.sleep(25)    

if __name__ == "__main__":
    main()

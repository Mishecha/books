import urllib.parse
import argparse
import logging
import time
import requests
import os

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlparse


def get_response_book(number):
    book_url = f'https://tululu.org/b{number}/'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)  
    return response


def check_for_redirect(check_response):
   if check_response:
       raise requests.exceptions.HTTPError


def get_book_name(soup):
    name_book_author = soup.find('h1')
    name_book = name_book_author.text.replace('\xa0', '').split('::')
    heading, author = name_book
    return heading, author


def get_extension(user_link):
    user_quote_link = urllib.parse.unquote(user_link,
                                           encoding='utf-8', errors='replace')
    parsed_link = urlparse(user_quote_link)
    path = parsed_link.path
    splitext = os.path.splitext(path)
    file_name, expansion = splitext
    return expansion


def download_photo(number, photo_link):
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


def parse_book_page(response, photo_link):
    soup = BeautifulSoup(response.text, 'lxml')

    block_comments = soup.find_all('span', class_='black')
    comments_text = [comment.text for comment in block_comments]

    block_genre = soup.find_all('span', class_='d_book')
    genre_text = [comment.text for comment in block_genre]
    str_genre_text = (' '.join(genre_text))
    ready_genre_text = str_genre_text.replace('\xa0', '')

    photo_book = soup.find(class_='bookimage').find('img')['src']

    heading, autor = get_book_name(soup)
    book = {
        'autor' : autor,
        'book name' : heading,
        'genre' : ready_genre_text,
        'comments' : comments_text,
        'cover' : photo_link,
    }
    return book, photo_book


def main():
    os.makedirs('dir_books', exist_ok=True)
    os.makedirs('dir_images', exist_ok=True)
    parser = argparse.ArgumentParser(description='нужен для создания аргументов')
    parser.add_argument('--start_id', type=int, help='начало id книг', default=1)
    parser.add_argument('--end_id', type=int, help='конец id книг', default=11)
    args = parser.parse_args()
    for number in range(args.start_id , args.end_id):
        try:
            response = get_response_book(number)
            photo_book, book_page = parse_book_page(response, photo_link)
            photo_book = parse_book_page(response, photo_link)
            photo_link = urljoin(f'http://tululu.org/b{number}/', photo_book) 
            book_page(response, photo_link)

            download_photo(number, photo_link),
            download_txt(number, response)
        except requests.exceptions.HTTPError:
            logging.error('Ошибка при запросе к tululu')
        except requests.ConnectionError:
            logging.error('Проблемы со связью. Пожалуйста, повторите попытку снова')
            time.sleep(60)

if __name__ == "__main__":
    main()

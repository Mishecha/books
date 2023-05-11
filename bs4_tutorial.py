import requests
from bs4 import BeautifulSoup
import os
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
import urllib.parse
from urllib.parse import urlparse
import argparse


def check_for_redirect(response):
   if response:
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


def book_name(response):
    soup = BeautifulSoup(response.text, 'lxml')
    name_book_author = soup.find('h1')
    name_book = name_book_author.text.replace('\xa0', '').split('::')
    return name_book[0], name_book[1]


def photo_name(number):
    book_url = f'https://tululu.org/b{number}/'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)

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


def download_photo(number):
    photo_link = urljoin('http://tululu.org/', photo_name(number))
    file_path = os.path.join('dir_images', f'{number} {get_extension(photo_link)}')
    response = requests.get(photo_link)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)
    


def download_txt(number):
    file_name = (f"{sanitize_filename(book_name(number)[1])}")
    file_path = os.path.join('dir_books', f'{number} {file_name}')
    book_url = f'https://tululu.org/txt.php?id={number}'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def parse_book_page(number):
    book_url = f'https://tululu.org/b{number}/'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)
    heading = f'Заголовок: {book_name(response)[0]}'
    author = f'Автор: {book_name(response)[1]}'
    return heading, author


def main():
    os.makedirs('dir_books', exist_ok=True)
    os.makedirs('dir_images', exist_ok=True)
    parser = argparse.ArgumentParser()
    parser.add_argument('start_id', help='начало id книг', type=int, default=1)
    parser.add_argument('end_id', help='конец id книг', type=int, default=11)
    args = parser.parse_args()
    for number in range(args.start_id , args.end_id):
        try:
            print(parse_book_page(number))
        except requests.exceptions.HTTPError:
            pass
    
if __name__ == "__main__":
    main()

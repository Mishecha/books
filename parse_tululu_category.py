import requests
import os
import json
import logging
import time

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tululu import check_for_redirect, download_txt, download_photo, parse_book_page
from urllib.parse import urljoin


def get_response_book_id(number):
    book_url = f'https://tululu.org/l55/{number}'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)
    return response


def download_link(response):
    book_link = []
    soup = BeautifulSoup(response.text, 'lxml')
    block_id = soup.find_all(class_='d_book')
    for id in block_id:
        book_id = id.find('a')['href']
        book_link.append(urljoin('https://tululu.org', book_id))
    return book_link


def get_response_book(link):
    response = requests.get(link)
    response.raise_for_status()
    check_for_redirect(response.history)
    return response


def json_file(book_dict):
    book_json = json.dumps(book_dict, ensure_ascii=False)
    with open("book.json", "a", encoding='utf8') as my_file:
        my_file.write(book_json)


def main():
    os.makedirs('dir_books', exist_ok=True)
    os.makedirs('dir_images', exist_ok=True)
    for number in range(5, 9):
        response = get_response_book_id(number)
        book_link = download_link(response)
        for link in book_link:
            try:
                response_book = get_response_book(link)
                book_content = parse_book_page(response_book)
                parsed_link = link.split('b')
                other, number_link = parsed_link
                parsed_number_id = number_link.split('/')
                number_id, other = parsed_number_id

                heading = book_content['book_name']
                photo_book = book_content['image_link']
                photo_link = urljoin(f'http://tululu.org/b{number_id}/', photo_book)
                json_file(book_content)
                #download_txt(number_id, heading)
                #download_photo(number_id, photo_link)
            except requests.exceptions.HTTPError:
                logging.error('Ошибка при запросе к tululu')
                continue
            except requests.ConnectionError:
                logging.error('Проблемы со связью. Пожалуйста, повторите попытку снова')
                time.sleep(60)
                continue                
if __name__ == "__main__":
    main()
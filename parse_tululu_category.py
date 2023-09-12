import requests
import os
import json
import logging
import time
import argparse

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tululu import check_for_redirect, download_txt, download_photo, parse_book_page
from urllib.parse import urljoin


def get_response_book_id(number):
    book_url = f'https://tululu.org/l55/{number}/'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)
    return response


def download_link(response):
    book_link = []
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.d_book'
    block_id = soup.select(selector)
    for id in block_id:
        selector = 'a'
        book_id = id.select_one(selector)['href']
        book_link.append(urljoin('https://tululu.org', book_id))
    return book_link


def get_response_book(link):
    response = requests.get(link)
    response.raise_for_status()
    check_for_redirect(response.history)
    return response


def json_file(book_dict, dir_name):
    file_path = os.path.join(dir_name, 'book.json')
    with open(file_path, "w+", encoding="utf-8-sig") as f:
        json.dump(book_dict, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Парсит книги с и до определенной страницы книги')
    parser.add_argument('--start_page', type=int, help='начало id книг', default=700)
    parser.add_argument('--end_page', type=int, help='конец id книг', default=701)

    parser.add_argument('--skip_img', help='не скачивать картинки', action="store_true")
    parser.add_argument('--skip_txt', help='не скачивать книги', action="store_true")
    parser.add_argument('--dest_folder', type=str,
                        help='путь с результатами парсинга: картинкам, книгам, JSON', default='json_folder')
    args = parser.parse_args()
    os.makedirs(args.dest_folder, exist_ok=True)
    if not args.skip_txt:
        os.makedirs('dir_books', exist_ok=True)
    if not args.skip_img:
        os.makedirs('dir_images', exist_ok=True)
    book_dict = []
    for number in range(args.start_page, args.end_page):
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
                book_dict.append(book_content)
                if not args.skip_txt:
                    download_txt(number_id, heading)
                if not args.skip_img:
                    download_photo(number_id, photo_link)
            except requests.exceptions.HTTPError as ex:
                logging.error(ex)
                continue
            except requests.ConnectionError as ex:
                logging.error(ex)
                time.sleep(60)
                continue
    json_file(book_dict, args.dest_folder)


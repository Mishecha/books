import requests
import os
import json
import logging
import time
import argparse

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tululu import download_txt, download_photo, parse_book_page, get_response_book
from urllib.parse import urljoin


def get_book_links(response):
    book_links = []
    soup = BeautifulSoup(response.text, 'lxml')
    selector = '.d_book'
    block_number = soup.select(selector)
    for number in block_number:
        selector = 'a'
        book_number = number.select_one(selector)['href']
        book_links.append(urljoin('https://tululu.org', book_number))
    return book_links


def save_json_file(book_dict, dir_name):
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
    book = []
    for number in range(args.start_page, args.end_page):
        book_url = f'https://tululu.org/l55/{number}/'

        try:
            response = get_response_book(book_url)
            book_links = get_book_links(response)
        except requests.exceptions.HTTPError as ex:
            logging.error(ex)
            continue
        except requests.ConnectionError as ex:
            logging.error(ex)
            time.sleep(60)
            continue

        for link in book_links:
            try:
                book_response = get_response_book(link)
                book_content = parse_book_page(book_response)
                parsed_link = link.split('b')
                other, number_link = parsed_link
                parsed_number_id = number_link.split('/')
                number_id, other = parsed_number_id
                heading = book_content['book_name']
                book_photo = book_content['image_link']
                photo_link = urljoin(f'http://tululu.org/b{number_id}/', book_photo)
                book.append(book_content)
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
    save_json_file(book, args.dest_folder)


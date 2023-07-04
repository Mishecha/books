from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


def get_response_book():
    book_url = f'https://tululu.org/b239'
    response = requests.get(book_url)
    response.raise_for_status()
    return response


def download_link(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_number = soup.find(class_='d_book').find('a')['href']
    book_link = urljoin('https://tululu.org', book_number)
    return book_link


def main():
    response = get_response_book()
    print(download_link(response))

if __name__ == "__main__":
    main()
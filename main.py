import requests
import os


def download_image(file_path):
    photo_url = 'https://dvmn.org/media/Requests_Python_Logo.png'
    response = requests.get(photo_url)
    response.raise_for_status()
    with open(file_path, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response:
        raise requests.exceptions.HTTPError
        


def download_text_book(number):
    file_path = os.path.join('dir_books', f'{number} text_books.txt')
    book_url = f'https://tululu.org/txt.php?id={number}'
    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response.history)
    print(response.history)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def main():
    os.makedirs('dir_books', exist_ok=True)
    for number in range(1, 11):
        try:
            download_image('image.jpeg')
            download_text_book(number)
        except requests.exceptions.HTTPError:
            pass
    
if __name__ == "__main__":
    main()

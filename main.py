from configparser import ConfigParser
from mongoengine import connect
from pathlib import Path
from redis import StrictRedis
from redis_lru import RedisLRU

from models import Author, Quote

client = StrictRedis()
ceche = RedisLRU(client)


@ceche
def parser(query: str) -> list | str:
    command, params = query.strip().split(':')
    if command in ['name', 'tag', 'tags', 'exit']:
        return [command, params.strip().split(',')]
    return 'Невідома команда'


@ceche
def search(params: list) -> list:
    quote = None
    match params[0]:
        case 'name':
            author = Author.objects(fullname=params[1][0])[0]  # TODO: add or istartswith__in=params[1][0]
            quote = Quote.objects(author=author.id)
            quote = [author.fullname, [quo.quote for quo in quote]]
        case 'tag' | 'tags':
            quote = Quote.objects(tags__name__in=params[1])
            quote = [(quo.author.fullname, quo.quote) for quo in quote]
    return quote


def main():
    path = Path(__file__).parent.joinpath('config.ini')
    config = ConfigParser()
    config.read(path)
    user = config.get('DB', 'user')
    password = config.get('DB', 'pass')
    db = config.get('DB', 'db_name')
    domain = config.get('DB', 'domain')

    connect('HW8', host=f'mongodb+srv://{user}:{password}@{domain}/{db}?retryWrites=true&w=majority', ssl=True)

    print('Привіт! Я допоможу з пошуком цитат за ім\'ям автора, тегом або кількома тегами. '
          'Для пошуку, введи "name: ім\'я автора", "tag: тег" або "tags: тег1,тег2". Для виходу введи "exit".')
    while True:
        query = input('Пошук: ')
        if query == 'exit':
            exit()
        try:
            params = parser(query)
            quote = search(params)
            if quote:
                print(f'Результати пошуку за "{query}":')
                if params[0] == 'name':
                    quotes = "\n".join(quote[1])
                    text = f'Author: {quote[0]}\nQuotes:\n{quotes}'
                    print(text)
                else:
                    for quo in quote:
                        print(f'Author: {quo[0]}')
                        print(quo[1])
            else:
                print(f'Немає результатів за запитом "{query}".')
        except IndexError:
            print('Невідомі параметри.')
        except ValueError:
            print('Невідома команда.')
        print('Шукати ще?')


if __name__ == '__main__':
    main()

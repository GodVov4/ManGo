from configparser import ConfigParser
from datetime import datetime
from json import load
from mongoengine import connect, Document, EmbeddedDocument, StringField, DateField, ListField, ReferenceField, CASCADE, EmbeddedDocumentField
from pathlib import Path


class Tag(EmbeddedDocument):
    name = StringField(max_length=50)


class Author(Document):
    fullname = StringField(max_length=120)
    born_date = DateField()
    born_location = StringField(max_length=200)
    description = StringField()
    meta = {'collection': 'authors'}


class Quote(Document):
    tags = ListField(EmbeddedDocumentField(Tag))
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    quote = StringField()
    meta = {'collection': 'quotes'}


def main():
    path = Path(__file__).parent.joinpath('config.ini')
    config = ConfigParser()
    config.read(path)
    user = config.get('DB', 'user')
    password = config.get('DB', 'pass')
    db = config.get('DB', 'db_name')
    domain = config.get('DB', 'domain')

    connect('HW8', host=f'mongodb+srv://{user}:{password}@{domain}/{db}?retryWrites=true&w=majority', ssl=True)

    with open('authors.json', 'r') as json_file:
        authors: list[dict] = load(json_file)
    for author in authors:
        auth = Author(**author)
        auth.born_date = datetime.strptime(auth.born_date, '%B %d, %Y').date()
        auth.save()

    with open('quotes.json', 'r') as json_file:
        quotes: list[dict] = load(json_file)
    for quote in quotes:
        tags = quote.pop('tags')
        quo = Quote(**quote)
        quo.tags = [Tag(name=tag) for tag in tags]
        quo.author = Author.objects(fullname=quote.get('author'))[0]
        quo.save()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(e)

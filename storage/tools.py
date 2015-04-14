# encoding: utf-8
# Created by David Rideout <drideout@safaribooksonline.com> on 2/7/14 4:58 PM
# Copyright (c) 2013 Safari Books Online, LLC. All rights reserved.

from storage.models import Book


def process_book_element(book_element):
    """
    Process a book element into the database.

    :param book: book element
    :returns:
    """
    try:
        validate_book_element(book_element)
    except ImportError as err:
        print("Error when importing book id {} Title '{}'".format(
                book_element.get('id'),
                book_element.findtext('title'),
            )
        )
        print("Error details {}".format(err.message))
        # No further processing of this book
        return

    book, created = Book.objects.get_or_create(pk=book_element.get('id'))
    book.title = book_element.findtext('title')
    book.description = book_element.findtext('description')

    for alias in book_element.xpath('aliases/alias'):
        scheme = alias.get('scheme')
        value = alias.get('value')

        book.aliases.get_or_create(scheme=scheme, value=value)

    book.save()

def iter_aliases(book_element):
    """
    Return an iterator over the aliases in a book_element. Each iteration yields
    a (scheme, value) tuple.
    """
    return (
        (alias.get('scheme'), alias.get('value'))
        for alias
        in book_element.xpath('aliases/alias')
    )

def validate_book_element(book_element):
    """
    Check the data in the element against the existing data in the database.
    Raise an error if any conflicts are found.

    when processing an insert record, check for collisions
        Id against existing ids
        Id against existing aliases
        Each alias against existing ids
        Each alias against existing aliases

    :param book: book element
    :returns:
    """
    return

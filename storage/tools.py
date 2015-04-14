# encoding: utf-8
# Created by David Rideout <drideout@safaribooksonline.com> on 2/7/14 4:58 PM
# Copyright (c) 2013 Safari Books Online, LLC. All rights reserved.

from storage.models import Book, Alias


def process_book_element(book_element):
    """
    Process a book element into the database.

    :param book: book element
    :returns:
    """
    validate_book_element(book_element)
    book, created = Book.objects.get_or_create(pk=book_element.get('id'))
    book.title = book_element.findtext('title')
    book.description = book_element.findtext('description')

    for scheme, value in iter_aliases(book_element):
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
    list_of_conflict_messages = []
    # list_of_conflict_messages.extend(check_id_id_conflict(book_element))
    list_of_conflict_messages.extend(check_id_alias_conflict(book_element))
    # list_of_conflict_messages.extend(check_alias_id_conflict(book_element))

    if list_of_conflict_messages:
        err_msg = "Conflicts\n"
        err_msg += "\n".join(list_of_conflict_messages)
        raise ImportError(err_msg)

# def check_id_id_conflict(book_element):
#     """
#     Return a list of error messages if book_element has an id that conflicts
#     with an existing book id in the database.
#
#     Of course, this could be just a regular update of an existing book, so this
#     function only returns an error message if the amount of changes exceeds some
#     threshhold value.
#     """
#     # TODO implement
#     return []

def check_id_alias_conflict(book_element):
    """
    Return a list of error messages if book_element has an id that conflicts
    with an existing book alias in the database.
    """

    candidate_id = book_element.get('id')

    # Find all the aliase of all the books that are not this book.
    possible_aliases = Alias.objects.exclude(book__pk=candidate_id)

    import_errors = []
    for alias in possible_aliases:
        if alias.value == candidate_id:
            # Found a conflict
            err_msg = ("Imported data {} conflicts with existing alias (scheme "
                       "{} value {}) for book id {}".format(candidate_id,
                                                            alias.scheme,
                                                            alias.value,
                                                            alias.book.id,
                                                           )
                      )
            import_errors.append(err_msg)
    return import_errors

# TODO implement these checks
# def check_alias_id_conflict(book_element):
#     """
#     Return a list of error messages if book_element has an alias that conflicts
#     with an existing book id in the database.
#     """
#     return []

# def check_alias_alias_conflict(book_element):
#     """
#     Return a list of error messages if book_element has an alias that conflicts
#     with an existing book in the database.
#     """
#     return []


class ImportError(Exception):
    """
    Custom error to throw when a publisher record can not be imported.
    """

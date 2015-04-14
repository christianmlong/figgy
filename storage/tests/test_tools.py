# encoding: utf-8
# Created by David Rideout <drideout@safaribooksonline.com> on 2/7/14 5:01 PM
# Copyright (c) 2013 Safari Books Online, LLC. All rights reserved.

from django.test import TestCase
from lxml import etree
from storage.models import Book, Alias
import storage.tools


class TestTools(TestCase):

    xml_str = '''
    <book id="12345">
        <title>A title</title>
        <aliases>
            <alias scheme="ISBN-10" value="0158757819"/>
            <alias scheme="ISBN-13" value="0000000000123"/>
        </aliases>
    </book>
    '''

    def setUp(self):
        pass

    def test_storage_tools_process_book_element_db(self):
        '''process_book_element should put the book in the database.'''

        xml = etree.fromstring(self.xml_str)
        storage.tools.process_book_element(xml)

        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.get(pk='12345')

        self.assertEqual(book.title, 'A title')
        self.assertEqual(book.aliases.count(), 2)
        self.assertEqual(Alias.objects.get(scheme='ISBN-10').value, '0158757819')
        self.assertEqual(Alias.objects.get(scheme='ISBN-13').value, '0000000000123')

    def test_storage_tools_process_book_element_idempotent(self):
        '''process_book_element should be idempotent.'''

        xml = etree.fromstring(self.xml_str)
        storage.tools.process_book_element(xml)
        # Do it again
        storage.tools.process_book_element(xml)

        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.get(pk='12345')

    def test_iter_aliases(self):
        '''iter_aliases should provide an iterator over the aliases'''

        xml = etree.fromstring(self.xml_str)
        aliases = storage.tools.iter_aliases(xml)
        scheme, value = aliases.next()
        self.assertEqual(scheme, 'ISBN-10')
        self.assertEqual(value, '0158757819')
        scheme, value = aliases.next()
        self.assertEqual(scheme, 'ISBN-13')
        self.assertEqual(value, '0000000000123')
        with self.assertRaises(StopIteration):
            aliases.next()

    def test_storage_tools_check_id_alias_conflict(self):
        '''check_id_alias_conflict should catch conflicts'''

        xml = etree.fromstring(self.xml_str)
        storage.tools.process_book_element(xml)

        xml_str_with_conflict = '''
        <book id="0158757819">
            <title>Another title</title>
            <aliases>
                <alias scheme="ISBN-13" value="0000000000456"/>
            </aliases>
        </book>
        '''
        xml_with_conflict = etree.fromstring(xml_str_with_conflict)
        with self.assertRaises(storage.tools.ImportError):
            storage.tools.process_book_element(xml_with_conflict)





#

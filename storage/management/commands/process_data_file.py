# encoding: utf-8
# Created by David Rideout <drideout@safaribooksonline.com> on 2/7/14 4:56 PM
# Copyright (c) 2013 Safari Books Online, LLC. All rights reserved.

from django.core.management.base import BaseCommand, CommandError

from lxml import etree
import storage.tools


class Command(BaseCommand):
    args = '<filename filename2 filename3 ...>'
    help = 'Process an xml file '

    def handle(self, *args, **options):
        for filename in args:
            with open(filename, 'rb') as fh:
                print "Importing %s into database." % filename
                book_node = etree.parse(fh).getroot()
                try:
                    storage.tools.process_book_element(book_node)
                except storage.tools.ImportError as err:
                    print("Error when importing {} into "
                          "database.".format(filename))
                    print("Error details {}".format(err.message))
                    print("\n\n")

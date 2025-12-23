"""
TODO: Fill this in
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db import transaction
from journal import models
from django.contrib.auth import get_user_model

from datetime import datetime, time
import re
import sys

DATE_PREFIXES = ('Jan ', 'Feb ', 'Mar ', 'Apr ', 'May ', 'Jun ', 'Jul ', 'Aug ', 'Sep ', 'Oct ', 'Nov ', 'Dec ')
IRREGULARITIES = {'June ': 'Jun ', 'July ': 'Jul ', 'October ': 'Oct ', 'November ': 'Nov ', 'December ': 'Dec '}

CURRENT_YEAR = None

def MANUAL_CHECK(reason, content):
    print(f"Please check: #{reason} {repr(content)[:1000]}")

def try_parse_date(patterns, ds):
    result = None
    for pattern in patterns:
        try:
            return datetime.strptime(ds, pattern)
        except:
            pass

def parse_fb_entries(text):
    lines = text.splitlines()
    def generator(lines):
        entries = []
        current_date = None
        current_content = []
        last_line = None

        for line in lines:
            line = line.strip()

            # Deal with irregularities in the data
            for dpk, dpv in IRREGULARITIES.items():
                if line.startswith(dpk):
                    line = line.replace(dpk, dpv, 1)

            if line in ("Si Fong", "賞鯉專家"):
                if current_date:
                    yield(current_date, current_content)
                    current_date = None
                    current_content = []
                else:
                    MANUAL_CHECK("No date", [last_line, line, current_content])

            # Detect date lines (e.g., "Jan 1", "Jan 9")
            if line.startswith(DATE_PREFIXES) or try_parse_date(('%b %d', '%d %b'), line):
                if last_line not in ("Si Fong", "賞鯉專家"):
                    MANUAL_CHECK("Misparse separator", [last_line, line, current_content])

                current_date = line

            current_content.append(line)

            last_line = line

        # Handle last entry
        yield(current_date, current_content)

    result = []
    for ds, content in generator(lines):
        dt = try_parse_date(('%b %d', '%d %b'), ds).replace(hour=19, minute=0, second=0, year=CURRENT_YEAR)
        joined = '\n'.join(content[2:]).strip()
        if len(joined) > 9999:
            MANUAL_CHECK("content too long", [len(joined), joined])
        if len(joined) == 0:
            MANUAL_CHECK("no content", [len(joined), joined])
        else:
            result.append((dt, f"FB {content[0]} {content[1]}", joined))

    return result


def parse_threads_entries(text):
    lines = text.splitlines()
    def generator(lines):
        entries = []
        current_date = None
        current_content = []
        last_line = None

        for line in lines:
            line = line.strip()

            # Deal with irregularities in the data
            for dpk, dpv in IRREGULARITIES.items():
                if line.startswith(dpk):
                    line = line.replace(dpk, dpv, 1)

            if line in ("si.fong", "si.fong"):
                if current_date:
                    yield(current_date, current_content)
                    current_date = None
                    current_content = []
                else:
                    MANUAL_CHECK("No date", current_content)

            # Detect date lines
            if re.match(r'[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9]', line) or re.match(r'[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9]', line):
                if last_line not in ("si.fong", ):
                    MANUAL_CHECK("Misparse separator", [last_line, line, current_content])

                current_date = line

            current_content.append(line)

            last_line = line

        # Handle last entry
        yield(current_date, current_content)

    result = []
    for ds, content in generator(lines):
        dt = try_parse_date(["%m/%d/%Y", "%m/%d/%y"], ds).replace(hour=19, minute=0, second=0)
        joined = '\n'.join(content[2:])
        result.append((dt, f"THR {content[0]} {content[1]}", joined))
        if len(joined) > 9999:
            MANUAL_CHECK("content too long", [len(joined), joined])

    return result

def parse_blog_entries(text):
    lines = text.splitlines()
    entries = []
    current_date = None
    current_title = None
    current_content = []

    # Date format: "Thursday, June 20, 2024"
    date_format = "%A, %B %d, %Y"

    for line in lines:
        stripped = line.rstrip()

        # Try parsing as date
        if stripped:
            try:
                current_date = datetime.strptime(stripped, "%A, %B %d, %Y")
                # Save previous entry if exists
                if current_date is not None:
                    entries.append((
                        current_date,
                        "CT " + current_title.strip() if current_title else '',
                        '\n'.join(current_content).strip()
                    ))

                # Start new entry
                current_title = None
                current_content = []
                continue

            except ValueError:
                # Not a date — keep accumulating content
                pass

        # If we're in an entry and haven't set title yet, this line is the title
        if current_date is not None and current_title is None and stripped:
            current_title = stripped
        elif current_date is not None:
            # Accumulate content lines
            current_content.append(stripped)

    # Don't forget the last entry
    if current_date is not None:
        entries.append((
            current_date,
            "CT " + current_title.strip() if current_title else '',
            '\n'.join(current_content).strip()
        ))

    return entries

class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--basedir', type=str, required=True, help='Base directory path')
        parser.add_argument('--user', type=str, required=True, help='Author username')
        parser.add_argument('--year', type=int, required=True, help='Year to process')
        parser.add_argument('--no_save', default=False, action='store_true', help='Whether to actually save')

    @transaction.atomic
    def handle(self, *args, **options):
        import uuid
        import os
        os.chdir(options["basedir"])
        global CURRENT_YEAR
        CURRENT_YEAR = int(options["year"])
        username = options["user"]
        User = get_user_model()

        should_save = not options["no_save"]

        print("should save:", should_save)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(f"User '{username}' not found.")

        for entry in parse_fb_entries(open(f"{CURRENT_YEAR}-fb.txt").read()) + parse_blog_entries(open(f"{CURRENT_YEAR}-blog.txt").read()) + parse_threads_entries(open(f"{CURRENT_YEAR}-threads.txt").read()):
            print(repr(entry[0]), entry[1], len(entry[2]), repr(entry[2][:50]))

            e = models.Entry()
            e.title = entry[1]
            e.slug = uuid.uuid4().hex
            e.author = user
            e.entry_type = 'blog'
            e.is_hidden = False
            e.is_public = False
            e.content = entry[2]
            e.created_at = entry[0]
            e.updated_at = entry[0]
            e.plain_text = True

            if should_save:
                e.save()




        print("should save:", should_save)

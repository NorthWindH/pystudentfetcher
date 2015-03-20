import sys
import os
import os.path as path
import collections
import re
import datetime
import argparse

# Note, is_dst=None is used below so ambiguous dst situations result in error
class MatchError(argparse.ArgumentTypeError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

date_pattern_src = r'([0-9]{4})-([0-9]{2})-([0-9]{2})'
datetime_pattern_src = r'(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})'
date_pattern = re.compile(".*%s" % date_pattern_src)
datetime_pattern = re.compile(".*%s" % datetime_pattern_src)
date_pattern_strict = re.compile("^%s$" % date_pattern_src)
datetime_pattern_strict = re.compile("^%s$" % datetime_pattern_src)

def date_from_match(m):
    return datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

def datetime_from_match(m):
    return datetime.datetime(
                int(m.group(1)), int(m.group(2)), int(m.group(3)),
                int(m.group(4)), int(m.group(5)), int(m.group(6)))

def validate_date(arg):
    m = date_pattern_strict.match(arg)
    if m:
        try:
            return date_from_match(m)
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid date value %s" % arg)

    raise MatchError("Invalid date %s" % arg)

def validate_datetime(arg):
    m = datetime_pattern_strict.match(arg)
    if m:
        try:
            return datetime_from_match(m)
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid datetime value %s" % arg)

    raise MatchError("Invalid datetime %s" % arg)

def validate_due(arg):
    try:
        return validate_date(arg)
    except MatchError:
        pass

    try:
        return validate_datetime(arg)
    except MatchError:
        pass

    raise MatchError("Invalid due date %s" % arg)

def meets_deadline(d, deadline):
    """
    Returns true if date or datetime d is less than or equal to date or datetime
    deadline.

    If both are datetimes, the full datetime is compared.
    If either is a date, only the date components are tested.
    """

    if isinstance(d, datetime.datetime) and isinstance(deadline, datetime.datetime):
        return d <= deadline

    if isinstance(d, datetime.datetime):
        d = d.date()

    if isinstance(deadline, datetime.datetime):
        deadline = deadline.date()

    return d <= deadline

def weekday_idx_to_letter(idx):
    return 'mtwrfsn'[idx]

class StudentFinder:
    def __init__(self,
        source=list(),
        submission_type=None,
        name=list(),
        name_file=list(),
        name_directory=list(),
        pattern=list(),
        pattern_file=list(),
        pattern_directory=list(),
        recursive=False,
        due=None,
        holiday=list(),
        business_days="mtwrf",
        *args,
        **kwargs
    ):
        self.source = source
        self.submission_type = submission_type
        self.name_file = list()
        self.name_file += name_file
        self.name_directory = list()
        self.name_directory += name_directory
        self.name_file += name
        self.name_directory += name
        self.pattern_file = list(pattern_file)
        self.pattern_directory = list(pattern_directory)
        self.pattern_file += pattern
        self.pattern_directory += pattern
        self.recursive = recursive
        self.due = due
        self.holiday = holiday
        self.business_days = business_days

    def match(self, student_key):
        match_submissions = list()
        match_results = list()
        submission_date = None
        late_days = None

        # Go over all sources and collect submissions
        for src_dir in self.source:
            basenames = os.listdir(src_dir)
            for basename in basenames:
                if basename.count(student_key):
                    do_append = True
                    sub_path = path.join(src_dir, basename)
                    if not self.submission_type or \
                        (self.submission_type == 'files' and path.isfile(sub_path)) or \
                        (self.submission_type == 'directories' and path.isdir(sub_path)):
                        match_submissions.append(sub_path)

        # Iterate over submissions and behave accordingly
        for submission in match_submissions:

            # Match directory contents by name and pattern
            if path.isdir(submission):

                # If no name specs and no patterns, just fetch directory itself
                if not self.name_file and not self.name_directory and \
                    not self.pattern_file and not self.pattern_directory:
                    match_results.append(submission)

                # Otherwise, look through contents
                else:
                    contents = [path.join(submission, f) for f in os.listdir(submission)]
                    while conents:
                        item = contents.pop(0)

                        name_list = self.name_file
                        pattern_list = self.pattern_file
                        isdir = path.isdir(item)
                        if isdir:
                            name_list = self.name_directory
                            pattern_list = self.pattern_directory

                        basename = path.basename(item)
                        if basename in name_list or \
                            any([p.match(basename) for p in pattern_list]):
                            match_results.append(item)
                        elif isdir and self.recursive:
                            contents.append([path.join(item, f) for f in os.listdir(item)])

            # Match file by pattern
            elif self.pattern_file:
                basename = path.basename(submission)
                if any([p.match(basename) for p in self.pattern_file]):
                    match_results.append(submission)

            # No patterns, just add file to results
            else:
                match_results.append(submission)

        # Find submission date
        submission_date = None
        for submission in match_submissions:
            basename = path.basename(submission)

            test_date = None

            m = datetime_pattern.match(basename)
            if m:
                try:
                    test_date = datetime_from_match(m)
                except ValueError:
                    print("File %s contains invalid datetime values, ignored for late days calculation..." %
                        submission)
            else:
                m = date_pattern.match(basename)
                if m:
                    try:
                        test_date = date_from_match(m)
                    except ValueError:
                        print("File %s contains invalid date values, ignored for late days calculation..." %
                            submission)

            if test_date:
                do_replace = False
                if not submission_date:
                    do_replace = True
                else:
                    d1 = submission_date
                    d2 = test_date

                    # Ensure both types can be compared
                    if type(d1) != type(d2):
                        if isinstance(d1, datetime.datetime):
                            d1 = d1.date()
                        if isinstance(d2, datetime.datetime):
                            d2 = d2.date()
                        if d2 > d1:
                            do_replace = True

                if do_replace:
                    submission_date = test_date

        # If due date, calculate late days
        if self.due:

            # If sub late, walk through calendar to calculate late days...
            late_days = None
            if submission_date:
                late_days = list()
                if not meets_deadline(submission_date, self.due):
                    next_day = self.due
                    if isinstance(next_day, datetime.datetime):
                        next_day = next_day.date()
                    day_advance = datetime.timedelta(days=1)
                    while True:
                        # Find next business day date
                        late_days.append(next_day)
                        while True:
                            next_day = next_day + day_advance
                            if weekday_idx_to_letter(next_day.weekday()) in self.business_days and \
                                not next_day in self.holiday:
                                break
                        if meets_deadline(submission_date, next_day):
                            break

        return {
            'match_submissions': match_submissions,
            'match_results': match_results,
            'submission_date': submission_date,
            'late_days': late_days,
        }

#!/bin/env python3

import sys
import shutil
import os.path as path
import argparse
import re
import datetime
import textwrap
from pystudentfetcher.studentfinder import StudentFinder, MatchError, validate_date, validate_due

if __name__ == "__main__":
    def validate_business_days(arg):
        arg = arg.lower()
        if re.match(r'.*[^mtwrfsn]', arg):
            raise argparse.ArgumentTypeError("business day spec includes invalid character, with spec %s" % arg)
        return set(arg)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Fetches student files to destination directory.",
        epilog=textwrap.dedent("""\
            Student key is used to find student submissions where a submission's filename
            must contain the student key. Action taken is based on type of submission.

            Directory matches:
                If filenames specified then directory contents are searched for exactly
                matching files/directories and those are fetched;
                If patterns specified then directory contents are searched for matching
                files/directories and those are fetched;
                If no filenames or patterns, all directory matches are fetched verbatim.
            File matches:
                If patterns specified then files matching a provided pattern are fetched;
                If no patterns, all matching files fetched.

            Submission datetime is found by matching for YYYY-MM-DD-HH-MM-SS or YYYY-MM-DD
            in submission file/directory name. Latest date/datetime amongst all matched
            submissions is considered submission time.""")
    )
    basic = parser.add_argument_group("Basic Parameters")
    basic.add_argument("student_key", type=str, help="The key to use to find a student.")
    basic.add_argument("-s", "--source",
        action="append", default=list(), help="Add a directory (source) to look for student submissions in.")
    basic.add_argument("-d", "--destination", default=".", type=str, help="Set the fetch destination directory. Defaults to the working directory.")

    submission_type = parser.add_argument_group("Submission Type")
    submission_type.add_argument("-F", "--files-only",
        action="store_const", const="files", dest="submission_type", help="Look for file student submissions only.")
    submission_type.add_argument("-D", "--directories-only",
        action="store_const", const="directories", dest="submission_type", help="Look for directory student submissions only.")

    matching = parser.add_argument_group("Matching")
    matching.add_argument("-n", "--name",
        action="append", default=list(), help="Add a fetch name for files or directories.")
    matching.add_argument("-nf", "--name-file",
        action="append", default=list(), help="Add a fetch name for files.")
    matching.add_argument("-nd", "--name-directory",
        action="append", default=list(), help="Add a fetch name for directories.")
    matching.add_argument("-p", "--pattern", type=re.compile,
        action="append", default=list(), help="Add a fetch regex pattern that matches files or directories.")
    matching.add_argument("-pf", "--pattern-file", type=re.compile,
        action="append", default=list(), help="Add a fetch regex pattern that matches files.")
    matching.add_argument("-pd", "--pattern-directory", type=re.compile,
        action="append", default=list(), help="Add a fetch regex pattern that matches directories.")
    matching.add_argument("-r", "--recursive", action="store_true", default=False, help="Directory submissions are searched recursively for files and patterns.")

    late_days = parser.add_argument_group("Late Days")
    late_days.add_argument("-u", "--due", type=validate_due, help="Specify due date. Submission date is the latest date among all matched student submissions. Format YYYY-MM-DD or YYYY-MM-DD-HH-MI-SS.")
    late_days.add_argument("-y", "--holiday",
        type=validate_date, default=list(), action="append", help="Add a date that does not count against late days (ie non-business date eg stat holidays). Format YYYY-MM-DD.")
    late_days.add_argument("-b", "--business-days",
        type=validate_business_days,
        help="Specify business days. Allowed characters are m,t,w,r,f,s,n representing monday, tuesday, ... Defaults to mtwrf",
        default=set('mtwrf'))
    args = parser.parse_args()

    if not path.isdir(args.destination):
        print("Output path is not a valid directory, received %s (abs resolves to %s)" %(
            args.destination, path.abspath(args.destination)
        ))
        sys.exit(1)

    finder = StudentFinder(**vars(args))
    match = finder.match(args.student_key)
    print(match)
    exit()

    student_found = chooser.find_student(student_key)
    if not student_found:
        print("Could not find student with key %s" % student_key)
        sys.exit(1)

    # Verify existence of all fetch files
    for fetch_file in args.file:
        fetch_path = path.join(student_found.path, fetch_file)
        if not path.isfile(fetch_path):
            print("Could not find file %s in directory for student: %s, src %s, days late %d" % (
                fetch_file,
                path.basename(student_found.path),
                student_found.src,
                student_found.days_late))
            sys.exit(1)

    # Copy over all fetch files
    for fetch_file in args.file:
        fetch_path = path.join(student_found.path, fetch_file)
        shutil.copy(fetch_path, args.destination)

    print("Fetch success. Fetched %s, src %s, days late %d" % (
        path.basename(student_found.path),
        student_found.src,
        student_found.days_late))

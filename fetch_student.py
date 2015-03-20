#!/bin/env python3

import sys
import shutil
import os.path as path
import os
import argparse
import re
import datetime
import textwrap
from pystudentfetcher.studentfinder import StudentFinder, MatchError, validate_date, validate_due

def format_datetime(prefix, d):
    rv = "%s date: %s" % (prefix, format(d, "%A, %B %d, %Y"))
    if isinstance(d, datetime.datetime):
        rv = rv + "\n%s time: %s" % (prefix, format(d, "%I:%M:%S %p"))
    return rv

def main():
    def validate_business_days(arg):
        arg = arg.lower()
        if re.match(r'.*[^mtwrfsn]', arg):
            raise argparse.ArgumentTypeError("business day spec includes invalid character, with spec %s" % arg)
        return set(arg)

    parser = argparse.ArgumentParser(
        prog='pystudentfetcher',
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
        return 1

    finder = StudentFinder(**vars(args))
    match = finder.match(args.student_key)

    if not match['match_submissions']:
        print("Found no entry submissions...")
        return 1

    print("Found %d entry submissions:" % len(match['match_submissions']))
    for s in match['match_submissions']:
        print("    %s" % s)
    print('')

    print("Found %d filesystem targets:" % len(match['match_results']))
    for s in match['match_results']:
        print("    %s" % s)
    print('')

    if args.due:
        print("%s\n" % format_datetime("Due", args.due))

    if 'submission_date' in match:
        d = match['submission_date']
        print("%s\n" % format_datetime("Submission", match['submission_date']))
    else:
        print("No submission date could be extracted...\n")

    if args.due:
        l = match['late_days']
        if l != None:
            print("Late days (%d):" % len(l))
            for i, day in enumerate(l):
                print("%s" % format_datetime("Day %d" % i, day))
            print('')
        else:
            print("Due date present but could not extrace submission date...\n")

    for f in match['match_results']:
        dest_path = path.join(args.destination, path.basename(f))
        if path.isdir(f):
            if path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.copytree(f, dest_path)
        else:
            shutil.copyfile(f, dest_path)

    print("Fetch success.")
    return 0

if __name__ == "__main__":
    exit(main())

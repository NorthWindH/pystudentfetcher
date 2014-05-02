import sys
import shutil
import os.path as path
import argparse
from pystudentfetcher.studentfinder import StudentFinder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetches student files to local directory")
    parser.add_argument("student_key", type=str, help="The key to use to find a student.")
    parser.add_argument("-s", "--source", action="append", help="Add a directory (source) to look for student directories in.")
    parser.add_argument("-f", "--file", action="append", help="Add a file to fetch from the student directory upon success.")
    parser.add_argument("-d", "--destination", default=".", type=str, help="Set the fetch destination directory")
    args = parser.parse_args()

    student_key = args.student_key

    if not path.isdir(args.destination):
        print("Output path is not a valid directory, received %s (abs resolves to %s)" %(
            args.destination, path.abspath(args.destination)
        ))
        sys.exit(1)

    chooser = StudentFinder(args.source)
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

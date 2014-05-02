import sys
import os
import os.path as path
import collections

class FoundStudent:
    def __init__(self, path_, src, days_late):
        self.path = path_
        self.src = src
        self.days_late = days_late

class StudentFinder:
    def __init__(self, student_dirs):
        if not isinstance(student_dirs, collections.Iterable):
            raise Exception("Student dirs not iterable")
        self.student_dirs = student_dirs

    def _find_student_dir_helper(self, dir_path, student_key):
        # Attempt to find the student's key in this directory
        student_key = student_key.lower()
        for dir_entry in os.listdir(dir_path):
            abspath = path.abspath(os.path.join(dir_path, dir_entry))
            if os.path.isdir(abspath) and dir_entry.lower().count(student_key):
                return abspath
        return ""

    def find_student(self, student_key):
        for student_dir in self.student_dirs:
            bn = path.basename(student_dir)

            # Try to find student in larger dir first
            student_found = self._find_student_dir_helper(student_dir, student_key)

            # If student found, return path with 0 late days
            if student_found:
                return FoundStudent(student_found, bn, 0)

            # Try to find student in late dirs
            for dir_entry in os.listdir(student_dir):
                dir_entry_path = path.join(student_dir,dir_entry)
                if not path.isdir(dir_entry_path) or not dir_entry.count('late'):
                    continue

                student_found = self._find_student_dir_helper(
                    dir_entry_path, student_key)

                if not student_found:
                    continue

                # Return found student with late days
                try:
                    days_late = int(dir_entry[4:])
                except:
                    print("Error while parsing days late: ", sys.exc_info()[0])
                    raise
                return FoundStudent(student_found, bn, days_late)

        return None

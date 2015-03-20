pystudentfetcher
================

Python 3 module for fetching downloaded student work from a set of source
directories. Handles blackboard download format well. Includes support for
files, directories, recursion, filename matching, regex pattern matching,
and late day calculation including business day and holiday support (if provided).

Typical use case
================

Directory structure:
```
/
	Assignment1
		bob
			calc.cpp
			calc.h
			honesty.txt
	tracy
			sup.cpp
			calc.cpp
			calc.h
	workspace
```

After installing pystudentfetcher on the python search path, we can fetch a student's work like this:
```
cd /workspace
python3 -m pystudentfetcher -s /Assignment1 -n calc.cpp -n calc.h b
```

This will fetch the files calc.cpp and calc.h from /Assignment1/bob to the current directory. In this case, the given options are:
```
-s	Adds a directory source to look for student directories
-n	Adds a file to fetch
```

The positional argument is the key to look for students with. In this case, the key was b and since only bob contains b, that directory is what is matched.

We can also fetch like this:
```
cd /
python3 -m pystudentfetcher -s /Assignment1 -n calc.cpp -n calc.h -d /workspace b
```

In this case, we've added one option and the result is that while the current directory is /, fetched files are placed in /workspace.
```
-d	Sets the directory that fetched files should be placed in.
```

We could additionally fetch by pattern by using -p.

For example:
```
cd /
python3 -m pystudentfetcher -s /Assignment1 -p .*\\.cpp\$ -p .*\\.h\$ -n honesty.txt -d /workspace b
```

In this case, the cpp, h, and txt file will all be fetched. As you can see,
-p and -n options can be safely mixed.

A fair number more options are supported. Full usage is at the bottom.

Late Days
=========

The system can also deal with late days. It looks for date and datetime strings
in submission files.

For example, given the following directory structure:
```
/
	Assignment1
		bob_2015-02-09
			calc.cpp
			calc.h
			honesty.txt
		tracy
			sup.cpp
			calc.cpp
			calc.h
	workspace
```

Now if we do an updated command:
```
cd /workspace
python3 -m pystudentfetcher -s /Assignment1 -n calc.cpp -n calc.h b -u 2015-02-01
```

The system will report that bob was 7 days late then show the exact days he was
late for since the 1st is a sunday and bob submitted on the 9th, a monday.

By default, business days are monday, tuesday, wednesday, thursday, friday but
this can be changed with -b.

Holidays can also be specified by using -y repeatedly and those are not counted
as business days.

Fetch Failure
=============

If the fetch fails for any reason, the query failure is reported and the reason why is indicated (eg no matching directory found, no files found, etc...).

Full Usage
==========
```
usage: pystudentfetcher [-h] [-s SOURCE] [-d DESTINATION] [-F] [-D] [-n NAME]
                        [-nf NAME_FILE] [-nd NAME_DIRECTORY] [-p PATTERN]
                        [-pf PATTERN_FILE] [-pd PATTERN_DIRECTORY] [-r]
                        [-u DUE] [-y HOLIDAY] [-b BUSINESS_DAYS]
                        student_key

Fetches student files to destination directory.

optional arguments:
  -h, --help            show this help message and exit

Basic Parameters:
  student_key           The key to use to find a student.
  -s SOURCE, --source SOURCE
                        Add a directory (source) to look for student
                        submissions in.
  -d DESTINATION, --destination DESTINATION
                        Set the fetch destination directory. Defaults to the
                        working directory.

Submission Type:
  -F, --files-only      Look for file student submissions only.
  -D, --directories-only
                        Look for directory student submissions only.

Matching:
  -n NAME, --name NAME  Add a fetch name for files or directories.
  -nf NAME_FILE, --name-file NAME_FILE
                        Add a fetch name for files.
  -nd NAME_DIRECTORY, --name-directory NAME_DIRECTORY
                        Add a fetch name for directories.
  -p PATTERN, --pattern PATTERN
                        Add a fetch regex pattern that matches files or
                        directories.
  -pf PATTERN_FILE, --pattern-file PATTERN_FILE
                        Add a fetch regex pattern that matches files.
  -pd PATTERN_DIRECTORY, --pattern-directory PATTERN_DIRECTORY
                        Add a fetch regex pattern that matches directories.
  -r, --recursive       Directory submissions are searched recursively for
                        files and patterns.

Late Days:
  -u DUE, --due DUE     Specify due date. Submission date is the latest date
                        among all matched student submissions. Format YYYY-MM-
                        DD or YYYY-MM-DD-HH-MI-SS.
  -y HOLIDAY, --holiday HOLIDAY
                        Add a date that does not count against late days (ie
                        non-business date eg stat holidays). Format YYYY-MM-
                        DD.
  -b BUSINESS_DAYS, --business-days BUSINESS_DAYS
                        Specify business days. Allowed characters are
                        m,t,w,r,f,s,n representing monday, tuesday, ...
                        Defaults to mtwrf

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
submissions is considered submission time.
```

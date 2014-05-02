pystudentfetcher
================

Python 3 module. Given a string, fetches a selected set of files from a directory that matches given string. Looks for directories inside a provided set of source directories. Has support for late days. Outputs fetch results and copied files upon query completion.

Typical use case
================

Directory structure:
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

After installing pystudentfetcher on the python search path, we can fetch a student's work like this:

cd /workspace
python -m pystudentfetcher.fetch_student -s /Assignment1 -f calc.cpp -f calc.h b

This will fetch the files calc.cpp and calc.h from /Assignment1/bob to the current directory and report that bob is 0 days late. In this case, the given options are:

-s	Adds a directory source to look for student directories
-f	Adds a file to fetch

The positional argument is the key to look for students with. In this case, the key was b and since only bob contains b, that is the directory the system fetches from. As a rule, the system fetches the first matching directory.

We can also fetch like this:
cd /
python -m pystudentfetcher.fetch_student -s /Assignment1 -f calc.cpp -f calc.h -d /workspace b

In this case, we've added one option and the result is that while the current directory is /, fetched files are placed in /workspace.

-d	Sets the directory that fetched files should be placed in.

Late Days
=========

The system can also deal with "late days". The mechanism for this is incredibly simple. If the query matches a student directory that is directly underneath a directory with a name like "late 1" or "late 3", it reports back that the days late are 1 or 3 respectively.

For example, given the following directory structure:

/
	Assignment1
		late 5
			bob
				calc.cpp
				calc.h
				honesty.txt
		tracy
			sup.cpp
			calc.cpp
			calc.h
	workspace

Now if we do the same command as above:
cd /workspace
python -m pystudentfetcher.fetch_student -s /Assignment1 -f calc.cpp -f calc.h b

The system will report that bob was 5 days late.

Fetch Failure
=============

If the fetch fails for any reason, the query failure is reported and the reason why is indicated (eg no matching directory found, required file missing, etc...).



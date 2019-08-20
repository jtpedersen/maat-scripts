#!/bin/env python
#  git log --all --numstat --date=short --pretty=format:'--%h--%ad--%aN' --no-renames --after=2019-01-01  | this
import re
import sys

from collections import Counter

commit_pattern = r"^--(?P<rev>\w{5,8})--(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})--(?P<author>.*)$"
commit_matcher = re.compile(commit_pattern)

diff_pattern = r"^(?P<added>(\d+|-))\s(?P<deleted>(\d+|-))\s(?P<filename>.*)$"
diff_matcher = re.compile(diff_pattern)


class Edit:
    def __init__(self, rev, author, filename, added, deleted):
        self.rev = rev
        self.author = author
        self.filename = filename
        self.added = 1 if added == "-" else int(added)
        self.deleted = 1 if deleted == "-" else int(deleted)
    def __str__(self):
        return f"{self.author} {self.rev} {self.filename} {self.added} {self.deleted}"

class Project:
    def __init__(self):
        self.edits = []
        self.parser = Parser(self)

    def add(self, edit):
        self.edits.append(edit)

    def touch_top(self):
        """ How many times was a file touched"""
        counter = Counter()
        for e in self.edits:
            counter.update({e.filename: 1})

        for f,c in counter.most_common(10):
            print( f"{c}\t{f}")


    def edits_top(self):
        """ How many times was a file touched"""
        counter = Counter()
        for e in self.edits:
            counter.update({e.filename: e.added+ e.deleted})

        for f,c in counter.most_common(10):
            print( f"{c}\t{f}")


class Commit:
    def __init__(self, data):
        self.author = data["author"]
        self.rev = data["rev"]
        self.edits = []

    def add_diff(self, data):
        edit = Edit(self.rev, self.author, data["filename"], data["added"], data["deleted"])
        self.edits.append(edit)

    def __str__(self):
        return "\n\t".join([str(x) for x in self.edits])

    def __len__(self):
        return len(self.edits)

    def __getitem__(self, idx):
        return self.edits[idx]

class Parser:
    def __init__(self, project):
        self.cur = None
        self.project = project

    def start_commit(self, data):
#        print(f"start commit {data.groupdict()}")
        if self.cur:
            for e in self.cur:
                self.project.add(e)
#            print(self.cur)
        self.cur = Commit(data)

    def add_diff(self, data):
        if self.cur == None:
            print(f"No commit for {data.groupdict()} kjkj {self.cur}")
        else:
            self.cur.add_diff(data)


    def read_line(self,line):
        if len(line) == 0 :
            return
        m = commit_matcher.match(line)
        if m:
            self.start_commit(m)
        else:
            m = diff_matcher.match(line)
            if m:
                self.add_diff(m)
            else:
                print(f"no match om \"{line}\"")

def run():
    project = Project()
    parser = project.parser
    for line in sys.stdin:
        parser.read_line(line.strip());
    project.touch_top()
    project.edits_top()



if __name__ == "__main__":
    run()

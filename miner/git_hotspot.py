#!/bin/env python
#  git log --all --numstat --date=short --pretty=format:'--%h--%ad--%aN' --no-renames --after=2019-01-01  | this
import re
import sys

from collections import Counter

commit_pattern = r"^--(?P<rev>\w{8})--(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})--(?P<author>.*)$"
commit_matcher = re.compile(commit_pattern)

diff_pattern = r"^(?P<added>\d)+\s(?P<deleted>\d)+\s(?P<filename>.*)$"
diff_matcher = re.compile(diff_pattern)


class Edit:
    def __init__(self, rev, author, filename, added, deleted):
        self.rev = rev
        self.author = author
        self.filename = filename
        self.added = added
        self.deleted = deleted
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
        if self.cur:
            for e in self.cur:
                self.project.add(e)
            print(self.cur)
        self.cur = Commit(data)

    def read_line(self,line):
        m = commit_matcher.match(line)
        if m:
            self.start_commit(m)
            return
        edit_data = diff_matcher.match(line)
        if edit_data:
            self.cur.add_diff(edit_data)

def run():
    project = Project()
    parser = project.parser
    for line in sys.stdin:
        parser.read_line(line);
    project.touch_top()


if __name__ == "__main__":
    run()

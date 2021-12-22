#!/usr/bin/env python
# -*- mode: python; -*-

import argparse
import multiprocessing
import os
import re
import subprocess
import sys


def is_repo_initialized():
    return os.system("repo help 1> /dev/null 2>&1") == 0


def parse_project_line(line):
    line = line.strip()

    if not line.startswith("<") or not line.endswith(">"):
        return None

    # Remove start brace
    line = line[1:]

    # Remove end brace
    line = re.sub("/?>$", "", line).strip()

    tag = line.split()[0]
    attr_strings = line.split()[1:]
    attrs = {}
    for attr_string in attr_strings:
        if '=' in attr_string:
            attr, value = attr_string.split('=')
            value = value.replace('"', '').replace("'", '')
            attrs[attr] = value
        else:
            attrs[attr_string] = True
    return tag, attrs


def select_project():
    try:
        output = subprocess.check_output(
            "repo manifest | grep '<project' | fzf --multi --height=100%",
            shell=True)
        output = output.strip()
    except subprocess.CalledProcessError:
        output = ""

    return [pj.strip() for pj in output.splitlines()]


def extract_project_name(project):
    tag, attrs = parse_project_line(project)
    return attrs["name"]


def repo_sync(project_names, jobs):
    cmd = "repo sync --jobs=%d %s" % (jobs, " ".join(project_names))
    print(cmd)
    subprocess.call(cmd.split())


def main(args):
    if not is_repo_initialized():
        sys.stderr.write(
            "error: command'manifest' requires repo to be installed first.\n"
            "         Use \"repo init\" to install it here.\n")
        return 1

    projects = select_project()
    project_names = [extract_project_name(project) for project in projects]

    if args.jobs:
        jobs = args.jobs
    else:
        jobs = multiprocessing.cpu_count() + 1

    if len(project_names) < 1:
        return 1

    return repo_sync(project_names, jobs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=None)
    args = parser.parse_args()
    sys.exit(main(args))

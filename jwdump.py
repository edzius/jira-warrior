#!/usr/bin/env python

import sys
import os
import re
from configparser import ConfigParser

from jira import JIRA


def parse_sprints(issue):
    if not issue:
        return []

    sprints_def = None
    for key, val in issue.fields.__dict__.items():
        if type(val) != list or len(val) == 0 or type(val[0]) != str:
            continue

        if not re.search("com.atlassian.greenhopper.service.sprint.Sprint", val[0]):
            continue

        sprints_def = val
        break

    if not sprints_def:
        return []

    sprints = []
    for sd in sprints_def:
        content = re.match(".*?\[(.+?)\].*?", sd)
        if not content:
            continue

        name = re.search("name=([^,]+)", content.group(1))
        if not name:
            continue

        sprints.append(name.group(1))

        # XXX: in case we would need all springs info
        #sprint = {}
        #for item in re.finditer("(\w+)=([^,]+),?", content.group(1)):
        #    sprint[item.group(1)] = item.group(2)
        #sprints.append(sprint)

    return sprints


def jw_config(project):
    config = ConfigParser()

    files = []
    files.append("jw.conf")
    files.append("/etc/jw.conf")
    if os.getenv("HOME"):
        files.append(os.getenv("HOME") + "/.jw.conf")

    config.read(files)

    section = {}
    if project:
        section.update(config.items(project))
    else:
        section.update(config.items(config.sections()[0]))

    return section


if __name__ == '__main__':
    config = jw_config(sys.argv[1] if len(sys.argv) > 1 else None)

    jira_project = config["project"]
    jira_board = config["board"]
    options = {
        "server": config["server"],
        "agile_rest_path": "agile",
    }
    basic_auth = (config["username"], config["password"],)
    jira = JIRA(options=options, basic_auth=basic_auth)

    issues = jira.search_issues('project=%s AND sprint in openSprints()' %
                                (jira_project,), maxResults=1)

    if len(issues) == 0:
        print("No issues")
    else:
        for attr, value in issues[0].__dict__.items():
            print("---------")
            print(attr, value)
            print("=========")

        print(parse_sprints(issues[0]))

    exit(0)

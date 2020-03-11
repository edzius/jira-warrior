#!/usr/bin/env python

import re
import sys
import datetime
from termcolor import colored

import jwargs
import jwconf
import jwfetch
import jwprint


def die(msg):
    print(msg)
    sys.exit(1)


def jw_version_by_name(version_name):
    versions = jwfetch.jw_versions()
    for version in versions:
        if version.name.find(version_name) == -1:
            continue
        return version

    die("Version not found: %s" % version_name)


def jw_sprint_by_name(sprint_name):
    sprints = jwfetch.jw_sprints()
    for sprint in sprints:
        if sprint.name.find(sprint_name) == -1:
            continue
        return sprint

    die("Sprint not found: %s" % sprint_name)


def jw_sprint_by_relevance(sprint_offset):
    dateNow = datetime.datetime.now().replace(tzinfo=None)
    sprint_number = -1
    sprints = jwfetch.jw_sprints()
    # Assumes sprints are sorted timewise.
    for sprint in sprints:
        sprint_number += 1
        if sprint.dateFrom and sprint.dateFrom > dateNow:
            continue
        elif sprint.dateTo and sprint.dateTo < dateNow:
            continue

        break

    sprint_number += sprint_offset
    if sprint_number > len(sprints):
        return sprints[len(sprints)-1]
    elif sprint_number < 0:
        return sprints[0]
    else:
        return sprints[sprint_number]


def jw_date_by_relevance(date_offset):
    match = re.match("(\-?\d+)([hdw])", date_offset)
    if not match:
        return None, None

    count = match.group(1)
    scale = match.group(2)
    dnow = datetime.datetime.now().replace(tzinfo=None)
    if scale == "h":
        dnew = dnow + datetime.timedelta(hours=int(count))
    elif scale == "d":
        dnow = dnow.replace(hour=0, minute=0, second=0, microsecond=0)
        dnew = dnow + datetime.timedelta(days=int(count))
    elif scale == "w":
        dnow = dnow.replace(hour=0, minute=0, second=0, microsecond=0)
        dnow = dnow - datetime.timedelta(days=dnow.weekday())
        dnew = dnow + datetime.timedelta(weeks=int(count))

    if dnow > dnew:
        dfrom = dnew
        dto = dnow
    else:
        dfrom = dnow
        dto = dnew

    return dfrom, dto


def _jw_group_tasks_by_assignee(tasks):
    groups = {}
    for task in tasks:
        assignee = "Unassigned"
        if task.fields.assignee:
            assignee = task.fields.assignee.displayName

        if assignee not in groups:
            groups[assignee] = []

        groups[assignee].append(task)

    return groups


def _jw_filter_tasks_by_type(tasks, taskType):
    filtered = []
    for task in tasks:
        if taskType == "Bug" and task.fields.issuetype.name != "Bug":
            continue
        elif taskType == "Technical Story" and task.fields.issuetype.name != "Technical Story":
            continue
        elif taskType == "User Story" and task.fields.issuetype.name != "User Story":
            continue
        elif taskType == "Support Task" and task.fields.issuetype.name != "Support Task":
            continue
        elif taskType == "Epic" and task.fields.issuetype.name != "Epic":
            continue

        filtered.append(task)

    return filtered


def _jw_filter_tasks_by_state(tasks, taskState):
    filtered = []
    for task in tasks:
        if taskState == "Open" and task.fields.status.name == "Closed":
            continue
        elif taskState == "Closed" and task.fields.status.name != "Closed":
            continue
        elif taskState == "Done" and task.fields.status.name != "In Review":
            continue
        elif taskState == "Working" and (task.fields.status.name != "In Progress" and task.fields.status.name != "In Review"):
            continue
        elif taskState == "Pending" and (task.fields.status.name != "Open" and task.fields.status.name != "Paused"):
            continue

        filtered.append(task)

    return filtered


def jw_run():
    params = jwargs.jw_options()
    config = jwconf.jw_config(params.project)

    jwfetch.jw_init(config, params)

    if params.showVersions:
        versions = jwfetch.jw_versions()
        jwprint.jw_print_versions(versions)
    elif params.showSprints:
        sprints = jwfetch.jw_sprints()
        jwprint.jw_print_sprints(sprints)
    elif params.showTasks:
        if params.lookupVersion:
            version = jw_version_by_name(params.lookupVersion)
            tasks = jwfetch.jw_tasks_by_version(version.name)
            printer = jwprint.jw_task_printer(params,
                                              jwprint.TasksInState(),
                                              version=version,
                                              dateFrom=version.dateFrom,
                                              dateTo=version.dateTo)
            if not params.showBrief:
                sys.stdout.write("Tasks in version: %s\n" % version.name)
        elif params.lookupSprint:
            sprint = jw_sprint_by_name(params.lookupSprint)
            tasks = jwfetch.jw_tasks_by_sprint(sprint.name)
            printer = jwprint.jw_task_printer(params,
                                              jwprint.TasksInRange(sprint.dateFrom, sprint.dateTo),
                                              sprint=sprint, dateFrom=sprint.dateFrom,
                                              dateTo=(sprint.dateDone or sprint.dateTo))
            if not params.showBrief:
                sys.stdout.write("Tasks in sprint: %s\n" % sprint.name)
        elif params.lookupPeriod:
            if params.findVersion:
                version = jw_version_by_name(params.findVersion)
                dateFrom, dateTo = version.dateFrom, version.dateTo
                printer = jwprint.jw_task_printer(params,
                                                  jwprint.TasksInVersion(version),
                                                  version=version,
                                                  dateFrom=dateFrom,
                                                  dateTo=dateTo)
            elif params.findSprint:
                sprint = jw_sprint_by_name(params.findSprint)
                dateFrom, dateTo = sprint.dateFrom, sprint.dateDone or sprint.dateTo
                printer = jwprint.jw_task_printer(params,
                                                  jwprint.TasksInSprint(sprint),
                                                  sprint=sprint,
                                                  dateFrom=dateFrom,
                                                  dateTo=dateTo)
            elif params.relSprint != None:
                sprint = jw_sprint_by_relevance(params.relSprint)
                dateFrom, dateTo = sprint.dateFrom, sprint.dateDone or sprint.dateTo
                printer = jwprint.jw_task_printer(params,
                                                  jwprint.TasksInSprint(sprint),
                                                  sprint=sprint,
                                                  dateFrom=dateFrom,
                                                  dateTo=dateTo)
            elif params.relDate != None:
                dateFrom, dateTo = jw_date_by_relevance(params.relDate)
                printer = jwprint.jw_task_printer(params,
                                                  params.onlyResolved and
                                                  jwprint.TasksInType() or
                                                  jwprint.TasksInState(),
                                                  dateFrom=dateFrom,
                                                  dateTo=dateTo)
            else:
                dateFrom, dateTo = jw_date_by_relevance('-24h')
                printer = jwprint.jw_task_printer(params,
                                                  params.onlyResolved and
                                                  jwprint.TasksInType() or
                                                  jwprint.TasksInState(),
                                                  dateFrom=dateFrom,
                                                  dateTo=dateTo)

            tasks = jwfetch.jw_tasks_by_date(dateFrom, dateTo)
            if not params.showBrief:
                sys.stdout.write("Tasks in period: %s - %s\n" %
                                 (dateFrom.strftime("%Y-%m-%d"),
                                  dateTo.strftime("%Y-%m-%d"),))
        else:
            dateFrom, dateTo = jw_date_by_relevance('-24h')
            printer = jwprint.jw_task_printer(params,
                                              params.onlyResolved and
                                              jwprint.TasksInType() or
                                              jwprint.TasksInState(),
                                              dateFrom=dateFrom,
                                              dateTo=dateTo)
            tasks = jwfetch.jw_tasks_by_date(dateFrom, dateTo)
            if not params.showBrief:
                sys.stdout.write("Recent tasks\n")

        if params.typeFilter:
            tasks = _jw_filter_tasks_by_type(tasks, params.typeFilter)

        if params.stateFilter:
            tasks = _jw_filter_tasks_by_state(tasks, params.stateFilter)

        if not params.showBrief and len(tasks) == 0:
            die("Tasks not found")

        groups = _jw_group_tasks_by_assignee(tasks)
        if params.showBrief:
            for name, taskgroup in groups.items():
                sys.stdout.write("%s: " % name)
                printer.brief(taskgroup)
        elif params.showDetail:
            for name, taskgroup in groups.items():
                sys.stdout.write("\n%s:\n\n" % name)
                printer.detail(taskgroup)
        else:
            for name, taskgroup in groups.items():
                sys.stdout.write("\n%s:\n\n" % name)
                printer.normal(taskgroup)
    else:
        print("Projects:\n")
        projects = jwfetch.jw_projects()
        for project in projects:
            print("* %s - %s" % (project.key, project.name,))
            versions = jwfetch.jw_versions(project)
            if len(versions) == 0:
                continue
            print("\n  - %s\n" % "\n  - ".join([version.name for version in jwfetch.jw_versions(project)]))

        print()
        print("Boards:\n")
        boards = jwfetch.jw_boards()
        for board in boards:
            print("* %s" % (board.name,))
            sprints = jwfetch.jw_sprints(board)
            if len(sprints) == 0:
                continue
            print("\n  - %s\n" % "\n  - ".join([sprint.name for sprint in jwfetch.jw_sprints(board)]))


if __name__ == '__main__':
    jw_run()

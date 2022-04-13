#!/usr/bin/env python3

import re
import sys
import math
import datetime

from jw import options as jwoptions
from jw import config as jwconfig
from jw import fetch as jwfetch
from jw import properties as jwprops
from jw import summary as jwsummary
from jw import versions as jwversions
from jw import sprints as jwsprints
from jw import tasks as jwtasks


def die(msg):
    print(msg)
    sys.exit(1)


def year_week(dt):
    dcurrent = dt.date()
    dfirst = dcurrent.replace(month = 1, day = 1)
    drange = dcurrent - dfirst
    return math.floor(drange.days / 7)


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


def _jw_task_property_getter(name):
    if name == 'type':
        return lambda task: task.fields.issuetype.name
    elif name == 'state':
        return lambda task: task.fields.status.name
    elif name == 'assignee':
        return lambda task: task.fields.assignee.displayName
    elif name == 'reporter':
        return lambda task: task.fields.reporter.displayName
    elif name == 'sprint':
        return lambda task: jwprops.taskSprints(task, True)
    elif name == 'version':
        return lambda task: jwprops.taskVersions(task, True)
    else:
        raise "Unknown property name " + name

def _jw_task_type(name, task):
    if name == "Support Task":
        return "Support"
    elif name == "User Story":
        return "Feature"
    elif name == "Technical Story":
        return "Task"
    else:
        return name

def _jw_task_state(name, task):
    if name == "Pending Estimation":
        return "Estimating"
    elif name == "Defining Story":
        return "Defining"
    else:
        return name

def _jw_task_person(name, task):
    name, sep, rest = name.partition(' ')
    return name

def _jw_task_sprint(name, task):
    res = re.match("\S+ \S+", name)
    if not res:
        return name
    return res.group(0)

def _jw_task_version(name, task):
    if len(name) < 15:
        return name
    else:
        p1, s, p2 = name.partition('-')
        return p1[:14]

def jw_run():
    params = jwoptions.parse()
    config = jwconfig.get(params.project)

    jwfetch.jw_init(config, params)

    if params.showTasks:
        if params.showInspect:
            if params.showInspect == True:
                task = jwfetch.jw_tasks_by_precedence(1)[0]
            else:
                task = jwfetch.jw_tasks_by_key(params.showInspect)
            jwtasks.debug(task)
            return

        if params.lookupVersion:
            version = jw_version_by_name(params.lookupVersion)
            tasks = jwfetch.jw_tasks_by_version(version.name, params)
            print("Tasks version: %s" % version.name)
        elif params.lookupSprint:
            sprint = jw_sprint_by_name(params.lookupSprint)
            tasks = jwfetch.jw_tasks_by_sprint(sprint.name, params)
            print("Tasks sprint: %s" % sprint.name)
        elif params.lookupPeriod:
            if params.findVersion:
                version = jw_version_by_name(params.findVersion)
                dateFrom, dateTo = version.dateFrom, version.dateTo
            elif params.findSprint:
                sprint = jw_sprint_by_name(params.findSprint)
                dateFrom, dateTo = sprint.dateFrom, sprint.dateDone or sprint.dateTo
            elif params.relSprint != None:
                sprint = jw_sprint_by_relevance(params.relSprint)
                dateFrom, dateTo = sprint.dateFrom, sprint.dateDone or sprint.dateTo
            elif params.relDate != None:
                dateFrom, dateTo = jw_date_by_relevance(params.relDate)
            else:
                dateFrom, dateTo = jw_date_by_relevance('-24h')

            print("Tasks week: %i - %i" % (year_week(dateFrom), year_week(dateTo),))
            print("Tasks date: %s - %s" % (dateFrom.strftime("%Y-%m-%d"), dateTo.strftime("%Y-%m-%d"),))

            tasks = jwfetch.jw_tasks_by_date(params.findState, dateFrom, dateTo, params)
        elif params.lookupList:
            tasks = []
            for item in params.lookupList:
                tasks.append(jwfetch.jw_tasks_by_key(item))
        else:
            tasks = jwfetch.jw_tasks_by_precedence(params.lookupLimit, params)

        if len(tasks) == 0:
            print("Tasks not found")
            return

        tasks_total = len(tasks)

        # Apply filtering
        if params.taskChangeStatus:
            tasks = jwtasks.FilterChangedStatus(dateFrom, dateTo).digest(tasks)
        if params.taskChangeResolution:
            tasks = jwtasks.FilterChangedResolution(dateFrom, dateTo).digest(tasks)

        tasks_shown = len(tasks)
        print("Tasks total: %u/%u" % (tasks_shown, tasks_total,))

        if params.showSummary:
            printing = jwtasks.TasksStream()
            heading = jwtasks.TasksInline()
        else:
            printing = jwtasks.TasksPrinter()
            heading = None
            if params.showBrief:
                printing.mapping('type', _jw_task_type, "%-10s")
                printing.mapping('state', _jw_task_state, "%-12s")
                printing.mapping('assignee', _jw_task_person, "%-10s")
                printing.mapping('reporter', _jw_task_person, "%-10s")
                printing.mapping('sprint', _jw_task_sprint, "%-10s")
                printing.mapping('version', _jw_task_version, "%-15s")

            if not params.taskPrint:
                printing.default()
            else:
                printing.include(*params.taskPrint)

        grouping = jwtasks.TasksGroups()
        for group in params.taskGroup or []:
            grouping.group(_jw_task_property_getter(group), heading)
        grouping.print(printing)
        grouping.digest(tasks)
    elif params.showSprints:
        if params.showInspect:
            jwsprints.debug(params.showInspect)
            return
        jwsprints.run()
    elif params.showVersions:
        if params.showInspect:
            jwversions.debug(params.showInspect)
            return
        jwversions.run()
    else:
        jwsummary.run()


if __name__ == '__main__':
    jw_run()

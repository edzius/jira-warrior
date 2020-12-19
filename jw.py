#!/usr/bin/env python

import re
import sys
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
        if params.showDebug:
            if params.showDebug == True:
                task = jwfetch.jw_tasks_by_precedence(1)[0]
            else:
                task = jwfetch.jw_tasks_by_key(params.showDebug)
            jwtasks.debug(task)
            return

        if params.lookupVersion:
            version = jw_version_by_name(params.lookupVersion)
            tasks = jwfetch.jw_tasks_by_version(version.name)
        elif params.lookupSprint:
            sprint = jw_sprint_by_name(params.lookupSprint)
            tasks = jwfetch.jw_tasks_by_sprint(sprint.name)
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

            tasks = jwfetch.jw_tasks_by_date(dateFrom, dateTo, params.findActivity or "updated")
        else:
            tasks = jwfetch.jw_tasks_by_precedence(params.lookupLimit)

        if len(tasks) == 0:
            print("Tasks not found")
            return

        # Configure tasks filters
        filtering = jwtasks.TasksFilter()
        for fgroup in params.taskFilter or []:
            flist = []
            for ftype, fvalue in fgroup:
                if ftype == 'state':
                    flist.append(jwtasks.FilterByState(fvalue))
                elif ftype == 'type':
                    flist.append(jwtasks.FilterByType(fvalue))
                else:
                    fwlog.warn("unknow filter type: %s=%s" % (ftype, fvalue,))

            filtering.add(*flist)

        tasks = filtering.digest(tasks)

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
        if params.showDebug:
            jwsprints.debug(params.showDebug)
            return
        jwsprints.run()
    elif params.showVersions:
        if params.showDebug:
            jwversions.debug(params.showDebug)
            return
        jwversions.run()
    else:
        jwsummary.run()


if __name__ == '__main__':
    jw_run()

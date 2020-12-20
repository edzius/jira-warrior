
import sys
import datetime

from jira import JIRA


jira_project = None
jira_board = None
jira = None
jw_config = None
jw_params = None


def jw_init(config, params):
    global jira_project
    global jira_board
    global jira
    global jw_config
    global jw_params

    jw_config = config
    jw_params = params

    jira_project = config.project
    jira_board = config.board
    options = {
        "server": config.server,
        "agile_rest_path": "agile",
    }
    basic_auth = (config.username, config.password,)
    jira = JIRA(options=options, basic_auth=basic_auth)


def jw_projects():
    return jira.projects()


def jw_boards():
    return jira.boards()


def jw_versions(project=None):
    try:
        versions = jira.project_versions(project.key if project else jira_project)
    except:
        return []

    for version in versions:
        if hasattr(version, 'startDate'):
            version.dateFrom = datetime.datetime.strptime(version.startDate, "%Y-%m-%d")
        else:
            version.dateFrom = None

        if hasattr(version, 'releaseDate'):
            version.dateTo = datetime.datetime.strptime(version.releaseDate, "%Y-%m-%d")
        else:
            version.dateTo = None

        if not hasattr(version, 'name'):
            version.name = None

        if not hasattr(version, 'description'):
            version.description = None

    return sorted(versions, key=lambda version: version.dateTo and datetime.datetime.timestamp(version.dateTo) or sys.maxsize)


def jw_sprints(board=None):
    if not board:
        boards = jira.boards()
        board = [board for board in boards if board.name == jira_board][0]
    try:
        sprints = jira.sprints(board.id)
    except:
        return []

    for sprint in sprints:
        if hasattr(sprint, 'startDate'):
            sprint.dateFrom = datetime.datetime.strptime(sprint.startDate, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        else:
            sprint.dateFrom = None

        if hasattr(sprint, 'completeDate'):
            sprint.dateDone = datetime.datetime.strptime(sprint.completeDate, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        else:
            sprint.dateDone = None

        if hasattr(sprint, 'endDate'):
            sprint.dateTo = datetime.datetime.strptime(sprint.endDate, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)
        else:
            sprint.dateTo = None

    return sorted(sprints, key=lambda sprint: sprint.dateFrom and datetime.datetime.timestamp(sprint.dateFrom) or sys.maxsize)


def jw_tasks(params, version=None, sprint=None, dateFrom=None, dateTo=None, taskState="updated", taskCount=1000):
    items = []
    items.append('project=%s' % jira_project)
    if version:
        items.append('fixVersion="%s"' % version)
    if sprint:
        items.append('sprint="%s"' % sprint)
    if dateFrom:
        if taskState == "updated":
            items.append('updated>="%s"' % dateFrom.strftime("%Y-%m-%d %H:%M"))
        elif taskState == "resolved":
            items.append('resolved>="%s"' % dateFrom.strftime("%Y-%m-%d %H:%M"))
        elif taskState == "created":
            items.append('created>="%s"' % dateFrom.strftime("%Y-%m-%d %H:%M"))
        else:
            raise TypeError("Unknown state '%s'" % taskState)
    if dateTo:
        if taskState == "updated":
            items.append('updated<="%s"' % dateTo.strftime("%Y-%m-%d %H:%M"))
        elif taskState == "resolved":
            items.append('resolved<="%s"' % dateTo.strftime("%Y-%m-%d %H:%M"))
        elif taskState == "created":
            items.append('created<="%s"' % dateTo.strftime("%Y-%m-%d %H:%M"))
        else:
            raise TypeError("Unknown state '%s'" % taskState)

    taskExpand = None
    if params:
        for fgroup in params.taskFilter or []:
            flist = []
            for ftype, fvalue in fgroup:
                if ftype == 'type':
                    flist.append('issuetype="%s"' % fvalue)
                elif ftype == 'state':
                    if fvalue == "Incomplete":
                        flist.append('(status!="Closed" AND status!="Done" AND status!="Resolved")')
                    elif fvalue == "Complete":
                        flist.append('(status="Closed" OR status="Done" OR status="Resolved")')
                    elif fvalue == "Working":
                        flist.append('(status="In Progress" OR status="In Review")')
                    elif fvalue == "Pending":
                        flist.append('(status="Open" OR status="Paused" OR status="To Do" OR status="Reopened")')
                    else:
                        flist.append('status="%s"' % fvalue)

            if len(flist) > 0:
                items.append("(%s)" % " OR ".join(flist))

        # Expand changelog when history is needed
        if params.taskChangeStatus or params.taskChangeResolution:
            taskExpand = "changelog"

    searchQuery = " AND ".join(items)

    if params.showVerbose:
        print(">", searchQuery)

    return jira.search_issues(searchQuery,
                              maxResults=taskCount,
                              expand=taskExpand)


def jw_tasks_by_key(key):
    return jira.issue(key, expand='changelog')


def jw_tasks_by_precedence(count, params):
    return jw_tasks(params, taskCount=count)


def jw_tasks_by_date(taskState, dateFrom, dateTo, params):
    if not dateFrom and not dateTo:
        raise TypeError("No date")

    return jw_tasks(params, dateFrom=dateFrom, dateTo=dateTo, taskState=taskState)


def jw_tasks_by_sprint(sprint, params):
    if not sprint:
        raise TypeError("No sprint")

    return jw_tasks(params, sprint=sprint)


def jw_tasks_by_version(version, params):
    if not version:
        raise TypeError("No version")

    return jw_tasks(params, version=version)

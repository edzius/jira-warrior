
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


def jw_versions():
    versions = jira.project_versions(jira_project)
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


def jw_sprints():
    boards = jira.boards()
    board = [board for board in boards if board.name == jira_board][0]
    sprints = jira.sprints(board.id)

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


def jw_tasks_by_date(dateFrom, dateTo=None):
    if dateFrom and dateTo:
        if jw_params.onlyResolved:
            query = 'project=%s AND resolved>="%s" AND resolved<="%s"'
        else:
            query = 'project=%s AND updated>="%s" AND updated<="%s"'
        return jira.search_issues(query %
                                  (jira_project,
                                   dateFrom.strftime("%Y-%m-%d %H:%M"),
                                   dateTo.strftime("%Y-%m-%d %H:%M"),),
                                  maxResults=1000)
    elif dateFrom:
        if jw_params.onlyResolved:
            query = 'project=%s AND resolved>="%s"'
        else:
            query = 'project=%s AND updated>="%s"'
        return jira.search_issues(query %
                                  (jira_project,
                                   dateFrom.strftime("%Y-%m-%d %H:%M"),),
                                  maxResults=1000)
    else:
        raise "No date"


def jw_tasks_by_sprint(sprint):
    return jira.search_issues('project=%s AND sprint="%s"' %
                              (jira_project, sprint,),
                              maxResults=1000)


def jw_tasks_by_version(version):
    return jira.search_issues('project=%s AND fixVersion="%s"' %
                                  (jira_project, version,),
                                  maxResults=1000)

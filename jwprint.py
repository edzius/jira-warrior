
import re
import datetime
from termcolor import colored


def parse_task_versions(task):
    if not task:
        return []

    versions = []
    for version in task.fields.fixVersions:
        versions.append(version.name)

    return versions


def parse_task_sprints(task):
    if not task:
        return []

    sprints_def = None
    for key, val in task.fields.__dict__.items():
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


class TasksPrinter:
    def __init__(self):
        pass

    def brief(self, tasks):
        print("; ".join(["%s" % task.key for task in tasks]))

    def detail(self, tasks):
        pass

    def normal(self, tasks):
        pass


class TasksInRange(TasksPrinter):
    def __init__(self, dateFrom, dateTo=None):
        TasksPrinter.__init__(self)
        self.dateFrom = dateFrom
        self.dateTo = dateTo

    def _color_by_resolution(self, task):
        # green -- resolved on given time
        # yellow -- resolved not on time
        # red -- not resolved
        # white -- no date ranges
        if not self.dateFrom and not self.dateTo:
            return "white"

        if not task.fields.resolutiondate:
            return "red"

        dateResolve = datetime.datetime.strptime(task.fields.resolutiondate, "%Y-%m-%dT%H:%M:%S.%f%z").replace(tzinfo=None)

        color = "green"
        if self.dateFrom and self.dateFrom > dateResolve:
            color = "yellow"

        if self.dateTo and self.dateTo < dateResolve:
            color = "yellow"

        return color

    def detail(self, tasks):
        for task in tasks:
            color = self._color_by_resolution(task)
            print(colored("%-10s %-20s %-20s %s" % (task.key, task.fields.issuetype.name, task.fields.status.name, task.fields.summary,), color))

    def normal(self, tasks):
        for task in tasks:
            color = self._color_by_resolution(task)
            print(colored("%-10s %s" % (task.key, task.fields.summary,), color))


class TasksInType(TasksPrinter):
    def __init__(self):
        TasksPrinter.__init__(self)

    def _color_by_type(self, task):
        # red -- bug
        # yellow -- Support Task
        # green -- Technical Story
        # cyan -- User Story
        # magenta -- Epic
        # white -- unknown task
        if task.fields.issuetype.name == "Bug":
            return "red"
        elif task.fields.issuetype.name == "Technical Story":
            return "green"
        elif task.fields.issuetype.name == "User Story":
            return "cyan"
        elif task.fields.issuetype.name == "Support Task":
            return "yellow"
        elif task.fields.issuetype.name == "Epic":
            return "magenta"
        else:
            return "white"

    def detail(self, tasks):
        for task in tasks:
            color = self._color_by_type(task)
            print(colored("%-10s %-20s %-20s %s" % (task.key, task.fields.issuetype.name, task.fields.status.name, task.fields.summary,), color))

    def normal(self, tasks):
        for task in tasks:
            color = self._color_by_type(task)
            print(colored("%-10s %s" % (task.key, task.fields.summary,), color))


class TasksInState(TasksPrinter):
    def __init__(self):
        TasksPrinter.__init__(self)

    def _color_by_state(self, task):
        # green -- closed tasks
        # yellow -- started or finished
        # red -- not started or suspended
        # white -- unknown states
        if task.fields.status.name == "Closed":
            return "green"
        elif (task.fields.status.name != "In Progress" and task.fields.status.name != "In Review"):
            return "yellow"
        elif (task.fields.status.name != "Open" and task.fields.status.name != "Paused"):
            return "red"
        else:
            return "white"

    def detail(self, tasks):
        for task in tasks:
            color = self._color_by_state(task)
            print(colored("%-10s %-20s %-20s %s" % (task.key, task.fields.issuetype.name, task.fields.status.name, task.fields.summary,), color))

    def normal(self, tasks):
        for task in tasks:
            color = self._color_by_state(task)
            print(colored("%-10s %s" % (task.key, task.fields.summary,), color))


class TasksInSprint(TasksPrinter):
    def __init__(self, sprint):
        TasksPrinter.__init__(self)
        self.sprint = sprint

    def _color_by_sprint(self, task):
        # green -- in current sprint
        # yellow -- no sprint
        # red -- in other sprints
        sprints = parse_task_sprints(task)

        color = "yellow"
        if self.sprint.name:
            if self.sprint.name in sprints:
                color = "green"
            else:
                color = "red"

        return color

    def detail(self, tasks):
        for task in tasks:
            color = self._color_by_sprint(task)
            print(colored("%-10s %-20s %-20s %s" % (task.key, task.fields.issuetype.name, task.fields.status.name, task.fields.summary,), color))

    def normal(self, tasks):
        for task in tasks:
            color = self._color_by_sprint(task)
            print(colored("%-10s %s" % (task.key, task.fields.summary,), color))


class TasksInVersion(TasksPrinter):
    def __init__(self, version):
        TasksPrinter.__init__(self)
        self.version = version

    def _color_by_version(self, task):
        # green -- in current sprint
        # yellow -- no sprint
        # red -- in other sprints
        versions = parse_task_versions(task)

        color = "yellow"
        if self.version.name:
            if self.version.name in versions:
                color = "green"
            else:
                color = "red"

        return color

    def detail(self, tasks):
        for task in tasks:
            color = self._color_by_version(task)
            print(colored("%-10s %-20s %-20s %s" % (task.key, task.fields.issuetype.name, task.fields.status.name, task.fields.summary,), color))

    def normal(self, tasks):
        for task in tasks:
            color = self._color_by_version(task)
            print(colored("%-10s %s" % (task.key, task.fields.summary,), color))


def jw_task_printer(params, default, **kwargs):
    if params.markMode == 'State':
        return TasksInState()
    elif params.markMode == 'Type':
        return TasksInType()
    elif params.markMode == 'Range' and 'dateFrom' in kwargs and 'dateTo' in kwargs:
        return TasksInRange(kwargs['dateFrom'], kwargs['dateTo'])
    elif params.markMode == 'Sprint' and 'sprint' in kwargs:
        return TasksInSprint(kwargs['sprint'])
    elif params.markMode == 'Version' and 'version' in kwargs:
        return TasksInVersion(kwargs['version'])
    else:
        return default


def jw_print_versions(versions):
    dateNow = datetime.datetime.now().replace(tzinfo=None)
    for version in versions:
        # blue -- released versions
        # cyan -- archived versions
        # yellow -- future development versions
        # green -- current development versions
        # red -- non-released passed versions
        if version.released:
            color = "blue"
        elif version.archived:
            color = "cyan"
        elif version.dateFrom and version.dateFrom > dateNow:
            color = "yellow"
        elif version.dateTo and version.dateTo > dateNow:
            color = "green"
        elif not version.dateTo and not version.dateFrom:
            color = "yellow"
        else:
            color = "red"

        if version.description:
            label = "%s (%s)" % (version.name, version.description,)
        else:
            label = version.name

        print(colored("%-10s - %-10s | %s" %
                      (version.dateFrom.strftime("%Y-%m-%d") if version.dateFrom else "N/A",
                       version.dateTo.strftime("%Y-%m-%d") if version.dateTo else "N/A",
                       label,),
                      color))


def jw_print_sprints(sprints):
    dateNow = datetime.datetime.now().replace(tzinfo=None)
    for sprint in sprints:
        # blue -- past sprints completed in time
        # red -- past spritns off schedule
        # yellow -- future sprints
        # green -- current sprint
        dateStart = sprint.dateFrom
        dateStop = None
        if dateStart and dateStart < dateNow:
            color = "green"
        else:
            color = "yellow"

        if sprint.dateDone and sprint.dateTo:
            dateStop = sprint.dateDone
            if sprint.dateTo < sprint.dateDone:
                color = "red"
            elif sprint.dateDone < dateNow:
                color = "blue"
        elif sprint.dateDone:
            dateStop = sprint.dateDone
            if sprint.dateDone < dateNow:
                color = "blue"
        elif sprint.dateTo:
            dateStop = sprint.dateTo
            if sprint.dateTo < dateNow:
                color = "red"

        print(colored("%-10s - %-10s | %s" %
                      (dateStart.strftime("%Y-%m-%d") if dateStart else "N/A",
                       dateStop.strftime("%Y-%m-%d") if dateStop else "N/A",
                       sprint.name,),
                      color))

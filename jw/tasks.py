
import sys
import datetime
from . import properties as jwprops

def all(*args):
    result = []
    for arg in args:
        result.extend(arg)
    return result


def checkRecordDate(record, dateFrom, dateTo):
    dateStr = record.created.split('T')[0]
    dateRec = datetime.datetime.strptime(dateStr, "%Y-%m-%d")
    if dateFrom and dateFrom > dateRec:
        return False
    if dateTo and dateTo < dateRec:
        return False
    return True


def getRecordField(record, field):
    for item in record.items:
        if item.field == field:
            return item
    return None


class FilterChangedStatus:

    def __init__(self, dateFrom, dateTo):
        self.dateFrom = dateFrom
        self.dateTo = dateTo

    def digest(self, tasks):
        filtered = []
        for task in tasks:
            found = False
            for record in task.changelog.histories:
                if not checkRecordDate(record, self.dateFrom, self.dateTo):
                    continue

                if not getRecordField(record, "status"):
                    continue

                found = True
                break
            if found:
                filtered.append(task)

        return filtered


class FilterChangedResolution:

    def __init__(self, dateFrom, dateTo):
        self.dateFrom = dateFrom
        self.dateTo = dateTo

    def digest(self, tasks):
        filtered = []
        for task in tasks:
            for record in task.changelog.histories:
                if not checkRecordDate(record, self.dateFrom, self.dateTo):
                    continue

                if not getRecordField(record, "resolution"):
                    continue

                filtered.append(task)
                break

        return filtered


class FilterByType:

    def __init__(self, name):
        self.taskType = name

    def run(self, data):
        filtered = []
        for task in data:
            if self.taskType == "Bug" and task.fields.issuetype.name != "Bug":
                continue
            elif self.taskType == "Technical Story" and task.fields.issuetype.name != "Technical Story":
                continue
            elif self.taskType == "User Story" and task.fields.issuetype.name != "User Story":
                continue
            elif self.taskType == "Support Task" and task.fields.issuetype.name != "Support Task":
                continue
            elif self.taskType == "Epic" and task.fields.issuetype.name != "Epic":
                continue

            filtered.append(task)

        return filtered


class FilterByState:

    def __init__(self, name):
        self.taskState = name

    """
    Filters tasks by state:
        - Open -- Tasks that are not "Done"; "In Review" is not done!
        - Done -- Tasks that are fully finished; review and testing included!
        - Working -- Tasks currenly work in progress.
        - Pending -- Tasks that were not started yet.
    """
    def run(self, data):
        filtered = []
        for task in data:
            if self.taskState == "Open" and task.fields.status.name == "Closed":
                continue
            elif self.taskState == "Done" and task.fields.status.name != "Closed":
                continue
            elif self.taskState == "Working" and (task.fields.status.name != "In Progress" and task.fields.status.name != "In Review"):
                continue
            elif self.taskState == "Pending" and (task.fields.status.name != "Open" and task.fields.status.name != "Paused"):
                continue

            filtered.append(task)

        return filtered


class TasksFilter:

    def __init__(self):
        self.do_filter = []

    def add(self, *args):
        self.do_filter.append(args)
        return self

    def digest(self, tasks):
        for item_and in self.do_filter:
            found = []
            for item_or in item_and:
                found.extend([rv for rv in item_or.run(tasks) if rv not in found])
            tasks = found

        return tasks
        propFn = buildPropertyFn(name)


class GroupBuilder:

    def __init__(self, propFn, showFn):
        self.propFn = propFn
        self.showFn = showFn

    def iterate(self, tasks):
        groups = {}
        for task in tasks:
            prop = self.propFn(task)
            if prop not in groups:
                groups[prop] = []
            groups[prop].append(task)

        for group in groups.values():
            yield group

    def display(self, tasks):
        if not self.showFn:
            return
        if len(tasks) == 0:
            return
        task = tasks[0]
        prop = self.propFn(task)
        self.showFn(task, prop)


class GroupPrinter:

    def __init__(self, showFn):
        self.showFn = showFn

    def __call__(self, tasks):
        if not tasks:
            return
        for task in tasks:
            self.showFn(task)


class TasksGroups:

    def __init__(self):
        self.do_group = []
        self.do_print = None

    def group(self, propFn, showFn=None):
        self.do_group.append(GroupBuilder(propFn, showFn))
        return self

    def print(self, showFn):
        self.do_print = GroupPrinter(showFn)
        return self

    def digest(self, tasks):
        self.__dive(0, tasks)

    def __dive(self, depth, ilist):
        if len(self.do_group) <= depth:
            self.do_print(ilist)
            return

        group = self.do_group[depth]
        # Guard from non-generators
        ogroups = group.iterate(ilist)
        if not ogroups:
            return

        for olist in ogroups:
            group.display(olist)
            self.__dive(depth + 1, olist)


class TasksPrinter:

    types = {
        'key': lambda task: task.key,
        'type': lambda task: task.fields.issuetype.name,
        'status': lambda task: task.fields.status.name,
        'assignee': lambda task: task.fields.assignee.displayName,
        'reporter': lambda task: task.fields.reporter.displayName,
        'summary': lambda task: task.fields.summary,
        'sprint': lambda task: jwprops.taskSprints(task, True),
        'version': lambda task: jwprops.taskVersions(task, True),
    }

    sizes = {
        'key': '%-12s',
        'type': '%-20s',
        'status': '%-20s',
        'assignee': '%-30s',
        'reporter': '%-30s',
        'summary': '%-50s',
        'sprint': '%-30s',
        'version': '%-30s',
    }

    extra = {}

    def __init__(self):
        self.columns = []

    def __call__(self, task):
        for column in self.columns:
            if column in self.extra:
                sys.stdout.write(self.sizes[column] % self.extra[column](self.types[column](task), task))
            else:
                sys.stdout.write(self.sizes[column] % self.types[column](task))
        sys.stdout.write('\n')

    def mapping(self, prop, propFn, propFmt):
        if propFn:
            self.extra[prop] = propFn
        if propFmt:
            self.sizes[prop] = propFmt

    def declare(self, prop, propFn, propFmt):
        self.types[prop] = propFn
        self.types[prop] = propFmt

    def default(self):
        self.columns = ['key', 'type', 'status', 'assignee', 'summary']
        return self

    def include(self, *args):
        for arg in args:
            if arg not in self.types:
                continue

            if arg in self.columns:
                continue

            self.columns.append(arg)

        return self

    def exclude(self, *args):
        for arg in args:
            if arg not in self.columns:
                return

            self.columns.remove(arg)

        return self


class TasksStream:

    def __init__(self):
        self.columns = []

    def __call__(self, task):
        sys.stdout.write('%s ' % task.key)


class TasksInline:

    def __init__(self):
        pass

    def __call__(self, task, prop):
        sys.stdout.write('\n%s: ' % prop)


def debug(task):
    print("%-20s %s" % ("id", task.id,))
    print("%-20s %s" % ("key", task.key,))
    for f in dir(task.fields):
        if f.startswith('_'):
            continue
        print("%-20s %s" % (f, getattr(task.fields, f),))

    print("----- ChangeLog -----")
    for record in task.changelog.histories:
        print(record.author, record.created, record.id, "::")
        for item in record.items:
            print("%-15s %s -> %s" % (item.field,
                  item.fromString if item.field != "Link" else getattr(item, "from"),
                  item.toString if item.field != "Link" else item.to))
        print('---')


if __name__ == '__main__':
    def order(data):
        gr = {}
        for i in data:
            if i["x"] not in gr:
                gr[i["x"]] = []
            gr[i["x"]].append(i)

        for z in gr.values():
            yield z

    td = TasksGroup()
    td.add(order, lambda x: print("group", x[1]["x"])).add(print).digest([{"x" : "a", "y" : 123}, {"x" : "b", "y" : 2}, {"x" : "b", "y" : 3}, {"x" : "a", "y" : 11}])

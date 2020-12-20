
import argparse


class TaskFilter(argparse.Action):
    def __init__(self, option_strings, dest, *args, **kwargs):
        super(TaskFilter, self).__init__(option_strings, "taskFilter", nargs=0, default=[], **kwargs)
    def __call__(self, parser, namespace, *args):
        filters = getattr(namespace, "taskFilter")
        combine = getattr(namespace, "taskOr")
        if len(filters) > 0 and combine:
            setattr(namespace, "taskOr", False)
            filters[len(filters) - 1].append(self.const)
        else:
            filters.append([self.const])
        setattr(namespace, "taskFilter", filters)


class TaskOr(argparse.Action):
    def __init__(self, option_strings, dest, *args, **kwargs):
        super(TaskOr, self).__init__(option_strings, "taskOr", nargs=0, **kwargs)
    def __call__(self, parser, namespace, *args):
        setattr(namespace, "taskOr", True)


def parse():
    parser = argparse.ArgumentParser(description='JIRA issues filter')

    parser.add_argument('project', type=str, nargs='?',
                        help='configured JIRA project')

    parser.add_argument('--verbose', const=True,
                        action='store_const', dest='showVerbose',
                        help='verbose print')
    parser.add_argument('--inspect', nargs='?', type=str, const=True,
                        action='store', dest='showInspect',
                        help='inspect data')

    group_detail = parser.add_mutually_exclusive_group(required=False)
    group_detail.add_argument('--show-brief',
                              action='store_true', dest='showBrief',
                              help='show tasks brief info')
    group_detail.add_argument('--show-summary',
                              action='store_true', dest='showSummary',
                              help='show tasks summary')

    group = parser.add_argument_group('Listing target selection')
    group_target = group.add_mutually_exclusive_group(required=False)
    group_target.add_argument('--versions',
                              action='store_true', dest='showVersions',
                              help='show versions list')
    group_target.add_argument('--sprints',
                              action='store_true', dest='showSprints',
                              help='show sprints list')
    group_target.add_argument('--tasks',
                              action='store_true', dest='showTasks',
                              help='show tasks list')

    group = parser.add_argument_group('Tasks lookup method selection', 'Effective only with --tasks option')
    group_lookup = group.add_mutually_exclusive_group(required=False)
    group_lookup.add_argument('--for-version', metavar='VERSION',
                              action='store', dest='lookupVersion',
                              help='for specified version')
    group_lookup.add_argument('--for-sprint', metavar='SPRINT',
                              action='store', dest='lookupSprint',
                              help='for specified sprint')
    group_lookup.add_argument('--for-period',
                              action='store_true', dest='lookupPeriod',
                              help='for specified period')
    group_lookup.add_argument('--limit', nargs=1, type=int, default=10,
                              action='store', dest='lookupLimit',
                              help='limit number of results')
    group_lookup.add_argument('--list', nargs='+',
                              action='store', dest='lookupList',
                              help='list specified entries')

    group_period = parser.add_argument_group('Tasks search period selection', 'Effective only with --for-period option')
    group_period.add_argument('--by-version', metavar='VERSION',
                              action='store', dest='findVersion',
                              help='for specified version')
    group_period.add_argument('--by-sprint', metavar='SPRINT',
                              action='store', dest='findSprint',
                              help='for specified sprint')
    group_period.add_argument('--this-sprint', const=0,
                              action='store_const', dest='relSprint',
                              help='for current sprint')
    group_period.add_argument('--last-sprint', const=-1,
                              action='store_const', dest='relSprint',
                              help='for previous sprint')
    group_period.add_argument('--this-week', const='1w',
                              action='store_const', dest='relDate',
                              help='for current week')
    group_period.add_argument('--last-week', const='-1w',
                              action='store_const', dest='relDate',
                              help='for previous week')

    group = parser.add_argument_group('Tasks state selection', 'Effective only with --for-period option')
    group_state = group.add_mutually_exclusive_group(required=False)
    group_state.add_argument('--updated', const='updated', default='updated',
                             action='store_const', dest='findState',
                             help='select updated tasks')
    group_state.add_argument('--resolved', const='resolved',
                             action='store_const', dest='findState',
                             help='select resolved tasks')
    group_state.add_argument('--created', const='created',
                             action='store_const', dest='findState',
                             help='select created tasks')

    """
    Filters tasks by state:
        - Incomplete -- Tasks that are not yet done.
        - Complete -- Tasks that are fully done; review and testing included!
        - Working -- Tasks currenly work in progress.
        - Pending -- Tasks that were not started yet.
    """
    group_filtering = parser.add_argument_group('Tasks filtering options', 'Effective only with --tasks option')
    group_filtering.add_argument('--state-incomplete', const=('state', 'Incomplete'),
                                 action=TaskFilter, help='filter incomplete tasks')
    group_filtering.add_argument('--state-complete', const=('state', 'Complete',),
                                 action=TaskFilter, help='filter complete tasks')
    group_filtering.add_argument('--state-working', const=('state', 'Working',),
                                 action=TaskFilter, help='filter work-in-progress tasks')
    group_filtering.add_argument('--state-pending', const=('state', 'Pending',),
                                 action=TaskFilter, help='filter pending-work tasks')
    group_filtering.add_argument('--type-bugs', const=('type', 'Bug',),
                                 action=TaskFilter, help='filter bugs')
    group_filtering.add_argument('--type-support', const=('type', 'Support Task',),
                                 action=TaskFilter, help='filter support tasks')
    group_filtering.add_argument('--type-tstory', const=('type', 'Technical Story',),
                                 action=TaskFilter, help='filter technical stories')
    group_filtering.add_argument('--type-ustory', const=('type', 'User Story',),
                                 action=TaskFilter, help='filter user stories')
    group_filtering.add_argument('--type-epics', const=('type', 'Epic',),
                                 action=TaskFilter, help='filter epics')
    group_filtering.add_argument('--or', action=TaskOr,
                                  help='logical OR filters')

    group_changed = parser.add_argument_group('Tasks changes options', 'Effective only with --tasks option')
    group_changed.add_argument('--change-status', dest='taskChangeStatus', const=True,
                               action='store_const', help='filter changed task status')
    group_changed.add_argument('--change-resolution', dest='taskChangeResolution', const=True,
                               action='store_const', help='filter changed task resolution')

    group_grouping = parser.add_argument_group('Tasks grouping options', 'Effective only with --tasks option')
    group_grouping.add_argument('--group-type', dest='taskGroup', const='type',
                                action='append_const', help='group tasks by "type"')
    group_grouping.add_argument('--group-state', dest='taskGroup', const='state',
                                action='append_const', help='group tasks by "state"')
    group_grouping.add_argument('--group-assignee', dest='taskGroup', const='assignee',
                                action='append_const', help='group tasks by "assignee"')
    group_grouping.add_argument('--group-reporter', dest='taskGroup', const='reporter',
                                action='append_const', help='group tasks by "reporter"')
    group_grouping.add_argument('--group-sprint', dest='taskGroup', const='sprint',
                                action='append_const', help='group tasks by "sprint"')
    group_grouping.add_argument('--group-version', dest='taskGroup', const='version',
                                 action='append_const', help='group tasks by "version"')

    group_printing = parser.add_argument_group('Tasks printing options', 'Effective only with --tasks option')
    group_printing.add_argument('--print-key', dest='taskPrint', const='key',
                                action='append_const', help='print task "key"')
    group_printing.add_argument('--print-type', dest='taskPrint', const='type',
                                action='append_const', help='print task "type"')
    group_printing.add_argument('--print-status', dest='taskPrint', const='status',
                                action='append_const', help='print task "status"')
    group_printing.add_argument('--print-assignee', dest='taskPrint', const='assignee',
                                action='append_const', help='print task "assignee"')
    group_printing.add_argument('--print-reporter', dest='taskPrint', const='reporter',
                                action='append_const', help='print task "reporter"')
    group_printing.add_argument('--print-summary', dest='taskPrint', const='summary',
                                 action='append_const', help='print task "summary"')
    group_printing.add_argument('--print-sprint', dest='taskPrint', const='sprint',
                                action='append_const', help='print task "sprint"')
    group_printing.add_argument('--print-version', dest='taskPrint', const='version',
                                 action='append_const', help='print task "version"')

    params = parser.parse_args()
    return params


if __name__ == '__main__':
    params = parse()
    print(params)

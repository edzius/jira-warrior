
import argparse


def jw_options():
    parser = argparse.ArgumentParser(description='JIRA issues filter')

    parser.add_argument('project', type=str, nargs='?',
                        help='configured JIRA project')

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

    group = parser.add_argument_group('Tasks search period selection', 'Effective only with --for-period option')
    group_period = group.add_mutually_exclusive_group(required=False)
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

    group = parser.add_argument_group('Tasks filtering by state', 'Effective only with --tasks option')
    group_state = group.add_mutually_exclusive_group(required=False)
    group_state.add_argument('--resolved',
                             action='store_true', dest='onlyResolved',
                             help='show only resolved tasks list')
    group_state.add_argument('--state-open', const='Open',
                             action='store_const', dest='stateFilter',
                             help='filter "open" state tasks')
    group_state.add_argument('--state-closed', const='Closed',
                             action='store_const', dest='stateFilter',
                             help='filter "closed" state tasks')
    group_state.add_argument('--state-done', const='Done',
                             action='store_const', dest='stateFilter',
                             help='filter "done" state tasks')
    group_state.add_argument('--state-working', const='Working',
                             action='store_const', dest='stateFilter',
                             help='filter "working" state tasks')
    group_state.add_argument('--state-pending', const='Pending',
                             action='store_const', dest='stateFilter',
                             help='filter "pending" state tasks')

    group = parser.add_argument_group('Tasks filtering by type', 'Effective only with --tasks option')
    group_type = group.add_mutually_exclusive_group(required=False)
    group_type.add_argument('--show-bugs', const='Bug',
                            action='store_const', dest='typeFilter',
                            help='show only bugs')
    group_type.add_argument('--show-support', const='Support Task',
                            action='store_const', dest='typeFilter',
                            help='show only support tasks')
    group_type.add_argument('--show-tstory', const='Tehcnical Story',
                            action='store_const', dest='typeFilter',
                            help='show only technical stories')
    group_type.add_argument('--show-ustory', const='User Story',
                            action='store_const', dest='typeFilter',
                            help='show only user stories')
    group_type.add_argument('--show-epics', const='Epic',
                            action='store_const', dest='typeFilter',
                            help='show only epics')

    group = parser.add_argument_group('Print coloring control')
    group_mark = group.add_mutually_exclusive_group(required=False)
    group_mark.add_argument('--mark-state', const='State',
                            action='store_const', dest='makrMode',
                            help='mark by task state')
    group_mark.add_argument('--mark-type', const='Type',
                            action='store_const', dest='markMode',
                            help='mark by task type')
    group_mark.add_argument('--mark-range', const='Range',
                            action='store_const', dest='markMode',
                            help='mark by resolution date')
    group_mark.add_argument('--mark-sprint', const='Sprint',
                            action='store_const', dest='markMode',
                            help='mark by assigned sprint')
    group_mark.add_argument('--mark-version', const='Version',
                            action='store_const', dest='markMode',
                            help='mark by assigned version')

    group = parser.add_argument_group('Print detail control')
    group_detail = group.add_mutually_exclusive_group(required=False)
    group_detail.add_argument('--show-brief',
                              action='store_true', dest='showBrief',
                              help='show brief info')
    group_detail.add_argument('--show-detail',
                              action='store_true', dest='showDetail',
                              help='show detailed info')

    params = parser.parse_args()
    return params


if __name__ == '__main__':
    params = jw_options()
    print(params)

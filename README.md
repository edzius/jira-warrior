# JIRA warrior

## Install

1. Install Python 3.x with default core packages.
2. Install JIRA API library 2.0 (`pip install jira`) from:
   https://pypi.org/project/jira/

## Setup

Create a configuration file: $HOME/.rw.conf or /etc/rw.conf
You may use configuration file template stored in `default.conf`.

Each JIRA target is separate JIRA project definition. Which
can be specified explicitly when running JW tool.

Example configuration defining two JIRA projects:

```
[target]
project=PROJECT
board=PROJECT board
server=http://jira.server:8080/
username=user_login
password=user_pass

[secret-target]
project=MANGERAL
board=MY board
server=http://other.server/
username=user_login
password=user_pass
```

For ones using atlassian cloud JIRA service JIRA API key
needs to be generated and used in `password` field.

## Usage

```
$ jw.py

  Will show JIRA server projects and boards information
```

```
$ jw.py --versions

  Will show previous, current and future versions
```

```
$ jw.py --sprints

  Will show previous, current and future sprints
```

```
$ jw.py --tasks

  Will show recent tasks
```

```
$ jw.py other-project --tasks --for-period --last-week --resolved

  Will show last week's resolved JIRA tasks for
  'other-project' defined in configuration file.
```

### Options

```
usage: jw.py [-h] (--versions | --sprints | --tasks) [--for-version VERSION | --for-sprint SPRINT | --for-period]
             [--by-version VERSION | --by-sprint SPRINT | --this-sprint | --last-sprint | --this-week | --last-week]
             [--resolved | --state-open | --state-closed | --state-done | --state-working | --state-pending]
             [--show-bugs | --show-support | --show-tstory | --show-ustory | --show-epics]
             [--mark-state | --mark-type | --mark-range | --mark-sprint | --mark-version] [--show-brief | --show-detail]
             [project]

JIRA issues filter

positional arguments:
  project               configured JIRA project

optional arguments:
  -h, --help            show this help message and exit

Listing target selection:
  --versions            show versions list
  --sprints             show sprints list
  --tasks               show tasks list

Tasks lookup method selection:
  Effective only with --tasks option

  --for-version VERSION
                        for specified version
  --for-sprint SPRINT   for specified sprint
  --for-period          for specified period

Tasks search period selection:
  Effective only with --for-period option

  --by-version VERSION  for specified version
  --by-sprint SPRINT    for specified sprint
  --this-sprint         for current sprint
  --last-sprint         for previous sprint
  --this-week           for current week
  --last-week           for previous week

Tasks filtering by state:
  Effective only with --tasks option

  --resolved            show only resolved tasks list
  --state-open          filter "open" state tasks
  --state-closed        filter "closed" state tasks
  --state-done          filter "done" state tasks
  --state-working       filter "working" state tasks
  --state-pending       filter "pending" state tasks

Tasks filtering by type:
  Effective only with --tasks option

  --show-bugs           show only bugs
  --show-support        show only support tasks
  --show-tstory         show only technical stories
  --show-ustory         show only user stories
  --show-epics          show only epics

Print coloring control:
  --mark-state          mark by task state
  --mark-type           mark by task type
  --mark-range          mark by resolution date
  --mark-sprint         mark by assigned sprint
  --mark-version        mark by assigned version

Print detail control:
  --show-brief          show brief info
  --show-detail         show detailed info
```

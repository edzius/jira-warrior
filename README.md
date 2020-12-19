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

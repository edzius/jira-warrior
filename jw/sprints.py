
from datetime import datetime
from termcolor import colored
from . import fetch as jwfetch


def run():
    sprints = jwfetch.jw_sprints()

    dateNow = datetime.now().replace(tzinfo=None)
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


def debug(sprint_name):
    sprint = None
    sprints = jwfetch.jw_sprints()
    for item in sprints:
        if sprint_name == True or item.name.find(sprint_name) != -1:
            sprint = item
            break

    for s in dir(sprint):
        if s.startswith('_'):
            continue
        print("%-20s %s" % (s, getattr(sprint, s),))

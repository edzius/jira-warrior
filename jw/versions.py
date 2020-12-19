
from datetime import datetime
from termcolor import colored
from . import fetch as jwfetch


def run():
    versions = jwfetch.jw_versions()

    dateNow = datetime.now().replace(tzinfo=None)
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


def debug(version_name):
    version = None
    versions = jwfetch.jw_versions()
    for item in versions:
        if version_name == True or item.name.find(version_name) != -1:
            version = item
            break

    for v in dir(version):
        if v.startswith('_'):
            continue
        print("%-20s %s" % (v, getattr(version, v),))

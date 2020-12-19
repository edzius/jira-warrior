
import re

def taskVersions(task, default=None):
    versions = []
    for version in task.fields.fixVersions:
        versions.append(version.name)

    if not default:
        return versions
    if default == True:
        return versions[0] if len(versions) > 0 else "None"
    else:
        return default


def taskSprints(task, default=None):
    sprints_def = None
    for key, val in task.fields.__dict__.items():
        if type(val) != list or len(val) == 0 or type(val[0]) != str:
            continue

        if not re.search("com.atlassian.greenhopper.service.sprint.Sprint", val[0]):
            continue

        sprints_def = val
        break

    if not sprints_def:
        sprints_def = []

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

    if not default:
        return sprints
    if default == True:
        return sprints[0] if len(sprints) > 0 else "None"
    else:
        return default


from . import fetch as jwfetch


def run():
    print("Projects:\n")
    projects = jwfetch.jw_projects()
    for project in projects:
        print("* %s - %s" % (project.key, project.name,))
        versions = jwfetch.jw_versions(project)
        if len(versions) == 0:
            continue
        print("\n  - %s\n" % "\n  - ".join([version.name for version in jwfetch.jw_versions(project)]))

    print()
    print("Boards:\n")
    boards = jwfetch.jw_boards()
    for board in boards:
        print("* %s" % (board.name,))
        sprints = jwfetch.jw_sprints(board)
        if len(sprints) == 0:
            continue
        print("\n  - %s\n" % "\n  - ".join([sprint.name for sprint in jwfetch.jw_sprints(board)]))


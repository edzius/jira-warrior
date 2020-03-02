
import os
from configparser import ConfigParser


class Section:
    def __init__(self, section):
        self.section = section

    def __getattr__(self, name):
        k1 = str.replace(name, '_', '-')
        k2 = str.replace(name, '-', '_')

        if name in self.section:
            return self.section[name]
        elif k1 in self.section:
            return self.section[k1]
        elif k2 in self.section:
            return self.section[k2]
        else:
            return None

    def __setattr__(self, name, value):
        if name == 'section':
            object.__setattr__(self, name, value)
        else:
            self.section[name] = value


def jw_config(project=None):
    config = ConfigParser()

    files = []
    files.append("jw.conf")
    files.append("/etc/jw.conf")
    if os.getenv("HOME"):
        files.append(os.getenv("HOME") + "/.jw.conf")

    config.read(files)

    section = {}
    if project:
        section.update(config.items(project))
    else:
        section.update(config.items(config.sections()[0]))

    return Section(section)


if __name__ == '__main__':
    config = jw_config()
    print(config)
    config = jw_config("8dev")
    print(config)

    s = Section({ "aa": "1", "b-b": "2", "c_c": "3" })
    print(s.aa)
    print(s.b_b)
    print(s.c_c)
    print(s.d_d)

    s.k = 'a'
    s.l_l = 'b'
    print(s.k)
    print(s.l_l)

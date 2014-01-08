#!/usr/bin/env python3

import sys, os, subprocess, random

CONFIG_DIR = os.path.expanduser(os.path.join("~", ".wallpyper"))
CONFIG_FILE = os.path.join(CONFIG_DIR, ".config")
CURRENT_COLLECTION_FILE = os.path.join(CONFIG_DIR, ".current")
SET_BACKGROUND_COMMAND = ["feh", "--bg-fill"]
NEXT = ("next", "forward", "after", ">")
PREVIOUS = ("prev", "previous", "before", "back", "<")

def usage():
    print("""Manages wallpapers in collections and switches them using feh.

    wallpyper.py use COLLECTION|next|previous
    wallpyper.py current
    wallpyper.py next
    wallpyper.py previous
    wallpyper.py add COLLECTION PATH [PATH [PATH...]]
    wallpyper.py create COLLECTION
    wallpyper.py list COLLECTION|current|collections
""")
    sys.exit(1)


class Collection(object):
    def __init__(self, name):
        self.current = 0
        self.name = name
        self.paths = []
        self.load()

    @property
    def path(self):
        return os.path.join(CONFIG_DIR, self.name)

    @property
    def path_current(self):
        return os.path.join(CONFIG_DIR, ".current." + self.name)

    def load(self):
        if not os.path.exists(self.path): return
        with open(self.path) as f:
            self.load_list([os.path.join(self.path, line) for line in f.readlines()])

        if not os.path.exists(self.path_current): return
        with open(self.path_current) as f:
            self.current=int(f.readlines()[0].strip())

    def load_list(self, paths):
        for path in paths:
            if os.path.isdir(path):
                self.load_list([os.path.join(path, f) for f in os.listdir(path)])
            elif not path.strip() in self.paths:
                self.paths.append(path.strip())

    def action_list(self):
        for path in self.paths:
            print(path)

    def action_next(self):
        self.current = (self.current + 1) % len(self.paths)
        self.update()
        self.save()

    def action_previous(self):
        self.current = (self.current - 1) % len(self.paths)
        self.update()
        self.save()

    def action_random(self):
        self.current = random.randint(0, len(self.paths) - 1)
        self.update()
        self.save()

    def action_add(self, paths):
        self.load_list([os.path.abspath(path) for path in paths])
        self.save()

    def action_current(self):
        print(self.name, self.paths[self.current])

    def update(self):
        subprocess.Popen(SET_BACKGROUND_COMMAND + [self.paths[self.current]])

    def save(self):
        with open(self.path, "w") as f:
            for path in self.paths:
                f.write(path + "\n")
            f.close()
        with open(self.path_current, "w") as f:
            f.write(str(self.current) + "\n")
            f.close()

def get_current_collection():
    with open(CURRENT_COLLECTION_FILE) as f:
        return Collection(f.readlines()[0].strip())

def set_current_collection(name):
    with open(CURRENT_COLLECTION_FILE, "w") as f:
        f.write(name + "\n")
        f.close()

def get_collections():
    return [name for name in os.listdir(CONFIG_DIR) if name[0] != "."]

def get_collection(name, create=False):
    if not name in get_collections():
        if create:
            c = Collection(name)
            c.save()
            return c
        else:
            print("Collection not found: " + name)
            sys.exit(1)
    else:
        return Collection(name)

if __name__ == "__main__":
    if not len(sys.argv) > 1: usage()

    cmd = sys.argv[1]
    if cmd in NEXT:
        get_current_collection().action_next()
    elif cmd in PREVIOUS:
        get_current_collection().action_previous()
    elif cmd in ("random"):
        get_current_collection().action_random()
    elif cmd in ("add"):
        if len(sys.argv) < 4: usage()
        else: get_collection(sys.argv[2]).action_add(sys.argv[3:])
    elif cmd in ("create"):
        if len(sys.argv) != 3: usage()
        else: get_collection(sys.argv[2], True).save()
    elif cmd in ("list"):
        if len(sys.argv) != 3: usage()
        c = sys.argv[2]
        if c == "current":
            get_current_collection().action_list()
        elif c == "collections":
            print("\n".join(get_collections()))
        else: 
            get_collection(c).action_list()
    elif cmd in ("current"):
        get_current_collection().action_current()
    elif cmd in ("use"):
        if len(sys.argv) != 3: usage()
        c = sys.argv[2]
        cols = get_collections()
        if c in NEXT:
            name = get_current_collection().name
            set_current_collection(cols[(cols.index(name) + 1) % len(cols)])
            get_current_collection().update()
        elif c in PREVIOUS:
            name = get_current_collection().name
            set_current_collection(cols[(cols.index(name) - 1) % len(cols)])
            get_current_collection().update()
        else:
            set_current_collection(c)

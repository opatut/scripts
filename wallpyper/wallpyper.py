#!/usr/bin/env python3

import sys, os, subprocess, random

CONFIG_DIR = os.path.expanduser(os.path.join("~", ".wallpyper"))
CONFIG_FILE = os.path.join(CONFIG_DIR, ".config")
CURRENT_COLLECTION_FILE = os.path.join(CONFIG_DIR, ".current_collection")
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
    wallpyper.py refresh [COLLECTION]
""")
    sys.exit(1)


class Collection(object):
    def __init__(self, name):
        self.current_image = 0
        self.name = name
        self.paths = []
        self.images = []
        self.load()

    @property
    def paths_path(self):
        return os.path.join(CONFIG_DIR, self.name)

    @property
    def images_path(self):
        return os.path.join(CONFIG_DIR, "." + self.name + ".image_cache")

    @property
    def current_image_path(self):
        return os.path.join(CONFIG_DIR, "." + self.name + ".current_image")

    def load(self):
        if os.path.exists(self.images_path):
            with open(self.images_path) as f:
                self.images = [os.path.join(CONFIG_DIR, line.strip()) for line in f.readlines()]
        if os.path.exists(self.paths_path):
            with open(self.paths_path) as f:
                self.paths = [os.path.join(CONFIG_DIR, line.strip()) for line in f.readlines()]
                if not self.images: self.load_images(self.paths)
        else: return

        if not os.path.exists(self.current_image_path): return
        with open(self.current_image_path) as f:
            self.current_image=int(f.readlines()[0].strip())

    def load_images(self, paths):
        if type(paths) is not list:
            print("error, got string")
            return
        for path in paths:
            if os.path.isdir(path):
                self.load_images([os.path.join(path, f) for f in os.listdir(path)])
            elif not path.strip() in self.images:
                self.images.append(path.strip())

    def refresh(self):
        current_image_name = self.images[self.current_image]

        self.images = []
        self.load_images(self.paths)

        self.current_image = self.images.index(current_image_name)
        self.save()

    def action_list(self):
        for path in self.paths:
            print(path)

    def action_next(self):
        self.current_image = (self.current_image + 1) % len(self.images)
        self.update()
        self.save()

    def action_previous(self):
        self.current_image = (self.current_image - 1) % len(self.images)
        self.update()
        self.save()

    def action_random(self):
        self.current_image = random.randint(0, len(self.images) - 1)
        self.update()
        self.save()

    def action_add(self, paths):
        for path in paths:
            self.paths.append(path.strip())
        self.load_images([os.path.abspath(path) for path in paths])
        self.save()

    def action_current(self):
        print(self.name, self.images[self.current_image])

    def update(self):
        subprocess.Popen(SET_BACKGROUND_COMMAND + [self.images[self.current_image]])

    def save(self):
        with open(self.images_path, "w") as f:
            for image in self.images:
                f.write(image + "\n")
            f.close()
        with open(self.paths_path, "w") as f:
            for path in self.paths:
                f.write(path + "\n")
            f.close()
        with open(self.current_image_path, "w") as f:
            f.write(str(self.current_image) + "\n")
            f.close()

def get_current_collection():
    if os.path.exists(CURRENT_COLLECTION_FILE):
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

    if (cmd in NEXT + PREVIOUS + ("random", "current")) and not get_current_collection():
        print("Error: No current collection set.")
    elif cmd in NEXT:
        get_current_collection().action_next()
    elif cmd in PREVIOUS:
        get_current_collection().action_previous()
    elif cmd in ("random"):
        get_current_collection().action_random()
    elif cmd in ("add"):
        if len(sys.argv) < 4: usage()
        else: 
            get_collection(sys.argv[2]).action_add(sys.argv[3:])
    elif cmd in ("create"):
        if len(sys.argv) != 3: usage()
        else: get_collection(sys.argv[2], True).save()
    elif cmd in ("list"):
        if len(sys.argv) != 3: usage()
        c = sys.argv[2]
        if c == "current":
            if get_current_collection(): get_current_collection().action_list()
            else: print("No current collection set.")
        elif c == "collections":
            print("\n".join(get_collections()))
        else: 
            get_collection(c).action_list()
    elif cmd in ("current"):
        get_current_collection().action_current()
    elif cmd in ("refresh"):
        if len(sys.argv) == 2:
            for collection in get_collections():
                get_collection(collection).refresh()
        elif len(sys.argv) == 3:
            get_collection(sys.argv[2]).refresh()
        else: usage()
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
    else: usage()

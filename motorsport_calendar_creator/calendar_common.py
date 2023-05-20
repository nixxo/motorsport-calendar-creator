import os
from ics import Calendar, Event


class CalendarCommon:
    EXT = ".ics"
    CALS = {}
    CALS_NEW = {}
    OUT = None
    DEBUG = False

    def __init__(self, debug=DEBUG):
        self.DEBUG = debug

    @staticmethod
    def str_enc(string):
        final = []
        for s in string.splitlines():
            final.append(f"{s}\n")
        return final

    @staticmethod
    def enc_str(s):
        try:
            s = s.encode("utf-8").decode("cp1252")
        except Exception:
            s = s
        return s

    @staticmethod
    def check_url(url, host):
        if url.startswith("http"):
            return url
        if host.endswith("/"):
            host = host.rstrip("/")
        if url.startswith("/"):
            url = url.lstrip("/")
        return f"{host}/{url}"

    @staticmethod
    def event_compare(e, evt):
        if (
            e.summary == evt.summary
            and e.description == evt.description
            and e.location == e.location
            and e.begin == evt.begin
            and e.end == evt.end
            and e.url == evt.url
        ):
            return 1  # identical
        if e.summary == evt.summary and (
            e.location == evt.location or e.url == evt.url
        ):
            return 0  # similar
        return -1  # different

    def create_calendars(self, output_folder, names, appendix=None):
        self.OUT = os.path.realpath(output_folder)

        if appendix:
            appendix = f"_{appendix}"

        for name in names:
            try:
                fn = os.path.realpath(
                    os.path.join(self.OUT, f"{name}{appendix}{self.EXT}")
                )
                f = open(fn, "r")
                self.CALS[name] = Calendar(f.read())
                f.close()
            except Exception:
                self.CALS[name] = Calendar()
            self.CALS_NEW[name] = Calendar()

    def write_calendars(self, output_folder, appendix=None):
        if not os.path.exists(self.OUT):
            os.mkdir(self.OUT)

        if appendix:
            appendix = "_" + appendix
        for cal in self.CALS_NEW:
            fn = os.path.realpath(os.path.join(self.OUT, f"{cal}{appendix}{self.EXT}"))
            with open(fn, "w") as my_file:
                my_file.write(self.CALS_NEW[cal].serialize())

    def create_event(self, summary, description, location, url, begin, end):
        e = Event()
        e.summary = summary
        e.description = description
        e.location = location
        e.url = url
        e.begin = begin
        if end != begin:
            e.end = end
        return e

    def add_if_new(self, clas, evt):
        updated, found = False, False
        i = 0
        for e in self.CALS[clas].events:
            evt_cmp = self.event_compare(e, evt)
            # identical
            if evt_cmp == 1:
                if self.DEBUG:
                    print("SAME EVENT FOUND")
                found = True
                self.CALS_NEW[clas].events.append(e)
                break
            # similar
            if evt_cmp == 0:
                e.description = evt.description
                e.url = evt.url
                # clear end time to avoid errors
                e.end = None
                e.begin = evt.begin
                if evt.begin != evt.end:
                    e.end = evt.end
                updated, found = True, True
                self.CALS_NEW[clas].events.append(e)
                if self.DEBUG:
                    print("SAME EVENT UPDATED")
                break
            i = i + 1
        if not found:
            updated = True
            if self.DEBUG:
                print("NEW EVENT")
            self.CALS[clas].events.append(evt)
            self.CALS_NEW[clas].events.append(evt)

        return updated

    def find_event(self, clas, evt):
        found = False
        for e in self.CALS[clas].events:
            found = True if self.event_compare(e, evt) in [0, 1] else found or False
        return found

    def same_size(self, clas):
        return len(self.CALS[clas].events) == len(self.CALS_NEW[clas].events)

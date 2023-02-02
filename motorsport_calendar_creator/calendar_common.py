import os
from ics import Calendar, Event


class CalendarCommon:
    EXT = ".ics"
    CALS = {}
    OUT = None

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

    def write_calendars(self, output_folder, appendix=None):
        if not os.path.exists(self.OUT):
            os.mkdir(self.OUT)

        if appendix:
            appendix = "_" + appendix
        for cal in self.CALS:
            fn = os.path.realpath(os.path.join(self.OUT, f"{cal}{appendix}{self.EXT}"))
            with open(fn, "w") as my_file:
                my_file.write(self.CALS[cal].serialize())

    def create_event(self, summary, description, location, url, begin, end):
        e = Event()
        e.summary = summary
        e.description = description
        e.location = location
        e.url = url
        e.begin = begin
        e.end = end
        return e

    def add_if_new(self, clas, evt):
        found = False
        i = 0
        for e in self.CALS[clas].events:
            if (
                e.summary == evt.summary
                and e.description == evt.description
                and e.location == e.location
                and e.begin == evt.begin
                and e.end == evt.end
                and e.url == evt.url
            ):
                found = True
                break
            if e.summary == evt.summary and e.location == evt.location:
                self.CALS[clas].events[i].description = evt.description
                self.CALS[clas].events[i].url = evt.url
                # clear end time to avoid errors
                self.CALS[clas].events[i].end = None
                self.CALS[clas].events[i].begin = evt.begin
                if evt.begin != evt.end:
                    self.CALS[clas].events[i].end = evt.end
                found = True
                print("UPDATED")
                break
            i = i + 1
        if not found:
            print("NEW EVENT")
            self.CALS[clas].events.append(evt)

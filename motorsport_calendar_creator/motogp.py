import datetime
import re
import requests
import sys
from bs4 import BeautifulSoup

from .calendar_common import CalendarCommon


class MotoGP:
    cc = None
    debug = False
    host = "https://www.motogp.com"
    calendar_url = f"{host}/en/calendar"
    calendar_url_json = "https://api.pulselive.motogp.com/motogp/v1/events?seasonYear=2025"
    event_base_url = "/en/calendar/2025/event/"
    event_api = "https://api.motogp.pulselive.com/motogp/v1/events/"
    calendar_filter = [
        {"appendix": "qualy-and-races", "filter": ["Q1", "Q2", "SPR", "RAC", "RAC1", "RAC2"]},
        {"appendix": "sprint-and-race", "filter": ["SPR", "RAC", "RAC1", "RAC2"]},
    ]
    sess_exclude = ["VIDEO", "SHOW", "PRESS"]
    classes = ["Moto3", "Moto2", "MotoGP", "MotoE"]
    appendix = "2025_calendar"
    updates = False

    def __init__(self, output_dir, debug=False):
        names = []
        self.debug = debug
        self.cc = CalendarCommon(debug=debug)
        for c in self.classes:
            names.append(c)
            for f in self.calendar_filter:
                names.append(f"{c}_{f['appendix']}")

        self.cc.create_calendars(output_dir, names, self.appendix)

    def get_events(self):
        e = requests.get(self.calendar_url_json)
        print(e.url)

        if e.status_code != 200:
            print("no connection")
            sys.exit()

        events = e.json()
        print(f"Found {len(events)} events in the calendar.")

        for event in events:
            if event.get("kind") != "GP":
                if self.debug:
                    print(f'Skipping {event.get("name")}')
                continue
            print(f"Loading {event.get('hashtag')}...")
            self.get_event_schedule(event)





        pass

    def get_events_links(self):
        events_links = []
        r = requests.get(self.calendar_url)
        print(r.url)

        if r.status_code != 200:
            print("no connection")
            sys.exit()

        # parse calendar webpage
        page = BeautifulSoup(r.text, "html.parser")
        events = page.find_all("a", class_="calendar-listing__event", limit=25)

        print(f"Found {len(events)} events in the calendar.")
        for link in events or []:
            if (
                link.find("div", class_="calendar-listing__status-type")
                .get_text()
                .strip()
                .lower()
                == "test"
            ):
                if self.debug:
                    print("skipping test")
                continue
            eid = re.search(
                r"(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})", link.attrs["href"]
            ).group(0)

            if self.debug:
                print(f"{self.event_api}{eid}")
            events_links.append(f"{self.event_api}{eid}")
        return events_links

    def get_event_schedule_from_link(self, link):
        e = requests.get(link)
        if e.status_code != 200:
            if not self.debug:
                print(link)
            print("no connection, skipping")
            return

        event = e.json()
        print(f"Loading #{event.get('url')}...")
        self.get_event_schedule(event)

    def get_event_schedule(self, event):
        # event name
        title = f'{event.get("kind")}{event.get("sequence")} - {event.get("name").strip()}'
        if self.debug:
            print(title)

        # circuit name / location
        if not event.get("circuit"):
            print("NO CIRCUIT INFO - ABORTING")
            return

        circuit = f"{event['circuit'].get('name')} - {event['circuit'].get('city')}"
        if self.debug:
            print(circuit)

        hashtag = event.get('hashtag')
        if self.debug:
            print(hashtag)

        # sessions
        sessions = event.get("broadcasts")
        if self.debug:
            print(f"Found {len(sessions)} sessions in the event.")
        
        flag = False

        for session in sessions:
            # Category Name
            clas = session["category"]["name"].strip()
            if clas not in self.classes:
                continue

            # Session Name
            sess_full = session.get("name").strip()
            sess = session.get("shortname").strip()

            if sess in self.sess_exclude:
                if self.debug:
                    print(f"{clas} {sess} {sess_full} skipped.")
                continue

            if self.debug:
                print(f"{clas} {sess} {sess_full}")

            # Session start/end
            sess_start = datetime.datetime.strptime(
                session.get("date_start"), "%Y-%m-%dT%H:%M:%S%z"
            )
            sess_end = datetime.datetime.strptime(
                session.get("date_end"), "%Y-%m-%dT%H:%M:%S%z"
            )
            e = self.cc.create_event(
                #f"[{clas}] {sess}",
                f"[{clas}] {sess} - {hashtag}",
                f"Event: {title}\nClass: {clas}\nSession: {sess_full}",
                circuit,
                self.cc.check_url(
                    f'{self.event_base_url}{event.get("url").lower().strip()}/{event.get("id").lower()}',
                    self.host
                ),
                sess_start,
                sess_end,
            )
            flag = self.cc.add_if_new(clas, e) or flag

            for f in self.calendar_filter:
                if sess in f["filter"]:
                    flag = self.cc.add_if_new(f"{clas}_{f['appendix']}", e) or flag

        self.updates = flag or self.updates
        print(f'{"Event updated" if flag else "No updates found"}\n')

    def write_calendars(self, output_dir, force_write=False):
        for clas in self.classes:
            self.updates = not self.cc.same_size(clas) or self.updates
        print(f'\n{"Calendar UPDATED" if self.updates else "No updates to the calendar"}')

        if self.updates or force_write:
            self.cc.write_calendars(output_dir, self.appendix)

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
    event_api = "https://api.motogp.pulselive.com/motogp/v1/events/"
    calendar_filter = [
        {"appendix": "filtered", "filter": ["Q1", "Q2", "SPR", "RAC", "RAC1", "RAC2"]},
        {"appendix": "sprint-and-race", "filter": ["SPR", "RAC", "RAC1", "RAC2"]},
    ]
    sess_exclude = ["VIDEO", "SHOW", "PRESS"]
    classes = ["Moto3", "Moto2", "MotoGP", "MotoE"]
    appendix = "2024_calendar"

    def __init__(self, output_dir, debug=False):
        names = []
        self.debug = debug
        cc = CalendarCommon(debug=debug)
        for c in self.classes:
            names.append(c)
            for f in self.calendar_filter:
                names.append(f"{c}_{f['appendix']}")

        cc.create_calendars(output_dir, names, self.appendix)

    def get_events_links(self):
        events_links = []
        r = requests.get(self.calendar_url)
        print(r.url)

        if r.status_code != 200:
            print("no connection")
            sys.exit()

        # parse calendar webpage
        page = BeautifulSoup(r.text, "html.parser")
        events = page.find_all("a", class_="calendar-listing__event")

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


def gp_main(output_dir, debug=False):
    cc = CalendarCommon(debug=debug)
    host = "https://www.motogp.com"

    calendar_url = "https://www.motogp.com/en/calendar"
    event_api = "https://api.motogp.pulselive.com/motogp/v1/events/"

    calendar_filter = [
        {"appendix": "qualy-and-races", "filter": ["Q1", "Q2", "SPR", "RAC", "RAC1", "RAC2"]},
        {"appendix": "sprint-and-race", "filter": ["SPR", "RAC", "RAC1", "RAC2"]},
    ]
    sess_exclude = ["VIDEO", "SHOW", "PRESS"]
    classes = ["Moto3", "Moto2", "MotoGP", "MotoE"]
    appendix = "2024_calendar"
    names = []
    for c in classes:
        names.append(c)
        for f in calendar_filter:
            names.append(f"{c}_{f['appendix']}")

    cc.create_calendars(output_dir, names, appendix)

    r = requests.get(calendar_url)
    print(r.url)

    if r.status_code != 200:
        print("no connection")
        sys.exit()

    # parse calendar webpage
    page = BeautifulSoup(r.text, "html.parser")
    events = page.find_all("a", class_="calendar-listing__event")

    updates = False

    print(f"Found {len(events)} events in the calendar.")
    for link in events or []:
        if (
            link.find("div", class_="calendar-listing__status-type")
            .get_text()
            .strip()
            .lower()
            == "test"
        ):
            if debug:
                print("skipping test")
            continue
        eid = re.search(r"(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})", link.attrs["href"]).group(
            0
        )

        if debug:
            print(f"{event_api}{eid}")

        e = requests.get(f"{event_api}{eid}")
        if e.status_code != 200:
            if not debug:
                print(f"{event_api}{eid}")
            print("no connection, skipping")
            continue

        event = e.json()
        print(f"Loading #{event.get('url')}...")
        # event name
        title = event.get("name").strip()
        if debug:
            print(title)

        # circuit name / location
        if not event.get("circuit"):
            print("NO CIRCUIT INFO - ABORTING")
            continue

        circuit = f"{event['circuit'].get('name')} - {event['circuit'].get('city')}"
        if debug:
            print(circuit)

        # sessions
        sessions = event.get("broadcasts")
        if debug:
            print(f"Found {len(sessions)} sessions in the event.")

        flag = False

        for session in sessions:
            # Category Name
            clas = session["category"]["name"].strip()
            if clas not in classes:
                continue
            # Session Name
            sess_full = session.get("name").strip()
            sess = session.get("shortname").strip()

            if sess in sess_exclude:
                # print(f"{clas} {sess} {sess_full} skipped.")
                continue
            # print(f"{clas} {sess} {sess_full}")
            # Session start/end

            sess_start = datetime.datetime.strptime(
                session.get("date_start"), "%Y-%m-%dT%H:%M:%S%z"
            )
            sess_end = datetime.datetime.strptime(
                session.get("date_end"), "%Y-%m-%dT%H:%M:%S%z"
            )
            e = cc.create_event(
                f"[{clas}] {sess}",
                f"Event: {title}\nClass: {clas}\nSession: {sess_full}",
                circuit,
                cc.check_url(f'/en/calendar/2023/event/{event.get("url")}', host),
                sess_start,
                sess_end,
            )
            flag = cc.add_if_new(clas, e) or flag

            for f in calendar_filter:
                if sess in f["filter"]:
                    flag = cc.add_if_new(f"{clas}_{f['appendix']}", e) or flag

        updates = flag or updates
        print(f'{"Event updated" if flag else "No updates found"}\n')

    for clas in classes:
        updates = not cc.same_size(clas) or updates
    print(f'\n{"Calendar UPDATED" if updates else "No updates to the calendar"}')

    cc.write_calendars(output_dir, appendix)

import datetime
import requests
import sys
from .calendar_common import CalendarCommon


def gp_main(output_dir, debug=False):
    cc = CalendarCommon(debug=debug)
    host = "https://www.motogp.com"
    calendar_url = "https://www.motogp.com/api/calendar-front/be/events-api/api/v1/business-unit/mgp/season/2023/events?type=SPORT&kind=GP"  # noqa: E501

    calendar_filter = [
        {"appendix": "filtered", "filter": ["Q1", "Q2", "SPR", "RAC", "RAC1", "RAC2"]},
        {"appendix": "sprint-and-race", "filter": ["SPR", "RAC", "RAC1", "RAC2"]},
    ]
    sess_exclude = ["VIDEO", "SHOW", "PRESS"]
    classes = ["Moto3", "Moto2", "MotoGP", "MotoE"]
    appendix = "2023_calendar"
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

    events = r.json()
    events = events.get("events") or []
    updates = False

    print(f"Found {len(events)} events in the calendar.")
    for event in events or []:
        # print(link['href'])
        print(f"Loading {event.get('hashtag')}...")
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

    # cc.clean_calendars()
    cc.write_calendars(output_dir, appendix)

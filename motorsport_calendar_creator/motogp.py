import datetime
import requests
import sys

import calendar_common as cc


host = "https://www.motogp.com"
calendar_url = "https://www.motogp.com/api/calendar-front/be/events-api/api/v1/business-unit/mgp/season/2023/events?type=SPORT&kind=GP"  # noqa: E501
sess_filter = ["Q1", "Q2", "RAC"]
sess_exclude = ["VIDEO", "SHOW", "PRESS"]
classes = ["Moto3", "Moto2", "MotoGP", "MotoE"]
output_folder = "../data/"
appendix = "2023_calendar"


def main():

    names = []
    for c in classes:
        names.append(c)
        names.append(c + "_filtered")

    cc.create_calendars(output_folder, names, appendix)

    r = requests.get(calendar_url)
    print(r.url)

    if r.status_code != 200:
        print("no connection")
        sys.exit()

    events = r.json()
    events = events.get("events") or []

    print(f"Found {len(events)} events in the calendar.")
    for event in events or []:
        # print(link['href'])
        print(f"Loading {event.get('hashtag')}...")
        # event name
        title = event.get("name").strip()
        print(title)

        # circuit name / location
        if not event.get("circuit"):
            print("NO CIRCUIT INFO - ABORTING")
            continue

        circuit = f"{event['circuit'].get('name')} - {event['circuit'].get('city')}"
        print(circuit)

        # sessions
        sessions = event.get("broadcasts")
        print(f"Found {len(sessions)} sessions in the event.")
        # print(sessions)

        for session in sessions:
            # Category Name
            clas = session["category"]["name"].strip()
            if clas not in classes:
                continue
            # Session Name
            sess_full = session.get("name").strip()
            sess = session.get("shortname").strip()

            if sess in sess_exclude:
                print(f"{clas} {sess} {sess_full} skipped.")
                continue
            print(f"{clas} {sess} {sess_full}")
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
            cc.add_if_new(clas, e)

            if sess in sess_filter:
                cc.add_if_new(f"{clas}_filtered", e)

        # break
        print("")

    cc.write_calendars(output_folder, appendix)


main()

import re
from datetime import date
import requests
from bs4 import BeautifulSoup
from concert_calendar.event_images import discard_repeated_generic_images, element_image_url
from concert_calendar.models import ConcertEvent

SOURCE_NAME="Nouveau Casino"; PROGRAMME_URL="https://www.nouveaucasino.fr/"; REQUEST_TIMEOUT=30
HEADERS={"User-Agent":"Mozilla/5.0 AppleWebKit/537.36 Safari/537.36"}
def clean(v): return re.sub(r"\s+"," ",v or "").strip()
def parse_items(soup, *, today=None):
    cutoff=today or date.today(); year=cutoff.year; previous_month=0; result=[]
    for day in soup.select("li.day_item"):
        dm=clean((day.select_one("time .date") or day).get_text(" ",strip=True))
        match=re.fullmatch(r"(\d{1,2})\.(\d{1,2})",dm)
        if not match: continue
        day_number,month=map(int,match.groups())
        if not previous_month and month < cutoff.month: year += 1
        if previous_month and month < previous_month: year += 1
        previous_month=month
        try: event_date=date(year,month,day_number)
        except ValueError: continue
        for card in day.select("li.event_item[data-type='concert']"):
            title=clean((card.select_one(".event_header h3") or card).get_text(" ",strip=True))
            sold=bool(re.search(r"\[(?:sold out|complet)\]",title,re.I))
            title=clean(re.sub(r"\s*\[(?:sold out|complet)\]\s*","",title,flags=re.I))
            if not title or event_date < cutoff: continue
            start=card.select_one(".event_header p span:not(.timeend)")
            ticket=card.select_one(".event_tickets a[href]")
            genres=[clean(x.get_text(" ",strip=True)) for x in card.select(".genre_list .tag")]
            image=element_image_url(card.select_one("picture img"),base_url=PROGRAMME_URL)
            result.append(ConcertEvent(date=event_date.isoformat(),headliner=title,venue=SOURCE_NAME,
                city="Paris",department="75",genre=", ".join(genres) or None,
                ticket_url=ticket.get("href") if ticket else PROGRAMME_URL,
                ticket_status="sold_out" if sold else "tickets",sold_out=sold,
                start_time=clean(start.get_text()) if start else None,image_url=image,
                image_source=SOURCE_NAME if image else None))
    return result
def load_events():
    session=requests.Session(); print(f"Downloading Nouveau Casino programme: {PROGRAMME_URL}")
    response=session.get(PROGRAMME_URL,headers=HEADERS,timeout=REQUEST_TIMEOUT); response.raise_for_status()
    events={}
    for event in parse_items(BeautifulSoup(response.text,"html.parser")):
        events.setdefault((event.date,event.headliner.casefold()),event)
    result=discard_repeated_generic_images(list(events.values()))
    print(f"Created {len(result)} Nouveau Casino ConcertEvent records"); return result

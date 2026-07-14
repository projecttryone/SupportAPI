"""pure filter , and info return file for getting information on tickers """
import json
from pathlib import Path
_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


print("DATA_DIR:", _DATA_DIR)

def load_tickets(path: Path | None = None) -> list[dict]:
    """Load the seed (tickets.json) into memory  as a list of dicts."""
    target = path or (_DATA_DIR / "tickets.json")
    with target.open(encoding="utf-8") as fh:
        return json.load(fh)
        #this returns the info in tickes.son as a list[dict]


#filter by priority
def filter_by_priority(tickets: list[dict], priority: str) -> list[dict]:
    """Return tickets whose priority matches the given value . Case- insensitive."""
    desired  = priority.lower() #all lowercase
    return [ticket for ticket in tickets if ticket.get("priority", "").lower() == desired ]  #list comprehension , gather all the dict that meet the condition into a new dict 


#filter by tenant 

def filter_by_tenant(tickets: list[dict] , tenant : str) -> list[dict]:
    """Return tickets scoped to one tenant . Tenant isolation."""
    return [ticket for ticket in tickets if ticket.get("tenant", "") == tenant ] #ticket["tenant"]


if __name__ == "__main__":
    tickets = load_tickets()
    # print(len(tickets))
    # print(type(tickets))
    # print(type(tickets[0]))
    # print(json.dumps(tickets[0], indent= 2))


    urgent = filter_by_priority(tickets , "urgent")
    print(f"urgent: {len(urgent)}")

    # acme = filter_by_tenant(tickets , "acme-corp")
    # print(f"acme-corp tickets : {len(acme)}")

    acme = filter_by_tenant(tickets , "acme-corp")
    print(f"acme-corp tickets :{len(acme)}")
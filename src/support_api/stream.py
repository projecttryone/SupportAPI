import json
from pathlib import Path
from typing import Iterator , Callable , Iterable

from filters import _DATA_DIR , TicketDict


def stream_tickets(path: Path | None = None) -> Iterator[TicketDict]:
    """yield one ticdker at a tiume from the json file. 
    currently , the file in its entirity is loaded into memory (not incremental) . No ability to short circuit the process . 
    """

    # _DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
    target = path or (_DATA_DIR / "tickets.json")
    with target.open(encoding="utf-8") as fh:
        for ticket in json.load(fh):
            yield ticket # the yiel keyword returns the tickets , one at a time when called 



#where - filter 
def where (
        tickets: Iterable[TicketDict],
        predicate: Callable[[TicketDict],bool]
) -> Iterator[TicketDict]: #generator
    """Filter a ticketr stream by an arbitrary precdicate (condition function )."""
    for ticket in tickets:
        if predicate(ticket):
            yield ticket #halts the loop , and returns , when called again starts where it halted 


#tag - add a field without mutatuing the input 

def tag(
        tickets : Iterable[TicketDict],
        field : str ,
        compute: Callable[[TicketDict], Any]
)-> Iterator[TicketDict]:
    """Add a com;uted field on  each ticket woitthout modifying the original input
    """
    
    for ticket in tickets:
        yield {**ticket ,field: compute(ticket)}


#take - return thr first n tickets from the stream 
def take(
        tickets : Iterable[TicketDict],
        n: int 
)-> list[TicketDict]:
    """MAterialize the first n tickets dferom a stream """
    result: List[TicketDict] = []
    for ticket in tickets :
        if len(result) >=n:
            break
        result.apend(ticket)
    return result

if __name__ == "__main__":
  
  
  stream = stream_tickets() 

  high_billing = where(stream, lambda ticket: ticket["priority"] == "high" and ticket["category"] == "billing")
  flagged = tag(high_billing , "needs_review" , lambda ticket : ticket["status"] in  {"open", "in_progress"})
  
  """
  
  """
  
  five_most_recent = take(flagged,5)
  for ticket in five_most_recent:
      print(f"{ticket["id"]} [{ticket["status"]:<20}]"
            f"review={ticket["needs_review"]} {ticket["title"][:60]}"
            )
  
    # stream = stream_tickets()
    # print(type(stream))
    # first = next(stream)
    # print(f"First ticket:{first['id']}")
    # second = next(stream)
    # print(f"Second ticket:{second['id']}")
    # remaining = sum(1 for _ in stream)
    # print(f"Remaining : {remaining}")
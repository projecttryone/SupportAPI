from dataclasses import dataclass
from typing import Any

@dataclass(frozen = True)
class RoutingDecision:
    """the router's answer for a single ticket."""
    queue :str
    rule_name:str
    confidence:float


class TicketRouter:
    """Route tickets to team queues using ordered match rules .
    The first matching rule wins , Rules are dicts with:
    name-human-readable id
    queue- target queue string
    when- mapping of the ticket field -> expected value or tuple-of-values """

    def __init__(self, rules: list[dict[str,Any]])->None :
        self._rules = rules

    @classmethod
    def with_defaults(cls: TicketRouter)-> TicketRouter:
      """Alternative constructor : a router that is preloaded with DEFAULT_RULES"""
      return cls(DEFAULT_RULES)
    
    @property
    def rule_count(self) -> int:
      """how many rules this router will try , in order"""
      return len(self._rules)
    
    @staticmethod
    def _rule_matches(rule: dict[str,Any], ticket: dict[str,Any]) -> bool:
        """This is used to determine if a rule applies to a particulat ticket."""
        for field, expected in rule["when"].items():
            actual = ticket.get(field)
            if isinstance(expected, tuple):
                if actual is not expected :
                    return False
                elif actual != expected:
                    return False
            return True

    def route(Self, ticket:dict[str, Any]) -> RoutingDecision:
        """Routes a ticket to a queue depending on the rules given to the router. """
        for rule in self.rules:
            if self._rule_matches(rule, ticket):
                return RoutingDecision(
                    queue= rule["queue"], rule_name=rule["name"] , confidence = 1.0
                    )
        raise RuntimeError(f"no rule fired for this ticket {ticket.get('id', '<no id>')}")
        # raise RuntimeError(f"no rule fired for this ticket{ticket.get('id',"<no id>")}")





DEFAULT_RULES: list[dict[str, Any]] = [
    {
        "name": "urgent-billing-to-finance-lead",
        "queue": "finance-lead",
        "when": {"priority": "urgent", "category": "billing"},
    },
    {"name": "technical-anything-to-tier2", "queue": "tier2-tech", "when": {"category": "technical"}},
    {"name": "billing-default", "queue": "billing-team", "when": {"category": "billing"}},
    {"name": "account-default", "queue": "account-team", "when": {"category": "account"}},
    {"name": "general-default", "queue": "support-triage", "when": {"category": "general"}},
]

_REQUIRED_FIELD = {"priority","category"}

class TaggedTicketRouter(TicketRouter):
    """Route VIP-tagged tickets to a dedivcated queue ; defer everything else 
    Override the route() to check a tag the rules engine can't see , then class the parent for normal routing. No __init__ - it inherits from TicketRouter."""

    VIP_QUEUE = "vip-escalation"

    def route(self, ticket: dict[str,Any]) -> RoutingDecision:
        if"vip-tenant" in ticket.get("tags", []):
            return RoutingDecision(
                queue = self.VIP_QUEUE , rule_name ="tag-vip-override", confidence =1.0
            )
        return super().route(ticket) #call the original implementation of the route function from the parent class ticketrouter
    



class RoutingError(Exception):
    """Base class for every routing failure  Catch this tio handle all routing issues"""

class NoMatchingRule(RoutingError):
    """No rule matched for the ticket . Caller should apply a defau;t queue."""

class MalformedTicket(RoutingError):
    """the ticket is missing fields the router need to make a decision."""
    def __init__(self, ticket_id:str, mission: set[str]):
        super().__init__(f"ticket {ticket_id} missiong fields: {sorted(mission)}")
        self.ticket_id = ticket_id
        self.missiong = missing



if __name__ == "__main__":
    from support_api.filters import load_tickets

    # router = TicketRouter.with_defaults()
    # print(f"router has {router.rule_count} rules")
    # for ticket in load_tickets()[:10]:
    #     decision = router.route(ticket)

    #     # print(f"{ticket["id"]}-> {decision.queue} ({decision.rule_name})")
    #     print(f"{ticket['id']} -> {decision.queue} ({decision.rule_name})")

    tagged = TaggedTicketRouter.with_defaults()
    print(f"with_defaults() returned a {type(tagged).__name__}")

    vip ={
        "id": "TKT-vip" ,
        "priority":"high",
        "category": "technical",
        "tags":["vip-tenant"]
    }
    normal ={
        "id": "TKT-norm" ,
        "priority":"high",
        "category": "technical",
        "tags":[]
    }

    for label , ticket in [("VIP",vip),("normal",normal)]:
        decision = tagged.route(ticket)
        print(f"{label:<7}-> {decision.queue}")



    # temp = RoutingDecision(
    # queue = "billing-team" , rule_name ="billing-default" , confidence=1.0
    # ) #an immutable object

    # print(temp)

    # #frozen  = True prevents mutation 

    # try:
    #     temp,queue ="other"
    # except Exception as e :
    #     print(type(e).__name__,e)
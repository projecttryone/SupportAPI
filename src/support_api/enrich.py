from typing import Any 
import httpx
import structlog
import time
import functools

_log = structlog.get_logger(__name__)
_DEFAULT_CONCURRENCY =10
base_url: str ="https://httpbin.org"


async def enrich_batch(
        
        tickets: list[dict[str,Any]],
        concurrency : int = _DEFAULT_CONCURRENCY) -> list[dict[str, Any]]:
    """enrich many tickets concurrently (at the same time), capped by a semaphhore(concurrency limit)"""

    semaphore = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(timeout=10.0) as client:

        async def _one(ticket:dict[str,Any]) -> dict[str , Any]:
            async with semaphore:
                return await enrich_ticket(ticket, client, base_url = base_url)
        return await asyncio.gather(*(_one(ticket) for ticket in tickets))





async def enrich_ticket(    ticket: dict[str, Any],
                  client: httpx.AsyncClient,
                  base_url: str ="https://httpbin.org"
                  
                  )->dict[str, Any]:
    """Fetch enrichment data for one ticket.
    Return a new dict - never mutates the existing input . The enrichment payload is whatever the mock endpoint echos back under 'args'
    """

    _log.info("enrichment_Started", ticket_id=ticket["id"])
    response = await client.get(f"{base_url}/get", params={"customer_id":ticket["customer_id"]})
    #if i need a error raise in the program 


    response.raise_for_status()
    echoed = response.json().get("args",{})
    _log.info("enrich_completed", ticket_id = ticket["id"],status=response.status_code)
    return{**ticket , "enrichment": echoed}



if __name__ == "__main__":
    import asyncio
    import json
    from pathlib import Path
    from support_api.utils import atomic_write , timed
    from support_api.filters import load_tickets
    import time
    import functools
    structlog.configure() #make out log statements go to STDOUT (console)

    async def main() -> None:
        tickets = load_tickets()[:20]
        try:
            results = await enrich_batch(tickets , concurrency=5)
        except httpx.RequestError as err:
            print(f"Network unreachable ({type(err).__name__});  skip this demo or retry later.")
            return
        print(f"\nEnriched{len(results)} tickets (concurrency=5)")
        print(f"First result enrichment: {results[0]['enrichment']}")

        out = Path("enrich.json")
        with atomic_write(out) as fh :
            json.dump(results , fh , indent=2)
        print(f"Wrote: {out}")

    @timed(label ='enrich-batch-run')
    def run() -> None:
        asyncio.run(main())
    
    run()




    #     ticket = load_tickets()[0]
    #     async with httpx.AsyncClient(timeout = 10.0) as client :
    #         try:
    #             enrigh = await enrich_ticket(ticket, client) 
    #         except httpx.RequestError  as err:
    #             print(f"Network unreachable({type(err).__name__}); skip this demo or retry later.")
    #             return 
        
    #     print(f"{enrigh['id']} -> {enrigh['enrichment']}")


    # asyncio.run(main())
from support_api.filters import filter_by_priority , filter_by_tenant

def test_filter_by_priority_urgent_subset(Seed_tickers):
    urgent = filter_by_priority(Seed_tickets,"urgent")
    assert all(ticket["priority"] == "urgent" for ticket in urgent )


def test_filter_by_tenant_Scopes_correctly(seed_tickets):
    acme = filter_by_tenant(seed_tickets , "acme-corp")
    assert all(ticket["tenant"] == "acme-corp" for ticket in acme) 
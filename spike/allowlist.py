"""Source-domain allowlist for the feasibility spike.

Categories follow the brief: .gov, .edu, national archives, Library of Congress, Smithsonian,
NPS, Britannica, encyclopedias, official estates and halls of fame, and national biography
dictionaries. Anything else is rejected, even if it is accurate. This list needs human
review before any production use.
"""
from urllib.parse import urlparse

SUFFIXES = (".gov", ".edu")  # covers loc.gov, archives.gov, nps.gov, si.edu, universities

HOSTS = {
    # encyclopedias / national biography dictionaries
    "britannica.com": "encyclopedia",
    "encyclopedia.com": "encyclopedia",
    "thecanadianencyclopedia.ca": "encyclopedia",
    "biographi.ca": "national biography dictionary (Canada)",
    # national archives and official agency sites outside .gov
    "docsteach.org": "U.S. National Archives education site",
    "stampsforever.com": "U.S. Postal Service stamp archive",
    "hdbg.de": "Haus der Bayerischen Geschichte (Bavarian state history institution)",
    "bibalex.org": "Bibliotheca Alexandrina (national library)",
    "wisconsinhistory.org": "Wisconsin Historical Society (state historical society)",
    # official estates, awarding bodies and halls of fame
    "irvingberlin.com": "official estate",
    "invent.org": "National Inventors Hall of Fame",
    "songhall.org": "Songwriters Hall of Fame",
    "walkoffame.com": "Hollywood Walk of Fame (official)",
    "rockhall.com": "Rock & Roll Hall of Fame",
    "fiba.basketball": "FIBA Hall of Fame",
    "hoophall.com": "Naismith Memorial Basketball Hall of Fame",
    "nobelprize.org": "awarding body",
    "pritzkerprize.com": "awarding body",
    "grammy.com": "awarding body",
    "goldenglobes.com": "awarding body",
    "oscars.org": "awarding body",
    "televisionacademy.com": "awarding body",
    "ethz.ch": "university (ETH Zurich library)",
}


def category(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host.endswith(SUFFIXES):
        return host.rsplit(".", 1)[-1]
    for allowed_host, label in HOSTS.items():
        if host == allowed_host or host.endswith("." + allowed_host):
            return label
    return ""


def allowed(url: str) -> bool:
    return urlparse(url).scheme == "https" and bool(category(url))

#!/usr/bin/env python3
"""
Fetches NCAA tournament results from ESPN, scores all 12 brackets,
and rebuilds the leaderboard HTML. Run manually or via GitHub Actions.
"""

import json
import re
import urllib.request
from datetime import datetime

# =====================================================
# ALL 12 ENTRIES' PICKS (keyed by game ID)
# =====================================================
PICKS = {
    "Bird Bath": {
        "FF1":"UMBC","FF2":"Lehigh","FF3":"Texas","FF4":"Miami (OH)",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Cal Baptist",
        "E5":"South Florida","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Clemson","S3":"Vanderbilt","S4":"Troy",
        "S5":"VCU","S6":"Illinois","S7":"Texas A&M","S8":"Houston",
        "MW1":"Michigan","MW2":"Saint Louis","MW3":"Akron","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Santa Clara","MW8":"Iowa State",
        "W1":"Arizona","W2":"Utah State","W3":"High Point","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Missouri","W8":"Purdue",
        "E9":"Duke","E10":"St. John's","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Vanderbilt","S11":"Illinois","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Tennessee","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"BYU","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"Houston",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"Duke","S15":"Houston","MW15":"Michigan","W15":"Arizona",
        "FF_1":"Houston","FF_2":"Arizona","CHIP":"Arizona"
    },
    "Open Vet": {
        "FF1":"UMBC","FF2":"Lehigh","FF3":"Texas","FF4":"SMU",
        "E1":"Duke","E2":"Ohio State","E3":"St. John's","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Clemson","S3":"Vanderbilt","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Georgia","MW3":"Texas Tech","MW4":"Alabama",
        "MW5":"SMU","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Villanova","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Missouri","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"Illinois","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Virginia","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"Michigan State",
        "S13":"Florida","S14":"Illinois",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"Duke","S15":"Florida","MW15":"Michigan","W15":"Arizona",
        "FF_1":"Duke","FF_2":"Michigan","CHIP":"Duke"
    },
    "Talkatoo": {
        "FF1":"UMBC","FF2":"Prairie View A&M","FF3":"Texas","FF4":"Miami (OH)",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Clemson","S3":"McNeese","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Saint Louis","MW3":"Texas Tech","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Villanova","W3":"High Point","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Miami (FL)","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"North Carolina","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Virginia","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"Houston",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"UConn","S15":"Houston","MW15":"Michigan","W15":"Arizona",
        "FF_1":"Houston","FF_2":"Arizona","CHIP":"Houston"
    },
    "PrimVeterinary": {
        "FF1":"UMBC","FF2":"Lehigh","FF3":"NC State","FF4":"SMU",
        "E1":"Siena","E2":"TCU","E3":"Northern Iowa","E4":"Kansas",
        "E5":"South Florida","E6":"North Dakota State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Clemson","S3":"McNeese","S4":"Nebraska",
        "S5":"VCU","S6":"Penn","S7":"Texas A&M","S8":"Houston",
        "MW1":"UMBC","MW2":"Georgia","MW3":"Akron","MW4":"Hofstra",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Santa Clara","MW8":"Tennessee State",
        "W1":"Long Island","W2":"Utah State","W3":"Wisconsin","W4":"Arkansas",
        "W5":"NC State","W6":"Gonzaga","W7":"Missouri","W8":"Purdue",
        "E9":"TCU","E10":"Kansas","E11":"North Dakota State","E12":"UConn",
        "S9":"Clemson","S10":"McNeese","S11":"VCU","S12":"Texas A&M",
        "MW9":"Georgia","MW10":"Hofstra","MW11":"Tennessee","MW12":"Tennessee State",
        "W9":"Utah State","W10":"Arkansas","W11":"NC State","W12":"Purdue",
        "E13":"TCU","E14":"UConn",
        "S13":"Clemson","S14":"Texas A&M",
        "MW13":"Georgia","MW14":"Tennessee",
        "W13":"Arkansas","W14":"Purdue",
        "E15":"UConn","S15":"Texas A&M","MW15":"Georgia","W15":"Purdue",
        "FF_1":"UConn","FF_2":"Georgia","CHIP":"UConn"
    },
    "VetGeni": {
        "FF1":"Howard","FF2":"Lehigh","FF3":"Texas","FF4":"SMU",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Clemson","S3":"McNeese","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Texas A&M","S8":"Houston",
        "MW1":"Michigan","MW2":"Saint Louis","MW3":"Texas Tech","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Villanova","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Missouri","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"Illinois","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Tennessee","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"Houston",
        "MW13":"Alabama","MW14":"Tennessee",
        "W13":"Arizona","W14":"Purdue",
        "E15":"UConn","S15":"Houston","MW15":"Tennessee","W15":"Purdue",
        "FF_1":"UConn","FF_2":"Houston","CHIP":"Houston"
    },
    "ScribVet": {
        "FF1":"UMBC","FF2":"Prairie View A&M","FF3":"NC State","FF4":"SMU",
        "E1":"Duke","E2":"TCU","E3":"Northern Iowa","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Iowa","S3":"Vanderbilt","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Georgia","MW3":"Texas Tech","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Villanova","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Miami (FL)","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"North Carolina","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Virginia","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"North Carolina",
        "MW13":"Michigan","MW14":"Virginia",
        "W13":"Arizona","W14":"Gonzaga",
        "E15":"Duke","S15":"Florida","MW15":"Michigan","W15":"Gonzaga",
        "FF_1":"Duke","FF_2":"Gonzaga","CHIP":"Duke"
    },
    "Otto": {
        "FF1":"UMBC","FF2":"Prairie View A&M","FF3":"Texas","FF4":"SMU",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Iowa","S3":"Vanderbilt","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Georgia","MW3":"Texas Tech","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Villanova","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Miami (FL)","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Louisville","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"North Carolina","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Tennessee","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"BYU","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"Houston",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"UConn","S15":"Houston","MW15":"Michigan","W15":"Arizona",
        "FF_1":"Houston","FF_2":"Michigan","CHIP":"Houston"
    },
    "Scope Health": {
        "FF1":"UMBC","FF2":"Prairie View A&M","FF3":"NC State","FF4":"SMU",
        "E1":"Duke","E2":"Ohio State","E3":"Northern Iowa","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCF","E8":"UConn",
        "S1":"Florida","S2":"Iowa","S3":"McNeese","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Georgia","MW3":"Akron","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Villanova","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Missouri","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"Illinois","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Tennessee","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"Houston",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"Duke","S15":"Houston","MW15":"Iowa State","W15":"Arizona",
        "FF_1":"Duke","FF_2":"Iowa State","CHIP":"Duke"
    },
    "VetRec": {
        "FF1":"Howard","FF2":"Lehigh","FF3":"NC State","FF4":"SMU",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Iowa","S3":"McNeese","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Texas A&M","S8":"Houston",
        "MW1":"Michigan","MW2":"Georgia","MW3":"Texas Tech","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Villanova","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Miami (FL)","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"North Carolina","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Tennessee","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"Houston",
        "MW13":"Alabama","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"UConn","S15":"Houston","MW15":"Iowa State","W15":"Purdue",
        "FF_1":"Houston","FF_2":"Purdue","CHIP":"Houston"
    },
    "VetSOAP": {
        "FF1":"UMBC","FF2":"Lehigh","FF3":"Texas","FF4":"SMU",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Kansas",
        "E5":"South Florida","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Clemson","S3":"Vanderbilt","S4":"Nebraska",
        "S5":"North Carolina","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Georgia","MW3":"Texas Tech","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Kentucky","MW8":"Iowa State",
        "W1":"Arizona","W2":"Utah State","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Miami (FL)","W8":"Purdue",
        "E9":"Duke","E10":"Kansas","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Nebraska","S11":"Illinois","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Virginia","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Florida","S14":"Houston",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"UConn","S15":"Houston","MW15":"Iowa State","W15":"Arizona",
        "FF_1":"Houston","FF_2":"Arizona","CHIP":"Houston"
    },
    "Digital Empathy": {
        "FF1":"Howard","FF2":"Lehigh","FF3":"Texas","FF4":"Miami (OH)",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Kansas",
        "E5":"Louisville","E6":"Michigan State","E7":"UCLA","E8":"UConn",
        "S1":"Florida","S2":"Iowa","S3":"Vanderbilt","S4":"Nebraska",
        "S5":"VCU","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Georgia","MW3":"Akron","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Santa Clara","MW8":"Iowa State",
        "W1":"Arizona","W2":"Utah State","W3":"Wisconsin","W4":"Arkansas",
        "W5":"BYU","W6":"Gonzaga","W7":"Miami (FL)","W8":"Purdue",
        "E9":"Duke","E10":"St. John's","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Vanderbilt","S11":"Illinois","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Virginia","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"Michigan State",
        "S13":"Florida","S14":"Houston",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"Duke","S15":"Houston","MW15":"Michigan","W15":"Arizona",
        "FF_1":"Duke","FF_2":"Arizona","CHIP":"Arizona"
    },
    "HappyDoc": {
        "FF1":"Howard","FF2":"Lehigh","FF3":"Texas","FF4":"SMU",
        "E1":"Duke","E2":"TCU","E3":"St. John's","E4":"Kansas",
        "E5":"South Florida","E6":"Michigan State","E7":"UCF","E8":"UConn",
        "S1":"Florida","S2":"Iowa","S3":"Vanderbilt","S4":"Nebraska",
        "S5":"VCU","S6":"Illinois","S7":"Saint Mary's","S8":"Houston",
        "MW1":"Michigan","MW2":"Saint Louis","MW3":"Akron","MW4":"Alabama",
        "MW5":"Tennessee","MW6":"Virginia","MW7":"Santa Clara","MW8":"Iowa State",
        "W1":"Arizona","W2":"Utah State","W3":"Wisconsin","W4":"Arkansas",
        "W5":"Texas","W6":"Gonzaga","W7":"Miami (FL)","W8":"Purdue",
        "E9":"Duke","E10":"St. John's","E11":"Michigan State","E12":"UConn",
        "S9":"Florida","S10":"Vanderbilt","S11":"Illinois","S12":"Houston",
        "MW9":"Michigan","MW10":"Alabama","MW11":"Virginia","MW12":"Iowa State",
        "W9":"Arizona","W10":"Arkansas","W11":"Gonzaga","W12":"Purdue",
        "E13":"Duke","E14":"UConn",
        "S13":"Vanderbilt","S14":"Houston",
        "MW13":"Michigan","MW14":"Iowa State",
        "W13":"Arizona","W14":"Purdue",
        "E15":"Duke","S15":"Houston","MW15":"Michigan","W15":"Arizona",
        "FF_1":"Duke","FF_2":"Arizona","CHIP":"Arizona"
    },
}

ENTRY_META = {
    "Bird Bath":       {"tool": "Claude", "champ": "Arizona", "url": "https://first100.io"},
    "Open Vet":        {"tool": "Open Vet AI", "champ": "Duke", "url": "https://openvet.ai"},
    "Talkatoo":        {"tool": "Talkatoo", "champ": "Houston", "url": "https://talkatoo.com"},
    "PrimVeterinary":  {"tool": "PrimVeterinary AI", "champ": "UConn", "url": "https://primveterinary.com"},
    "VetGeni":         {"tool": "VetGeni AI", "champ": "Houston", "url": "https://vetgeni.com"},
    "ScribVet":        {"tool": "ScribVet AI", "champ": "Duke", "url": "https://scribvet.com"},
    "Otto":            {"tool": "Otto AI", "champ": "Houston", "url": "https://otto.vet"},
    "Scope Health":    {"tool": "Scope Health AI", "champ": "Duke", "url": "https://scopehealth.com"},
    "VetRec":          {"tool": "VetRec AI", "champ": "Houston", "url": "https://vetrec.io"},
    "VetSOAP":         {"tool": "VetSOAP AI", "champ": "Houston", "url": "https://vetsoap.ai"},
    "Digital Empathy": {"tool": "Claude + ChatGPT", "champ": "Arizona", "url": "https://digitalempathyvet.com"},
    "HappyDoc":        {"tool": "HappyInsights", "champ": "Arizona", "url": "https://happydoc.ai"},
}

# Points per round
POINTS = {
    "First Four": 1, "Round of 64": 1, "Round of 32": 2,
    "Sweet 16": 4, "Elite 8": 8, "Final Four": 16, "Championship": 32
}

ROUND_INDEX = {
    "First Four": 0, "Round of 64": 0, "Round of 32": 1,
    "Sweet 16": 2, "Elite 8": 3, "Final Four": 4, "Championship": 5
}

# Game metadata: game_id -> (round, matchup_label)
GAMES = {
    "FF1": ("First Four","UMBC vs Howard"),
    "FF2": ("First Four","Prairie View A&M vs Lehigh"),
    "FF3": ("First Four","Texas vs NC State"),
    "FF4": ("First Four","Miami (OH) vs SMU"),
    "E1": ("Round of 64","Duke vs Siena"), "E2": ("Round of 64","Ohio State vs TCU"),
    "E3": ("Round of 64","St. John's vs Northern Iowa"), "E4": ("Round of 64","Kansas vs Cal Baptist"),
    "E5": ("Round of 64","Louisville vs South Florida"), "E6": ("Round of 64","Michigan State vs North Dakota State"),
    "E7": ("Round of 64","UCLA vs UCF"), "E8": ("Round of 64","UConn vs Furman"),
    "S1": ("Round of 64","Florida vs Lehigh/PV A&M"), "S2": ("Round of 64","Clemson vs Iowa"),
    "S3": ("Round of 64","Vanderbilt vs McNeese"), "S4": ("Round of 64","Nebraska vs Troy"),
    "S5": ("Round of 64","North Carolina vs VCU"), "S6": ("Round of 64","Illinois vs Penn"),
    "S7": ("Round of 64","Saint Mary's vs Texas A&M"), "S8": ("Round of 64","Houston vs Idaho"),
    "MW1": ("Round of 64","Michigan vs UMBC/Howard"), "MW2": ("Round of 64","Georgia vs Saint Louis"),
    "MW3": ("Round of 64","Texas Tech vs Akron"), "MW4": ("Round of 64","Alabama vs Hofstra"),
    "MW5": ("Round of 64","Tennessee vs Miami(OH)/SMU"), "MW6": ("Round of 64","Virginia vs Wright State"),
    "MW7": ("Round of 64","Kentucky vs Santa Clara"), "MW8": ("Round of 64","Iowa State vs Tennessee State"),
    "W1": ("Round of 64","Arizona vs LIU"), "W2": ("Round of 64","Villanova vs Utah State"),
    "W3": ("Round of 64","Wisconsin vs High Point"), "W4": ("Round of 64","Arkansas vs Hawaii"),
    "W5": ("Round of 64","BYU vs Texas/NC State"), "W6": ("Round of 64","Gonzaga vs Kennesaw State"),
    "W7": ("Round of 64","Miami (FL) vs Missouri"), "W8": ("Round of 64","Purdue vs Queens"),
    "E9": ("Round of 32","E9"), "E10": ("Round of 32","E10"),
    "E11": ("Round of 32","E11"), "E12": ("Round of 32","E12"),
    "S9": ("Round of 32","S9"), "S10": ("Round of 32","S10"),
    "S11": ("Round of 32","S11"), "S12": ("Round of 32","S12"),
    "MW9": ("Round of 32","MW9"), "MW10": ("Round of 32","MW10"),
    "MW11": ("Round of 32","MW11"), "MW12": ("Round of 32","MW12"),
    "W9": ("Round of 32","W9"), "W10": ("Round of 32","W10"),
    "W11": ("Round of 32","W11"), "W12": ("Round of 32","W12"),
    "E13": ("Sweet 16","E13"), "E14": ("Sweet 16","E14"),
    "S13": ("Sweet 16","S13"), "S14": ("Sweet 16","S14"),
    "MW13": ("Sweet 16","MW13"), "MW14": ("Sweet 16","MW14"),
    "W13": ("Sweet 16","W13"), "W14": ("Sweet 16","W14"),
    "E15": ("Elite 8","E15"), "S15": ("Elite 8","S15"),
    "MW15": ("Elite 8","MW15"), "W15": ("Elite 8","W15"),
    "FF_1": ("Final Four","FF_1"), "FF_2": ("Final Four","FF_2"),
    "CHIP": ("Championship","CHIP"),
}

# =====================================================
# ESPN API - fetch tournament results
# =====================================================
# NCAA Tournament group ID
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=100&dates={date}&limit=50"

# Name normalization: ESPN name -> our bracket name
NAME_MAP = {
    "Connecticut": "UConn",
    "UConn Huskies": "UConn",
    "Miami": "Miami (FL)",
    "Miami Hurricanes": "Miami (FL)",
    "Miami (OH) RedHawks": "Miami (OH)",
    "Miami RedHawks": "Miami (OH)",
    "St. John's Red Storm": "St. John's",
    "Saint Mary's Gaels": "Saint Mary's",
    "Saint Mary's": "Saint Mary's",
    "North Dakota State Bison": "North Dakota State",
    "N. Dakota St": "North Dakota State",
    "Long Island University": "Long Island",
    "LIU": "Long Island",
    "LIU Sharks": "Long Island",
    "Kennesaw State Owls": "Kennesaw State",
    "Tennessee State Tigers": "Tennessee State",
    "Prairie View A&M": "Prairie View A&M",
    "PV A&M": "Prairie View A&M",
    "Cal Baptist": "Cal Baptist",
    "California Baptist": "Cal Baptist",
    "Cal Baptist Lancers": "Cal Baptist",
    "UCF Knights": "UCF",
    "VCU Rams": "VCU",
    "South Florida Bulls": "South Florida",
    "USF": "South Florida",
}

def normalize_name(espn_name):
    """Normalize ESPN team name to match our bracket names."""
    if espn_name in NAME_MAP:
        return NAME_MAP[espn_name]
    # Strip common suffixes
    for suffix in [" Wildcats", " Blue Devils", " Buckeyes", " Horned Frogs",
                   " Red Storm", " Jayhawks", " Cardinals", " Bulls", " Spartans",
                   " Bison", " Bruins", " Huskies", " Gators", " Tigers",
                   " Commodores", " Cowboys", " Cornhuskers", " Trojans",
                   " Tar Heels", " Rams", " Fighting Illini", " Gaels",
                   " Aggies", " Cougars", " Vandals", " Wolverines",
                   " Bulldogs", " Billikens", " Red Raiders", " Zips",
                   " Crimson Tide", " Pride", " Volunteers", " RedHawks",
                   " Cavaliers", " Broncos", " Cyclones", " Mountaineers",
                   " Anteaters", " Coyotes", " Roadrunners", " Panthers",
                   " Bobcats", " Thundering Herd", " Saints",
                   " Owls", " Knights", " Bears", " Terriers",
                   " Retrievers", " Lancers", " Sharks",
                   " Paladins", " Kangaroos", " Royals",
                   " Lumberjacks", " Wave", " Razorbacks",
                   " Rainbow Warriors", " Penguins", " Lions",
                   " Hoyas", " Hawks", " Highlanders", " Nittany Lions",
                   " Catamounts", " Musketeers", " Boilermakers",
                   " Longhorns", " Wolfpack", " Dons", " Pilots",
                   " Miners", " Bearcats", " Hawkeyes", " Orangemen",
                   " Demon Deacons", " Hokies", " Seminoles",
                   " Yellow Jackets", " Eagles", " Sun Devils",
                   " Beavers", " Badgers", " Hoosiers", " Sooners",
                   " Peacocks", " Friars", " Red Foxes", " Flames",
                   " Tribe", " Monarchs", " Dukes", " Explorers",
                   " Quakers", " Stags"]:
        if espn_name.endswith(suffix):
            return espn_name[:-len(suffix)]
    return espn_name


def fetch_espn_results():
    """Fetch completed NCAA tournament games from ESPN."""
    results = {}  # game_id -> winner_name

    # Check all tournament dates
    dates = []
    for month, days in [(3, range(17, 30)), (4, range(1, 8))]:
        for day in days:
            dates.append(f"2026{month:02d}{day:02d}")

    for date_str in dates:
        try:
            url = ESPN_SCOREBOARD.format(date=date_str)
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
        except Exception:
            continue

        for event in data.get("events", []):
            status = event.get("status", {}).get("type", {}).get("name", "")
            if status != "STATUS_FINAL":
                continue

            competitors = event.get("competitions", [{}])[0].get("competitors", [])
            winner = None
            loser = None
            for c in competitors:
                team_name = normalize_name(c.get("team", {}).get("displayName", ""))
                seed = c.get("curatedRank", {}).get("current", 0)
                if not seed:
                    # Try alternate seed location
                    seed = c.get("team", {}).get("seed", "")
                if c.get("winner"):
                    winner = {"name": team_name, "seed": str(seed)}
                else:
                    loser = {"name": team_name, "seed": str(seed)}

            if winner and loser:
                # Try to match to a game ID
                game_id = match_game(winner["name"], loser["name"])
                if game_id:
                    results[game_id] = {
                        "winner": winner["name"],
                        "loser": loser["name"],
                        "winner_seed": winner["seed"],
                        "loser_seed": loser["seed"],
                        "round": GAMES[game_id][0],
                    }

    return results


def match_game(winner, loser):
    """Match a completed game to a game ID based on the teams involved."""
    teams = {winner, loser}

    # Build lookup from game matchups
    game_teams = {
        "FF1": {"UMBC", "Howard"}, "FF2": {"Prairie View A&M", "Lehigh"},
        "FF3": {"Texas", "NC State"}, "FF4": {"Miami (OH)", "SMU"},
        "E1": {"Duke", "Siena"}, "E2": {"Ohio State", "TCU"},
        "E3": {"St. John's", "Northern Iowa"}, "E4": {"Kansas", "Cal Baptist"},
        "E5": {"Louisville", "South Florida"}, "E6": {"Michigan State", "North Dakota State"},
        "E7": {"UCLA", "UCF"}, "E8": {"UConn", "Furman"},
        "S1": {"Florida"}, "S2": {"Clemson", "Iowa"},
        "S3": {"Vanderbilt", "McNeese"}, "S4": {"Nebraska", "Troy"},
        "S5": {"North Carolina", "VCU"}, "S6": {"Illinois", "Penn"},
        "S7": {"Saint Mary's", "Texas A&M"}, "S8": {"Houston", "Idaho"},
        "MW1": {"Michigan"}, "MW2": {"Georgia", "Saint Louis"},
        "MW3": {"Texas Tech", "Akron"}, "MW4": {"Alabama", "Hofstra"},
        "MW5": {"Tennessee"}, "MW6": {"Virginia", "Wright State"},
        "MW7": {"Kentucky", "Santa Clara"}, "MW8": {"Iowa State", "Tennessee State"},
        "W1": {"Arizona", "Long Island"}, "W2": {"Villanova", "Utah State"},
        "W3": {"Wisconsin", "High Point"}, "W4": {"Arkansas", "Hawaii"},
        "W5": {"BYU"}, "W6": {"Gonzaga", "Kennesaw State"},
        "W7": {"Miami (FL)", "Missouri"}, "W8": {"Purdue", "Queens"},
    }

    # First try exact match for R64 / First Four games
    for gid, gt in game_teams.items():
        if teams == gt or (len(gt) == 1 and gt.issubset(teams)):
            return gid

    # For later rounds, check if both teams appear somewhere and we haven't matched yet
    # This is handled by tracking which R64 winners feed into R32, etc.
    # For simplicity, we'll match by checking if either team is a known participant
    return None


# =====================================================
# SCORING
# =====================================================
def score_entries(results):
    """Score all entries against actual results. Returns dict of entry -> scores."""
    scores = {}
    for entry_name, picks in PICKS.items():
        # [r64_ff, r32, s16, e8, ff, chip, total]
        round_scores = [0, 0, 0, 0, 0, 0, 0]
        for game_id, result in results.items():
            rnd = result["round"]
            pts = POINTS[rnd]
            idx = ROUND_INDEX[rnd]
            if picks.get(game_id) == result["winner"]:
                round_scores[idx] += pts
                round_scores[6] += pts
        scores[entry_name] = round_scores
    return scores


def get_eliminated_champs(results):
    """Figure out which champion picks are still alive."""
    champs = {"Arizona", "Duke", "Houston", "UConn"}
    eliminated = set()
    for game_id, result in results.items():
        loser = result["loser"]
        if loser in champs:
            eliminated.add(loser)
    status = {}
    for c in champs:
        status[c] = c not in eliminated
    return status


# =====================================================
# HTML GENERATION
# =====================================================
def build_html(scores, results, champ_status):
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    games_played = len(results)
    games_left = 67 - games_played

    # Sort entries by total score desc
    sorted_entries = sorted(scores.items(), key=lambda x: (-x[1][6], x[0]))

    # Build results list for recent games
    results_html = ""
    if results:
        recent = sorted(results.items(), key=lambda x: list(GAMES.keys()).index(x[0]), reverse=True)
        for game_id, r in recent[:16]:
            correct_count = sum(1 for e in PICKS.values() if e.get(game_id) == r["winner"])
            rnd_short = {"First Four":"FF","Round of 64":"R64","Round of 32":"R32",
                         "Sweet 16":"S16","Elite 8":"E8","Final Four":"FF","Championship":"CHIP"}[r["round"]]
            results_html += f'''<div class="result-row">
        <span class="result-winner"><span class="result-seed">({r["winner_seed"]})</span>{r["winner"]}</span>
        <span class="result-loser">def. <span class="result-seed">({r["loser_seed"]})</span>{r["loser"]}</span>
        <span class="result-round">{rnd_short}</span>
        <span class="result-correct">{correct_count}/12 correct</span>
      </div>'''
    else:
        results_html = '<div class="no-results">No games played yet. First tip-off March 19.</div>'

    # Build leaderboard rows
    rows_html = ""
    prev_score = None
    rank = 0
    for i, (name, s) in enumerate(sorted_entries):
        if s[6] != prev_score:
            rank = i + 1
            prev_score = s[6]
        meta = ENTRY_META[name]
        champ = meta["champ"]
        alive = champ_status.get(champ, True)
        champ_class = "champ-alive" if alive else "champ-dead"
        rank_class = f"rank-{rank}" if rank <= 3 else ""
        rows_html += f'''<tr>
      <td class="rank {rank_class}">{rank}</td>
      <td><div class="entry-name"><a href="{meta['url']}" target="_blank">{name}</a></div><div class="entry-tool">{meta['tool']}</div></td>
      <td><span class="champ {champ_class}">{champ}</span></td>
      <td class="pts pts-total">{s[6]}</td>
      <td class="pts-round round-cols">{s[0]}</td>
      <td class="pts-round round-cols">{s[1]}</td>
      <td class="pts-round round-cols">{s[2]}</td>
      <td class="pts-round round-cols">{s[3]}</td>
      <td class="pts-round round-cols">{s[4]}</td>
      <td class="pts-round round-cols">{s[5]}</td>
    </tr>'''

    leader = sorted_entries[0][0] if games_played > 0 else "--"
    leader_style = 'style="font-size:16px"' if games_played > 0 else ""
    status_text = f"{games_played} of 67 games complete" if games_played > 0 else "Tournament starts March 19"

    return HTML_TEMPLATE.format(
        last_updated=now,
        games_played=games_played,
        games_left=games_left,
        leader_name=leader,
        leader_style=leader_style,
        status_text=status_text,
        leaderboard_rows=rows_html,
        results_html=results_html,
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vet AI Bracket Challenge 2026</title>
<style>
  :root {{
    --bg: #132e3b;
    --card: #1a3f50;
    --border: #245568;
    --text: #f0ece6;
    --muted: #8fb5c4;
    --accent: #e8862c;
    --green: #4dd88a;
    --red: #ef6b5b;
    --blue: #5ba8d6;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
  }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 24px 16px; }}
  .header {{ text-align: center; margin-bottom: 32px; }}
  .header-img {{ width: 100%; max-width: 960px; border-radius: 12px; margin-bottom: 16px; }}
  .header .sub {{ color: var(--muted); font-size: 14px; margin-bottom: 16px; }}
  .header .sub a {{ color: var(--accent); text-decoration: none; }}
  .header .sub a:hover {{ text-decoration: underline; }}
  .badge {{ display: inline-block; background: var(--card); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-size: 12px; color: var(--muted); font-weight: 500; }}
  .badge .live {{ color: var(--green); }}
  .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 24px; }}
  .stat {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; text-align: center; }}
  .stat .num {{ font-size: 24px; font-weight: 700; color: var(--accent); }}
  .stat .label {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }}
  .board {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; margin-bottom: 24px; }}
  .board-header {{ padding: 16px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }}
  .board-header h2 {{ font-size: 16px; font-weight: 600; }}
  .board-header .toggle {{ font-size: 12px; cursor: pointer; background: none; border: 1px solid var(--border); padding: 4px 10px; border-radius: 6px; color: var(--text); }}
  .board-header .toggle:hover {{ border-color: var(--muted); }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--muted); font-weight: 600; padding: 10px 12px; text-align: left; border-bottom: 1px solid var(--border); white-space: nowrap; }}
  thead th.num {{ text-align: center; }}
  tbody td {{ padding: 12px; border-bottom: 1px solid var(--border); font-size: 14px; }}
  tbody tr:last-child td {{ border-bottom: none; }}
  tbody tr:hover {{ background: rgba(255,255,255,0.04); }}
  .rank {{ font-weight: 700; color: var(--muted); width: 36px; text-align: center; }}
  .rank-1 {{ color: var(--accent); }}
  .rank-2 {{ color: #c0c0c0; }}
  .rank-3 {{ color: #cd7f32; }}
  .entry-name {{ font-weight: 600; }}
  .entry-name a {{ color: var(--text); text-decoration: none; }}
  .entry-name a:hover {{ color: var(--accent); }}
  .entry-tool {{ font-size: 12px; color: var(--muted); }}
  .champ {{ font-size: 12px; color: var(--muted); }}
  .champ-alive {{ color: var(--green); }}
  .champ-dead {{ color: var(--red); text-decoration: line-through; }}
  .pts {{ font-weight: 700; text-align: center; font-variant-numeric: tabular-nums; }}
  .pts-total {{ font-size: 18px; color: var(--accent); }}
  .pts-round {{ font-size: 13px; color: var(--muted); text-align: center; }}
  .round-cols {{ display: none; }}
  .round-cols.show {{ display: table-cell; }}
  .results {{ background: var(--card); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; margin-bottom: 24px; }}
  .results-header {{ padding: 16px 20px; border-bottom: 1px solid var(--border); }}
  .results-header h2 {{ font-size: 16px; font-weight: 600; }}
  .result-row {{ display: flex; align-items: center; padding: 10px 20px; border-bottom: 1px solid var(--border); font-size: 14px; }}
  .result-row:last-child {{ border-bottom: none; }}
  .result-winner {{ font-weight: 600; flex: 1; }}
  .result-loser {{ color: var(--muted); flex: 1; }}
  .result-seed {{ font-size: 11px; color: var(--muted); margin-right: 4px; }}
  .result-round {{ font-size: 11px; color: var(--muted); background: var(--bg); padding: 2px 8px; border-radius: 4px; margin-left: auto; }}
  .result-correct {{ font-size: 12px; color: var(--green); margin-left: 12px; white-space: nowrap; }}
  .no-results {{ padding: 40px 20px; text-align: center; color: var(--muted); font-size: 14px; }}
  .footer {{ text-align: center; color: var(--muted); font-size: 12px; padding: 20px 0; }}
  .footer a {{ color: var(--accent); text-decoration: none; }}
  @media (max-width: 640px) {{
    .stats {{ grid-template-columns: repeat(2, 1fr); }}
    table {{ font-size: 13px; }}
    thead th, tbody td {{ padding: 8px 6px; }}
    .hide-mobile {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="container">
<div class="header">
  <img src="header.png" alt="The Bird Bath presents: Veterinary AI Bracket Challenge" class="header-img">
  <div class="sub">12 vet AI companies. 67 games. One bracket to rule them all.<br>A <a href="https://thebirdbathvet.substack.com" target="_blank">Bird Bath</a> production.</div>
  <div class="badge"><span class="live">&#9679;</span> {status_text}</div>
</div>
<div class="stats">
  <div class="stat"><div class="num">{games_played}</div><div class="label">Games Played</div></div>
  <div class="stat"><div class="num">{games_left}</div><div class="label">Games Left</div></div>
  <div class="stat"><div class="num" {leader_style}>{leader_name}</div><div class="label">Current Leader</div></div>
  <div class="stat"><div class="num">192</div><div class="label">Max Possible</div></div>
</div>
<div class="board">
  <div class="board-header">
    <h2>Leaderboard</h2>
    <button class="toggle" onclick="toggleRounds()">Show Round Breakdown</button>
  </div>
  <div style="overflow-x:auto;">
  <table>
    <thead>
      <tr>
        <th class="num">#</th>
        <th>Entry</th>
        <th>Champion</th>
        <th class="num">Score</th>
        <th class="num round-cols">R64</th>
        <th class="num round-cols">R32</th>
        <th class="num round-cols">S16</th>
        <th class="num round-cols">E8</th>
        <th class="num round-cols">FF</th>
        <th class="num round-cols">Ship</th>
      </tr>
    </thead>
    <tbody>{leaderboard_rows}</tbody>
  </table>
  </div>
</div>
<div class="results">
  <div class="results-header"><h2>Recent Results</h2></div>
  <div>{results_html}</div>
</div>
<div class="footer">
  Updated {last_updated} &middot; <a href="https://thebirdbathvet.substack.com" target="_blank">The Bird Bath</a> &middot; <a href="https://first100.io" target="_blank">First 100</a>
</div>
</div>
<script>
let roundsVisible = false;
function toggleRounds() {{
  roundsVisible = !roundsVisible;
  document.querySelectorAll('.round-cols').forEach(el => el.classList.toggle('show', roundsVisible));
  document.querySelector('.toggle').textContent = roundsVisible ? 'Hide Round Breakdown' : 'Show Round Breakdown';
}}
</script>
</body>
</html>"""


# =====================================================
# MAIN
# =====================================================
if __name__ == "__main__":
    print("Fetching ESPN results...")
    results = fetch_espn_results()
    print(f"  Found {len(results)} completed games")

    print("Scoring entries...")
    scores = score_entries(results)
    champ_status = get_eliminated_champs(results)

    # Print leaderboard to console
    sorted_entries = sorted(scores.items(), key=lambda x: (-x[1][6], x[0]))
    print("\nLeaderboard:")
    for i, (name, s) in enumerate(sorted_entries):
        print(f"  {i+1}. {name}: {s[6]} pts")

    print("\nBuilding HTML...")
    html = build_html(scores, results, champ_status)
    with open("index.html", "w") as f:
        f.write(html)
    print("  index.html updated")

    # Print any results
    if results:
        print("\nResults:")
        for gid, r in results.items():
            correct = sum(1 for e in PICKS.values() if e.get(gid) == r["winner"])
            print(f"  {gid}: {r['winner']} def. {r['loser']} ({correct}/12 correct)")

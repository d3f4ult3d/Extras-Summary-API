"""
data.py — In-memory data store. Replaces the database entirely.

All services import directly from here.
To change match data, edit this file.
"""

MATCHES = {
    "IPL-2025-M42": {
        "id":         1,
        "match_code": "IPL-2025-M42",
        "home_team":  "Mumbai Indians",
        "away_team":  "Chennai Super Kings",
        "venue":      "Wankhede Stadium, Mumbai",
        "match_type": "T20",
        "status":     "live",
    },
    "IPL-2025-M43": {
        "id":         2,
        "match_code": "IPL-2025-M43",
        "home_team":  "Royal Challengers Bangalore",
        "away_team":  "Kolkata Knight Riders",
        "venue":      "M. Chinnaswamy Stadium, Bangalore",
        "match_type": "T20",
        "status":     "completed",
    },
}

INNINGS = {
    # match_id → list of innings
    1: [
        {
            "id":             1,
            "match_id":       1,
            "innings_number": 1,
            "batting_team":   "Mumbai Indians",
            "bowling_team":   "Chennai Super Kings",
            "status":         "in_progress",
        }
    ],
    2: [
        {
            "id":             2,
            "match_id":       2,
            "innings_number": 1,
            "batting_team":   "Royal Challengers Bangalore",
            "bowling_team":   "Kolkata Knight Riders",
            "status":         "completed",
        },
        {
            "id":             3,
            "match_id":       2,
            "innings_number": 2,
            "batting_team":   "Kolkata Knight Riders",
            "bowling_team":   "Royal Challengers Bangalore",
            "status":         "completed",
        },
    ],
}

# innings_id → flat lookup
INNINGS_BY_ID = {
    inn["id"]: inn
    for match_innings in INNINGS.values()
    for inn in match_innings
}

BALL_EVENTS = {
    # innings_id → list of ball events in chronological order
    1: [
        {"over_number": 1, "ball_number": 1, "runs_scored": 0, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 1, "ball_number": 2, "runs_scored": 4, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 1, "ball_number": 2, "runs_scored": 0, "extras": 1, "extra_type": "wide",    "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 1, "ball_number": 3, "runs_scored": 1, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 2, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 1, "ball_number": 4, "runs_scored": 6, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 1, "ball_number": 5, "runs_scored": 0, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 2, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 1, "ball_number": 6, "runs_scored": 2, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 2, "ball_number": 1, "runs_scored": 0, "extras": 0, "extra_type": None,      "is_wicket": True,  "batsman_id": 2, "bowler_id": 11, "fielder_id": 13,   "notes": "Top edge, diving catch behind the stumps", "wicket_type": "caught",  "batsman_name": "Ishan Kishan",       "bowler_name": "Deepak Chahar",  "fielder_name": "MS Dhoni"},
        {"over_number": 2, "ball_number": 2, "runs_scored": 4, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 3, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 2, "ball_number": 3, "runs_scored": 1, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 2, "ball_number": 3, "runs_scored": 0, "extras": 1, "extra_type": "no_ball", "is_wicket": False, "batsman_id": 3, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 2, "ball_number": 4, "runs_scored": 0, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 3, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 2, "ball_number": 5, "runs_scored": 6, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 2, "ball_number": 6, "runs_scored": 1, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 3, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 3, "ball_number": 1, "runs_scored": 0, "extras": 2, "extra_type": "bye",     "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 3, "ball_number": 2, "runs_scored": 0, "extras": 1, "extra_type": "leg_bye", "is_wicket": False, "batsman_id": 3, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 3, "ball_number": 3, "runs_scored": 4, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 3, "ball_number": 4, "runs_scored": 1, "extras": 0, "extra_type": None,      "is_wicket": True,  "batsman_id": 3, "bowler_id": 10, "fielder_id": 14,   "notes": "Direct hit from mid-on",              "wicket_type": "run_out", "batsman_name": "Suryakumar Yadav",   "bowler_name": None,             "fielder_name": "Ruturaj Gaikwad"},
        {"over_number": 3, "ball_number": 5, "runs_scored": 0, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 4, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 3, "ball_number": 6, "runs_scored": 6, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 1, "bowler_id": 10, "fielder_id": None, "notes": None},
        {"over_number": 4, "ball_number": 1, "runs_scored": 0, "extras": 5, "extra_type": "penalty", "is_wicket": False, "batsman_id": 1, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 4, "ball_number": 2, "runs_scored": 1, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 4, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 4, "ball_number": 3, "runs_scored": 0, "extras": 0, "extra_type": None,      "is_wicket": True,  "batsman_id": 1, "bowler_id": 11, "fielder_id": None, "notes": "Yorker, knocked middle stump",         "wicket_type": "bowled",  "batsman_name": "Rohit Sharma",       "bowler_name": "Ravindra Jadeja", "fielder_name": None},
        {"over_number": 4, "ball_number": 4, "runs_scored": 4, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 5, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 4, "ball_number": 5, "runs_scored": 1, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 4, "bowler_id": 11, "fielder_id": None, "notes": None},
        {"over_number": 4, "ball_number": 6, "runs_scored": 6, "extras": 0, "extra_type": None,      "is_wicket": False, "batsman_id": 5, "bowler_id": 11, "fielder_id": None, "notes": None},
    ],
}

BATTING_SCORECARDS = {
    # innings_id → list of batter rows
    1: [
        {"player_id": 1, "player_name": "Rohit Sharma",      "is_out": True},
        {"player_id": 2, "player_name": "Ishan Kishan",       "is_out": True},
        {"player_id": 3, "player_name": "Suryakumar Yadav",   "is_out": True},
        {"player_id": 4, "player_name": "Hardik Pandya",      "is_out": False},
        {"player_id": 5, "player_name": "Tilak Varma",        "is_out": False},
    ],
}

BOWLING_SCORECARDS = {
    # innings_id → list of bowler rows
    1: [
        {"player_id": 10, "player_name": "Deepak Chahar"},
        {"player_id": 11, "player_name": "Ravindra Jadeja"},
    ],
}
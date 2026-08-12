from datetime import datetime
# Government coalitions and opposition parties in Berlin parliament for different time periods

# COALITION_TYPE
# "aligned" → ideologically close (e.g., SPD + LINKE, CDU + FDP)
# "cross_ideological" → big tent (e.g., SPD + CDU)
# "left_coalition" → SPD + GRÜNE + LINKE
# "mixed" → unclear / broad

# Define election years
ELECTION_YEARS = {
    'berlin': [1990, 1995, 1999, 2001, 2006, 2011, 2016, 2021, 2023],
    'brandenburg': [1990, 1994, 1999, 2004, 2009, 2014, 2019],
    'baden-württemberg': [1992, 1996, 2001, 2006, 2011, 2016, 2021]
}

passed_bills_activities_berlin = ['Gesetz- und Verordnungsblatt', 'Bekanntmachung (Gesetz- und Verordnungsblatt)']
passed_bills_activities_bawue = ["Gesetz", "Gesetzblatt für Baden-Württemberg"]
passed_bills_activities_brandenburg = ["Gesetz", "Gesetz- und Verordnungsblatt"]
POSSIBLE_PASSED_BILL_ACTIVITIES = passed_bills_activities_berlin + passed_bills_activities_bawue + passed_bills_activities_brandenburg


# change to Wahltage?
BERLIN_COALITIONS = {
    "31.05.1990": {
        "government": ["SPD", "CDU"],
        "opposition": ["GRÜNE", "DIE LINKE", "FDP"],
        "agreement_score_file": "agreement_scores_berlin_projection_1990-05-31.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 177,
        "opposition_seats": 64
    },
    "30.11.1995": {
        "government": ["SPD", "CDU"],
        "opposition": ["GRÜNE", "DIE LINKE"],
        "agreement_score_file": "agreement_scores_berlin_projection_1995-11-30.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 142,
        "opposition_seats": 64
    },
    "18.11.1999": {
        "government": ["SPD", "CDU", "GRÜNE"],
        "opposition": ["DIE LINKE"],
        "agreement_score_file": "agreement_scores_berlin_projection_1999-11-18.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 118,
        "opposition_seats": 51
    },
    "29.11.2001": {
        "government": ["SPD", "DIE LINKE"],
        "opposition": ["CDU", "GRÜNE", "FDP"],
        "agreement_score_file": "agreement_scores_berlin_projection_2001-11-29.csv",
        "coalition_type": "aligned",
        "government_seats": 77,
        "opposition_seats": 64
    },
    "26.10.2006": {
        "government": ["SPD", "DIE LINKE"],
        "opposition": ["CDU", "GRÜNE", "FDP"],
        "agreement_score_file": "agreement_scores_berlin_projection_2006-10-26.csv",
        "coalition_type": "aligned",
        "government_seats": 76,
        "opposition_seats": 73
    },
    "27.10.2011": {
        "government": ["SPD", "CDU"],
        "opposition": ["GRÜNE", "DIE LINKE", "PIRATEN"],
        "agreement_score_file": "agreement_scores_berlin_projection_2011-10-27.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 86,
        "opposition_seats": 63
    },
    "27.10.2016": {
        "government": ["SPD", "GRÜNE", "DIE LINKE"],
        "opposition": ["CDU", "AfD", "FDP"],
        "agreement_score_file": "agreement_scores_berlin_projection_2016-10-27.csv",
        "coalition_type": "aligned",
        "government_seats": 92,
        "opposition_seats": 68
    },
    "04.11.2021": {
        "government": ["SPD", "GRÜNE", "DIE LINKE"],
        "opposition": ["CDU", "AfD", "FDP"],
        "agreement_score_file": "agreement_scores_berlin_projection_2021-11-04.csv",
        "coalition_type": "aligned",
        "government_seats": 92,
        "opposition_seats": 55
    },
    "16.03.2023": {
        "government": ["CDU", "SPD"],
        "opposition": ["GRÜNE", "AfD", "DIE LINKE"],
        "agreement_score_file": "agreement_scores_berlin_projection_2023-03-16.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 86,
        "opposition_seats": 73
    },
}

BERLIN_COALITIONS_SORTED = sorted(
    ((datetime.strptime(d, "%d.%m.%Y"), v) 
     for d, v in BERLIN_COALITIONS.items()),
    key=lambda x: x[0]
)

BERLIN_ELECTION_PERIODS_START_DATES = [
    d for d, _ in BERLIN_COALITIONS_SORTED
]

# Government coalitions and opposition parties in Baden-Württemberg parliament
BADEN_WUERTTEMBERG_COALITIONS = {
    "01.06.1984": {
        "government": ["CDU"],
        "opposition": ["GRÜNE", "SPD", "FDP"],
        "agreement_score_file": "agreement_scores_bawue_projection_1984-06-01.csv",
        "coalition_type": "aligned"
    },
    "01.06.1988": {
        "government": ["CDU"],
        "opposition": ["GRÜNE", "SPD", "FDP"],
        "agreement_score_file": "agreement_scores_bawue_projection_1988-06-01.csv",
        "coalition_type": "aligned"
    },
    "01.06.1992": {
        "government": ["CDU", "SPD"],
        "opposition": ["GRÜNE", "FDP", "REP"], # TODO: REP are not in the WahlOMat data
        "agreement_score_file": "agreement_scores_bawue_projection_1992-06-01.csv",
        "coalition_type": "cross_ideological"
    },
    "01.06.1996": {
        "government": ["CDU", "FDP"],
        "opposition": ["GRÜNE", "SPD", "REP"], # TODO: REP are not in the WahlOMat data
        "agreement_score_file": "agreement_scores_bawue_projection_1996-06-01.csv",
        "coalition_type": "aligned"
    },
    "01.06.2001": {
        "government": ["CDU", "FDP"],
        "opposition": ["GRÜNE", "SPD"],
        "agreement_score_file": "agreement_scores_bawue_projection_2001-06-01.csv",
        "coalition_type": "aligned"
    },
    "01.06.2006": {
        "government": ["CDU", "FDP"],
        "opposition": ["GRÜNE", "SPD"],
        "agreement_score_file": "agreement_scores_bawue_projection_2006-06-01.csv",
        "coalition_type": "aligned"
    },
    "01.05.2011": {
        "government": ["GRÜNE", "SPD"],
        "opposition": ["CDU", "FDP"],
        "agreement_score_file": "agreement_scores_bawue_projection_2011-05-01.csv",
        "coalition_type": "aligned"
    },
    "01.05.2016": {
        "government": ["GRÜNE", "CDU"],
        "opposition": ["SPD", "FDP", "AfD"],
        "agreement_score_file": "agreement_scores_bawue_projection_2016-05-01.csv",
        "coalition_type": "cross_ideological" # is it though??
    },
    "01.05.2021": {
        "government": ["GRÜNE", "CDU"],
        "opposition": ["SPD", "FDP", "AfD"],
        "agreement_score_file": "agreement_scores_bawue_projection_2021-05-01.csv",
        "coalition_type": "cross_ideological" # is it though??
    },
}

BADEN_WUERTTEMBERG_COALITIONS_SORTED = sorted(
    ((datetime.strptime(d, "%d.%m.%Y"), v)
     for d, v in BADEN_WUERTTEMBERG_COALITIONS.items()),
    key=lambda x: x[0]
)


BAWUE_ELECTION_PERIODS_START_DATES = [
    d for d, _ in BADEN_WUERTTEMBERG_COALITIONS_SORTED
]

# Government coalitions and opposition parties in Brandenburg parliament
BRANDENBURG_COALITIONS = {
    "26.10.1990": {
        "government": ["SPD", "FDP", "GRÜNE"], # TODO: actually Bündnis 90 not Grüne ...
        "opposition": ["CDU", "DIE LINKE"],
        "agreement_score_file": "agreement_scores_brandenburg_projection_1990-10-26.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 48,
        "opposition_seats": 40
    },
    "11.10.1994": {
        "government": ["SPD"], 
        "opposition": ["CDU", "DIE LINKE"],
        "agreement_score_file": "agreement_scores_brandenburg_projection_1994-10-11.csv",
        "coalition_type": "aligned",
        "government_seats": 52,
        "opposition_seats": 36
    },
    "29.09.1999": {
        "government": ["SPD", "CDU"], 
        "opposition": ["DIE LINKE", "DVU"],
        "agreement_score_file": "agreement_scores_brandenburg_projection_1999-09-29.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 62,
        "opposition_seats": 27
    },
    "13.10.2004": {
        "government": ["SPD", "CDU"], 
        "opposition": ["DIE LINKE", "DVU"], 
        "agreement_score_file": "agreement_scores_brandenburg_projection_2004-10-13.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 53,
        "opposition_seats": 35
    },
    "21.10.2009": {
        "government": ["SPD", "DIE LINKE"],
        "opposition": ["CDU", "FDP", "GRÜNE"],
        "agreement_score_file": "agreement_scores_brandenburg_projection_2009-10-21.csv",
        "coalition_type": "aligned",
        "government_seats": 57,
        "opposition_seats": 31
    },
    "08.10.2014": {
        "government": ["SPD", "DIE LINKE"],
        "opposition": ["CDU", "GRÜNE", "AfD", "FREIE WÄHLER"],
        "agreement_score_file": "agreement_scores_brandenburg_projection_2014-10-08.csv",
        "coalition_type": "aligned",
        "government_seats": 47,
        "opposition_seats": 41
    },
    "25.09.2019": {
        "government": ["SPD", "CDU", "GRÜNE"],
        "opposition": ["DIE LINKE", "AfD", "FREIE WÄHLER"],
        "agreement_score_file": "agreement_scores_brandenburg_projection_2019-09-25.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 50,
        "opposition_seats": 38
    },
    "17.10.2024": {
        "government": ["SPD", "BSW"],
        "opposition": ["AfD", "CDU"],
        "agreement_score_file": "agreement_scores_brandenburg_projection_2024-10-17.csv",
        "coalition_type": "cross_ideological",
        "government_seats": 46,
        "opposition_seats": 42
    },
}

BRANDENBURG_COALITIONS_SORTED = sorted(
    ((datetime.strptime(d, "%d.%m.%Y"), v)
     for d, v in BRANDENBURG_COALITIONS.items()),
    key=lambda x: x[0]
)


BRANDENBURG_ELECTION_PERIODS_START_DATES = [
    d for d, _ in BRANDENBURG_COALITIONS_SORTED
]
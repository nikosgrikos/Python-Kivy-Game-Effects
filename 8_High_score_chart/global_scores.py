# Monkey Buster 2048 Tutorial Part 8 (See video on YouTube)
# High score chart
# This code displays a high score chart, saves/updates a high score
import json
import requests
from plyer import uniqueid

# ------------------------------------------------------------------------------------------------------------------

def load_template_from_database(url):
    # Load template
    request = requests.get(url)
    jsonStr = request.json()
    jsonObj = dict(jsonStr)
    device = "Template"
    scoreDict = jsonObj[device]

    return scoreDict

# ------------------------------------------------------------------------------------------------------------------

def get_score_from_database(url, device=None):

    if device:
        id = device
    else:
        id = str(uniqueid.id)

    # Get users score
    request = requests.get(url)
    jsonStr = request.json()
    jsonObj = dict(jsonStr)
    scoreDict = jsonObj[id]

    score = scoreDict["score"]

    return score

# ------------------------------------------------------------------------------------------------------------------

def write_template_to_database(url):

    # Patch this first {"Template": {"country": "None", "score": 0, "name": "Nobody"}}
    JSON = '{"Template2": {"country": "None", "score": 0, "name": "Nobody"}}'
    to_database = json.loads(JSON)
    requests.patch(url=url, json=to_database)

    return

# ------------------------------------------------------------------------------------------------------------------

def write_score_to_database(url, country, score, name, device=None):

    # Example
    # {"Device2": {"country": "Cyprus", "score": 2500, "name": "Ginger"}}

    # Load template
    scoreDict = load_template_from_database(url)

    if device:
        id = device
    else:
        id = str(uniqueid.id)
    scoreDict["country"] = country
    scoreDict["score"] = score
    scoreDict["name"] = name

    JSON = "{" + json.dumps(id) + ":" + json.dumps(scoreDict) + "}"
    to_database = json.loads(JSON)
    requests.patch(url=url, json=to_database)

# ------------------------------------------------------------------------------------------------------------------

def retrieve_top_x_scores_from_database(url, top_x):

    # Returns a list in the following format
    # Country, name, score

    key_value = {}
    details = []
    sorted_scores = []

    request = requests.get(url)
    jsonStr = request.json()
    jsonObj = dict(jsonStr)
    deviceList = list(jsonObj)

    for i in range(0, len(deviceList)):
        device = deviceList[i]
        userDict = jsonObj[device]
        score = userDict["score"]
        country = userDict["country"]
        name = userDict["name"]

        key_value[i] = score
        details.extend([country, name])

    sorted_score_indices = sorted(key_value.items(), reverse=True, key=lambda kv: kv[1])

    max = len(deviceList)
    if max > top_x:
        max = top_x

    for i in range(0, max):
        index, score = sorted_score_indices[i]
        index2 = 2 * index
        if score > 0:
            sorted_scores.extend([details[index2], details[index2 + 1], score])

    return sorted_scores

# ------------------------------------------------------------------------------------------------------------------

def retrieve_top_x_team_scores_from_database(url, top_x_team, top_x):

    # Returns a list in the following format
    # Country, names, score

    key_value = {}
    team = []
    team_score = []
    team_count = []
    team_names = []
    sorted_team_scores = []

    sorted_scores = retrieve_top_x_scores_from_database(url, top_x)

    max_scores = int(len(sorted_scores) / 3)
    for i in range(max_scores):
        k = i * 3

        country = sorted_scores[k]
        name = sorted_scores[k + 1]
        score = sorted_scores[k + 2]

        if country in team:
            index = team.index(country)
        else:
            team.extend([country])
            team_count.extend([0])
            team_score.extend([0])
            team_names.extend([name])
            index = team.index(country)

        if team_count[index] < 4:
            team_count[index] += 1
            team_score[index] += score
            if team_count[index] > 1:
                team_names[index] += ', ' + name

    for j in range(len(team_score)):
        key_value[j] = team_score[j]

    sorted_score_indices = sorted(key_value.items(), reverse=True, key=lambda kv: kv[1])

    max = len(team_score)
    if max > top_x_team:
        max = top_x_team

    for i in range(0, max):
        index, score = sorted_score_indices[i]
        if score > 0:
            sorted_team_scores.extend([team[index], team_names[index], score])

    return sorted_team_scores

# ------------------------------------------------------------------------------------------------------------------

import yaml
import time
import datetime
import argparse
from httpx import Client


class UserInfo:
    def __init__(self):
        self.login_data = None
        self.cookie = None
        self.csrf_token = None


user_info = UserInfo()
client = Client()
parsed_info = yaml.safe_load(open("info.yaml"))


def login(oncall_url, username, password):
    user_info.login_data = {"username": username, "password": password}
    response = client.post(f"{oncall_url}/login", data=user_info.login_data)
    user_info.cookie = response.cookies
    user_info.csrf_token = {"x-csrf-token": response.json()["csrf_token"]}
    return response.json()


def create_teams(oncall_url):
    result = {}
    teams = parsed_info["teams"]
    for team in teams:
        response = client.post(
            f"{oncall_url}/api/v0/teams/",
            json=team,
            cookies=user_info.cookie,
            headers=user_info.csrf_token,
        )
        result[team["name"]] = response.status_code
    return result


def create_rosters(oncall_url):
    result = {}
    teams = parsed_info["teams"]
    for team in teams:
        response = client.post(
            f"{oncall_url}/api/v0/teams/{team['name']}/rosters/",
            json={"name": f'roster_{team["name"]}'},
            cookies=user_info.cookie,
            headers=user_info.csrf_token,
        )
        result[team["name"]] = response.status_code
    return result


def add_rosters_users(oncall_url):
    result = {}
    teams = parsed_info["teams"]
    for team in teams:
        for user in team["users"]:
            response = client.post(
                f"{oncall_url}/api/v0/teams/{team['name']}/rosters/roster_{team['name']}/users",
                json={"name": user["name"]},
                cookies=user_info.cookie,
                headers=user_info.csrf_token,
            )
            result[user["name"]] = response.json()
    return result


def update_contacts(oncall_url):
    result = {}
    teams = parsed_info["teams"]
    for team in teams:
        users = team["users"]
        new_users = {}
        for user in users:
            new_users["contacts"] = {
                "call": user["phone_number"],
                "email": user["email"],
                "sms": user["phone_number"],
            }
            new_users["name"] = user["name"]
            new_users["full_name"] = user["full_name"]
            response = client.put(
                f"{oncall_url}/api/v0/users/{user['name']}",
                json=new_users,
                cookies=user_info.cookie,
                headers=user_info.csrf_token,
            )
            result[user["name"]] = response.text
    return result


def create_users(oncall_url):
    result = {}
    teams = parsed_info["teams"]
    for team in teams:
        for user in team["users"]:
            response = client.post(
                f"{oncall_url}/api/v0/users",
                json={"name": user["name"]},
                cookies=user_info.cookie,
                headers=user_info.csrf_token,
            )
            result[user["name"]] = response.status_code
    return result


def create_events(oncall_url):
    result = []
    teams = parsed_info["teams"]
    for team in teams:
        users = team["users"]
        for user in users:
            for duty in user["duty"]:
                start = int(
                    time.mktime(
                        datetime.datetime.strptime(duty["date"], "%d/%m/%Y").timetuple()
                    )
                )
                end = start + 86400  #  прибавляем cутки
                event_info = {
                    "role": duty["role"],
                    "user": user["name"],
                    "team": team["name"],
                    "start": start,
                    "end": end,
                }
                response = client.post(
                    f"{oncall_url}/api/v0/events",
                    json=event_info,
                    cookies=user_info.cookie,
                    headers=user_info.csrf_token,
                )
                result.append(response.text)
    return result


def main(args):
    login(args.oncall, args.username, args.password)
    create_teams(args.oncall)
    create_rosters(args.oncall)
    create_users(args.oncall)
    update_contacts(args.oncall)
    add_rosters_users(args.oncall)
    create_events(args.oncall)


if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-u", "--username", help="username for login")
    argParser.add_argument("-p", "--password", help="password for login")
    argParser.add_argument(
        "-o", "--oncall", help="url for oncall", default="http://127.0.0.1:8080"
    )
    args = argParser.parse_args()
    main(args)

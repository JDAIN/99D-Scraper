# coding=utf-8
import requests
import bs4
import copy
from datetime import datetime
import pprint


def get_divlinks_dic_from_leaguepage(link):
    # connect
    url = link
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    website = requests.get(url, headers=headers)
    website.raise_for_status()
    # get html
    league_soup = bs4.BeautifulSoup(website.text, features="html.parser")

    divlinks_dic = {}
    league_element = league_soup.select('.league_overview_box .groups li')

    for e in league_element:
        try:
            divlinks_dic[e.text] = {'link': e.a['href']}
        except:
            pass

    return divlinks_dic


def get_teamlinks_dic_from_group(grouplink):
    # connect
    url = grouplink
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    website = requests.get(url, headers=headers)
    website.raise_for_status()
    # get html
    group_soup = bs4.BeautifulSoup(website.text, features="html.parser")

    teamlinks_dic = {}
    league_element = group_soup.select('.league_table td')

    for e in league_element:
        try:
            if e.text:
                teamlinks_dic[e.text.lstrip()] = {'link': e.a['href']}
        except:
            pass
    return teamlinks_dic


def teamdic_change_datestrings_to_timedate_objects(dic):
    '''
    Enter only a teamdic
    param dic
    '''
    # creates new list and replaces the datestring with an datetimeobject
    date_team_dic = copy.deepcopy(dic)

    for key in date_team_dic.keys():
        counterjoin = 0
        counterleave = 0
        for i in date_team_dic[key]['join_dates']:
            date_team_dic[key]['join_dates'][counterjoin] = datetime.strptime(
                i, '%a, %d %b %Y %H:%M:%S %z')
            counterjoin += 1

        for i in date_team_dic[key]['leave_dates']:
            date_team_dic[key]['leave_dates'][counterleave] = datetime.strptime(
                i, '%a, %d %b %Y %H:%M:%S %z')
            counterleave += 1
    # pretty.pprint(date_team_dic)
    return (date_team_dic)


def get_teamdic_from_teamlink(link):
    # enter when the 99dmg season starts, used to check if player was in the team at season start
    # season10 start: https://csgo.99damage.de/de/news/74090-jetzt-anmelden-fuer-die-99damage-liga
    # 99dmg season 10 started at 28. September 2018 (18: 00 Uhr)
    # use as input               28.09.2018 18:00 +0200
    # IMPORTANT TODO change for next season
    dmgseasonstart_datetime = datetime.strptime(
        '28.09.2018 18:00 +0200', '%d.%m.%Y %H:%M %z')
    # connect
    url = link
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    website = requests.get(url, headers=headers)
    website.raise_for_status()
    # get html
    team_soup = bs4.BeautifulSoup(website.text, features="html.parser")

    # {'steam_id': player_steamid, 'join_dates': [], 'leave_dates': [], 'time_in_team': '', 'join_afterSeasonStart': '-', 'leave_afterSeasonStart': '-'}
    team_dic = {}

    teamlog_elements = team_soup.select('#team_log tr td')
    team_log_dates = teamlog_elements[::4]
    team_log_playernames = teamlog_elements[1::4]
    team_log_actions = teamlog_elements[2::4]
    team_log_targets = teamlog_elements[3::4]

    for i in range(len(team_log_targets)):

        join_leave_date_string = team_log_dates[i].find('span')['title']
        teamlog_playername = team_log_playernames[i].text
        teamlog_action = team_log_actions[i].text
        teamlog_target = team_log_targets[i].text
        if teamlog_playername:
            if '(admin)' not in teamlog_playername:
                team_dic.setdefault(teamlog_playername, {
                    'steam_id': '-', 'join_dates': [], 'leave_dates': [], 'time_in_team': '', 'join_afterSeasonStart': False, 'leave_afterSeasonStart': False})
        if teamlog_target:
            team_dic.setdefault(teamlog_target, {
                'steam_id': '-', 'join_dates': [], 'leave_dates': [], 'time_in_team': '', 'join_afterSeasonStart': False, 'leave_afterSeasonStart': False})

        if (teamlog_action == 'member_join' or teamlog_action == 'create') and teamlog_playername:
            team_dic[teamlog_playername]['join_dates'].append(
                join_leave_date_string)
        if (teamlog_action == 'member_leave'):
            if ('(admin)' not in teamlog_playername) and teamlog_playername:
                team_dic[teamlog_playername]['leave_dates'].append(
                    join_leave_date_string)
            elif '(admin)' in teamlog_playername and teamlog_target:
                team_dic[teamlog_target]['leave_dates'].append(
                    join_leave_date_string)
        if (teamlog_action == 'member_kick'):
            if teamlog_target:
                team_dic[teamlog_target]['leave_dates'].append(
                    join_leave_date_string)
        if (teamlog_action == 'member_add'):
            if teamlog_target:
                team_dic[teamlog_target]['join_dates'].append(
                    join_leave_date_string)

    datetime_team_dic = teamdic_change_datestrings_to_timedate_objects(
        team_dic)
    for key in datetime_team_dic.keys():
        for date in datetime_team_dic[key]['join_dates']:
            if date > dmgseasonstart_datetime:
                team_dic[key]['join_afterSeasonStart'] = True
                break
        for date in datetime_team_dic[key]['leave_dates']:
            if date > dmgseasonstart_datetime:
                team_dic[key]['leave_afterSeasonStart'] = True
                break

    # get steamids of active players
    try:
        tables = team_soup.select('table')
        active_team_table = tables[0].select('tr td')

        active_team_playernames = active_team_table[0::3]
        active_team_steamids = active_team_table[2::3]
        for i in range(len(active_team_playernames)):
            if '[log]' in active_team_steamids[i]:
                team_dic[active_team_playernames[i].text]['steam_id'] = active_team_steamids[i].text.split('[', 1)[
                    0]
            else:
                team_dic[active_team_playernames[i].text]['steam_id'] = active_team_steamids[i].text
    except:
        pass

    if len(team_dic) == 0:
        return 'no players, team deleted'
    else:
        return (team_dic)


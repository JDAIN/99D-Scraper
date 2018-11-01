import datasoup_with_teams
import teamscraper
import pprint
import copy
import re
from collections import Counter


def check_if_switched_team_more_than_once():
    '''
    Rule: D. I.
        : Das Wechseln des Teams während einer laufenden Saison ist nur ein Mal erlaubt.
        : Mehrfacher Wechsel führt zur Sperrung des Spielers für die laufende Saison und Playoffs bzw. Relegationen.
    TODO check if in team for less than 24 hrs cause of exception look into
    '''
    joinleave_player_list = []
    for k, v in datasoup_with_teams.dmgdata.items():

        for ks, vs in datasoup_with_teams.dmgdata[k]['Teams'].items():

            if 'no players' not in datasoup_with_teams.dmgdata[k]['Teams'][ks]['Players']:
                for kss, vss in datasoup_with_teams.dmgdata[k]['Teams'][ks]['Players'].items():
                    if vss['join_afterSeasonStart'] or vss['leave_afterSeasonStart']:
                        joinleave_player_list.append(
                            (kss, k, v['link'], ks, vs['link'], vss['join_dates'], vss['leave_dates']))
    # counts the occurance of a playername, with Collections Counter
    player_counter = Counter(x[0] for x in joinleave_player_list)
    for k, v in player_counter.items():
        # k = playername v = amount
        # if player left or joined more than two teams in a season print his data
        if v > 2:
            # get index of the duplicate player items
            indices = [i for i, x in enumerate(
                joinleave_player_list) if x[0] == k]
            print(indices)
            # get the items with the indices from the list with joined or left player
            for e in indices:
                print(joinleave_player_list[e])


def check_lower_div_join():
    '''
    Rule: D. IV.
        : Spieler, die zu Beginn oder im Laufe einer jeden Saison in einem Team einer höheren Division vertreten waren, sind in einer niedrigeren Division nicht spielberechtigt.
        : Dies gilt unabhängig davon, ob bereits ein Match in der höheren Division bestritten wurde. Die Regelung ist auch für die Relegationen gültig.
    '''
    joinleave_player_list = []
    # copys dmgdata
    datasoup_date = copy.deepcopy(datasoup_with_teams.dmgdata)

    for k, v in datasoup_with_teams.dmgdata.items():
        for ks, vs in datasoup_with_teams.dmgdata[k]['Teams'].items():
            # gets only teamdic from dmgdata
            team_dic = datasoup_with_teams.dmgdata[k]['Teams'][ks]['Players']
            # print('%s : %s : %s ' % (k, ks, team_dic.keys()))
            # checks if player is a dic or just the string 'Team deleted'
            if type(datasoup_date[k]['Teams'][ks]['Players']) == dict:
                # changes/updates datestrings in team_dic_date to datetime object for comparission
                datasoup_date[k]['Teams'][ks]['Players'].update(teamscraper.teamdic_change_datestrings_to_timedate_objects(
                    team_dic))

        # TODO MAKE WORK
    for k, v in datasoup_date.items():

        for ks, vs in datasoup_date[k]['Teams'].items():

            if 'no players' not in datasoup_date[k]['Teams'][ks]['Players']:
                for kss, vss in datasoup_date[k]['Teams'][ks]['Players'].items():
                    if vss['join_afterSeasonStart'] or vss['leave_afterSeasonStart']:
                        # joinleave_player_list.append(
                         #   (kss, k, ks, vss['join_dates'], vss['leave_dates'], v['link'], vs['link'], ))
                        if len(vss['leave_dates']) > 0:
                            joinleave_player_list.append(
                                [kss, k, ks, vss['join_dates'][0], vss['leave_dates'][0], v['link'], vs['link']])
                        else:
                            joinleave_player_list.append(
                                [kss, k, ks, vss['join_dates'][0], vss['leave_dates'], v['link'], vs['link']])

    player_counter = Counter(x[0] for x in joinleave_player_list)

    for k, v in player_counter.items():
        # k = playername v = amount
        # if player left or joined more than two teams in a season print his data
        if v > 1:
            # get index of the duplicate player items
            indices = [i for i, x in enumerate(
                joinleave_player_list) if x[0] == k]
            # print(indices)
            # get the items with the indices from the list with joined or left player
            l = []
            for e in indices:
                l.append(joinleave_player_list[e])
                # print(joinleave_player_list[e])
            # print(l)

            # makes new list for players teams sorted after joindate
            sorted_after_joindate = sorted(l, key=lambda x: x[3], reverse=True)

            for i in range(len(sorted_after_joindate)):

                sorted_after_joindate[i][3] = sorted_after_joindate[i][3].strftime(
                    '%a, %d %b %Y %H:%M:%S %z')

                # needed bc if leavedate is a list
                try:
                    sorted_after_joindate[i][4] = sorted_after_joindate[i][4].strftime(
                        '%a, %d %b %Y %H:%M:%S %z')
                except:
                    pass
            first = True
            for e in sorted_after_joindate:

                if 'Starter' not in e[1]:
                    e.append(int(float(e[1].split()[1])))
                else:
                    e.append(int(7))

                if first:
                    first_e = e
                    first = False

                if first_e[-1] > e[-1]:
                    # TODO MAKE OUTPUT READABLE AND USEABLE
                    print('Gefahr')
                    pp = pprint.pformat(sorted_after_joindate,
                                        depth=8, width=500, compact=True)
                    print(pp)
                    print('______')

            # makes timedata object back to strings for readability


# check_lower_div_join()
check_if_switched_team_more_than_once()
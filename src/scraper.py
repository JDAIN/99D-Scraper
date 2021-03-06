# coding=utf-8
import copy
import io
import pprint
import scrap
import json
import time


def scrap_league_and_div_data(link, delay=10):
    '''
    @param link
        provide 99dmg seasonlink e.g 'https://csgo.99damage.de/de/leagues/99dmg/989-saison-10'
    @param delay
        delays the scraper by amount in sec, recommended is 5-10 sec
        default is 10 sec

    creates Dic of all Divisions and Teams and writes Data to py file as dmgdata
    '''
    divlinks_list = scrap.get_divlinks_dic_from_leaguepage(link)

    league_team_data = copy.deepcopy(divlinks_list)
    amount_divs = len(league_team_data)
    counter = 0
    est_runtime_min = round((amount_divs * delay) / 60)
    print('Estimated runtime: %s Minutes (Delay: %ss)' %
          (est_runtime_min, delay))
    for k, v in divlinks_list.items():
        teamlinks_list = scrap.get_teamlinks_dic_from_group(v['link'])
        counter += 1
        league_team_data[k].update({'Teams': teamlinks_list})
        print('(%s/%s) %s sleeping...(%ss)' %
              (str(counter), str(amount_divs), k, str(delay)))
        time.sleep(delay)

    # TODO is it? do not change the filename, is needed for add_teamdata_to_data
    # TODO make changeable in gui
    print('Done Scraping....writing to File....')
    with io.open('teamdata.json', 'w', encoding="utf-8") as file:
        json.dump(league_team_data, file, indent=4)

    print('Done, add Players can now be used')
    # file.write('dmgdata = ' + pprint.pformat(data))


def add_teamdata_to_data(delay=10):
    '''
    @param delay
        delays the scraper by amount in sec, recommended is 5-10 sec
        default: 10 sec
    NEEDS dicfile from scrap_league_and_div_data()
    '''
    try:
        # TODO if name changed in gui change here as well
        with open('teamdata.json') as json_data:
            teamdata = json.load(json_data)
    except FileNotFoundError as err:
        # TODO output on GUI
        print('[ERROR] You need to run the Leaguesraper first    ', err)
        return

    counter = 0
    estTeams = len(teamdata.keys()) * 8
    est_time_min = round((estTeams * delay) / 60)
    print('Estimated Teams: %s  Estimated time: %s Minutes (Delay %ss)' %
          (str(estTeams), str(est_time_min), str(delay)))
    for k, v in teamdata.items():

        print('scraping %s...' % k)
        for ks, vs in teamdata[k]['Teams'].items():
            counter += 1
            players = scrap.get_teamdic_from_teamlink(vs['link'])
            # print(ks + ' sleeping...(' + str(delay) + ')' + '')
            print('(%s/%s) %s | sleeping...(%ss)' %
                  (str(counter), str(estTeams), ks, str(delay)))
            time.sleep(delay)
            teamdata[k]['Teams'][ks].update({'Players': players})
        # after every division write to file,slower can be moved out of for for speed improvment but less stability

        with io.open('team_player_data.json', 'w', encoding="utf-8") as file:
            json.dump(teamdata, file, indent=4)
            print('wrote Data of %s to File' % k)

import schedule
import time
import requests
from bs4 import BeautifulSoup
import json
import csv
from numpy import NaN
import re
from shot_ml import main_ml


HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/94.0.4606.61 Safari/537.36 '
}


# создание списка ссылок на сезоны
SEASONS = [{'name': '08-09_RS', 'url': 'https://www.khl.ru/calendar-line/160/00/'},
           {'name': '08-09_PO', 'url': 'https://www.khl.ru/calendar-line/165/00/'},
           {'name': '09-10_RS', 'url': 'https://www.khl.ru/calendar-line/167/00/'},
           {'name': '09-10_PO', 'url': 'https://www.khl.ru/calendar-line/168/00/'},
           {'name': '10-11_RS', 'url': 'https://www.khl.ru/calendar-line/185/00/'},
           {'name': '10-11_PO', 'url': 'https://www.khl.ru/calendar-line/186/00/'},
           {'name': '11-12_RS', 'url': 'https://www.khl.ru/calendar-line/202/00/'},
           {'name': '11-12_PO', 'url': 'https://www.khl.ru/calendar-line/203/00/'},
           {'name': '12-13_RS', 'url': 'https://www.khl.ru/calendar-line/222/00/'},
           {'name': '12-13_PO', 'url': 'https://www.khl.ru/calendar-line/223/00/'},
           {'name': '13-14_RS', 'url': 'https://www.khl.ru/calendar-line/244/00/'},
           {'name': '13-14_PO', 'url': 'https://www.khl.ru/calendar-line/245/00/'},
           {'name': '14-15_RS', 'url': 'https://www.khl.ru/calendar-line/266/00/'},
           {'name': '14-15_PO', 'url': 'https://www.khl.ru/calendar-line/267/00/'},
           {'name': '15-16_RS', 'url': 'https://www.khl.ru/calendar-line/309/00/'},
           {'name': '15-16_PO', 'url': 'https://www.khl.ru/calendar-line/310/00/'},
           {'name': '16-17_RS', 'url': 'https://www.khl.ru/calendar-line/405/00/'},
           {'name': '16-17_PO', 'url': 'https://www.khl.ru/calendar-line/406/00/'},
           {'name': '17-18_RS', 'url': 'https://www.khl.ru/calendar-line/468/00/'},
           {'name': '17-18_PO', 'url': 'https://www.khl.ru/calendar-line/472/00/'},
           {'name': '18-19_RS', 'url': 'https://www.khl.ru/calendar-line/671/00/'},
           {'name': '18-19_PO', 'url': 'https://www.khl.ru/calendar-line/674/00/'},
           {'name': '19-20_RS', 'url': 'https://www.khl.ru/calendar-line/851/00/'},
           {'name': '19-20_PO', 'url': 'https://www.khl.ru/calendar-line/854/00/'},
           {'name': '20-21_RS', 'url': 'https://www.khl.ru/calendar-line/1045/00/'},
           {'name': '20-21_PO', 'url': 'https://www.khl.ru/calendar-line/1046/00/'},
           {'name': '21-22_RS', 'url': 'https://www.khl.ru/calendar-line/1097/00/'},
           {'name': '21-22_PO', 'url': 'https://www.khl.ru/calendar-line/1098/00/'},
           {'name': '22-23_RS', 'url': 'https://www.khl.ru/calendar-line/1154/00/'},
           {'name': '22-23_PO', 'url': 'https://www.khl.ru/calendar-line/1155/00/'},
           {'name': '23-24_RS', 'url': 'https://www.khl.ru/calendar-line/1217/00/'},
           {'name': '23-24_PO', 'url': 'https://www.khl.ru/calendar-line/1218/00/'}
           ]


def get_requests(url):
    req = requests.get(url=url, headers=HEADERS, verify=False)
    req.encoding = 'utf-8'
    src = req.text
    soup = BeautifulSoup(src, 'html5lib')
    return soup


def get_match_info(seasons):
    all_match_info = []
    for season in seasons:
        print(f"Воруем данные: {season['name']} ...")
        past_matches = get_requests(season['url']).find_all('div', class_='calendary-body__item games_past')
        matches = []
        for past_match in reversed(past_matches):
            matches.extend(past_match.find_all('div', class_='card-game'))
        for match in matches:
            if match.find(class_='card-game__center-score-left').text.strip() not in ['-', '+']:
                num = int(match.find(
                    class_='card-game__center-number roboto-condensed roboto-normal roboto-lg color-semiSecondary').text.split(
                    '№')[1].strip())
                home_name = match.find_all(class_='card-game__club-name roboto roboto-bold roboto-lg color-dark link')[
                    0].text.strip()
                away_name = match.find_all(class_='card-game__club-name roboto roboto-bold roboto-lg color-dark link')[
                    1].text.strip()
                href = 'https://www.khl.ru/' + match.find(class_='card-game__hover').find_all(
                    'a')[-2].get("href")
                all_match_info.append(
                    {
                        'season': season['name'],
                        'num': num,
                        'home_name': home_name,
                        'away_name': away_name,
                        'href': href,
                    }
                )
        print(f"Готово: {season['name']} !!! Спим 3 сек ...")
        time.sleep(3)

    return all_match_info


def write_json(json_file, new_match):
    with open(json_file, 'w', encoding="utf-8") as file:
        json.dump(new_match, file, indent=4, ensure_ascii=False)


def read_json(json_file):
    with open(json_file, encoding="utf-8") as file:
        all_match_info = json.load(file)
    return all_match_info


def create_column():
    with open(f'general_info.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'id_season',
                'id_match',
                'id_regular',
                'start_time',
                'location',
                'viewers',
                'coach_home',
                'coach_away',
                'referee_1',
                'referee_2',
                'linesman_1',
                'linesman_2',
                'team_home',
                'team_away',
                'G_home',
                'G_away',
                'end_match',
                'G_home_1per',
                'G_away_1per',
                'G_home_2per',
                'G_away_2per',
                'G_home_3per',
                'G_away_3per',
                'G_home_OT',
                'G_away_OT',
                'G_home_SO',
                'G_away_SO',
                'G_home_RT',
                'G_away_RT',
                'G_home_5on5',
                'G_home_5on4',
                'G_home_5on3',
                'G_home_4on4',
                'G_home_4on3',
                'G_home_3on3',
                'G_home_3on4',
                'G_home_3on5',
                'G_home_4on5',
                'G_home_EN',
                'G_home_bul',
                'G_away_5on5',
                'G_away_5on4',
                'G_away_5on3',
                'G_away_4on4',
                'G_away_4on3',
                'G_away_3on3',
                'G_away_3on4',
                'G_away_3on5',
                'G_away_4on5',
                'G_away_EN',
                'G_away_bul',
                'SOG_home',
                'SOG_away',
                'SOG_home_1per',
                'SOG_away_1per',
                'SOG_home_2per',
                'SOG_away_2per',
                'SOG_home_3per',
                'SOG_away_3per',
                'SOG_home_OT',
                'SOG_away_OT',
                'SOG_home_RT',
                'SOG_away_RT',
                'BLK_home',
                'BLK_away',
                'BLK_home_1per',
                'BLK_away_1per',
                'BLK_home_2per',
                'BLK_away_2per',
                'BLK_home_3per',
                'BLK_away_3per',
                'BLK_home_OT',
                'BLK_away_OT',
                'BLK_home_RT',
                'BLK_away_RT',
                'HIT_home',
                'HIT_away',
                'HIT_home_1per',
                'HIT_away_1per',
                'HIT_home_2per',
                'HIT_away_2per',
                'HIT_home_3per',
                'HIT_away_3per',
                'HIT_home_OT',
                'HIT_away_OT',
                'HIT_home_RT',
                'HIT_away_RT',
                'attack_time_home',
                'attack_time_away',
                'attack_time_home_1per',
                'attack_time_away_1per',
                'attack_time_home_2per',
                'attack_time_away_2per',
                'attack_time_home_3per',
                'attack_time_away_3per',
                'attack_time_home_OT',
                'attack_time_away_OT',
                'attack_time_home_RT',
                'attack_time_away_RT',
                'control_time_home',
                'control_time_away',
                'control_time_home_1per',
                'control_time_away_1per',
                'control_time_home_2per',
                'control_time_away_2per',
                'control_time_home_3per',
                'control_time_away_3per',
                'control_time_home_OT',
                'control_time_away_OT',
                'control_time_home_RT',
                'control_time_away_RT',
                'distance_covered_home',
                'distance_covered_away',
                'distance_covered_home_1per',
                'distance_covered_away_1per',
                'distance_covered_home_2per',
                'distance_covered_away_2per',
                'distance_covered_home_3per',
                'distance_covered_away_3per',
                'distance_covered_home_OT',
                'distance_covered_away_OT',
                'distance_covered_home_RT',
                'distance_covered_away_RT'
            )
        )

    with open(f'goal_score.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'id_season',
                'id_match',
                'home_team',
                'away_team',
                'score_number',
                'score_time_minute',
                'score_time_second',
                'score_home',
                'score_away',
                'goal format',
                'G_player_id',
                'G_player_name',
                'A1_player_id',
                'A1_player_name',
                'A2_player_id',
                'A2_player_name',
                'home_roster_on_ice',
                'away_roster_on_ice'
            )
        )

    with open(f'goalies_stats.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'id_season',
                'id_match',
                'team',
                'player_position',
                'player_num',
                'player_id',
                'player_name',
                'GP',
                'W',
                'L',
                'PH_series',
                'SA',
                'GA',
                'Svs',
                'G',
                'A',
                'SO',
                'PIM',
                'TOI'
            )
        )

    with open(f'skaters_stats.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'id_season',
                'id_match',
                'team',
                'player_position',
                'player_num',
                'player_id',
                'player_name',
                'GP',
                'G',
                'A',
                'P',
                'pl_min',
                'plus',
                'minus',
                'PIM',
                'GWG',
                'SOG',
                'FO',
                'FOW',
                'TOI',
                'shifts',
                'HIT',
                'BS',
                'foul_on_player',
                'attack_time',
                'avd_speed',
                'max_speed',
                'distance_covered'
            )
        )

    with open(f'ps_stats.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'id_season',
                'id_match',
                'home_team',
                'away_team',
                'PS_score_home',
                'PS_score_away',
                'PS_home_pl_id',
                'PS_home_pl_name',
                'PS_away_gp_id',
                'PS_away_gp_name',
                'PS_away_pl_id',
                'PS_away_pl_name',
                'PS_home_gp_id',
                'PS_home_gp_name'
            )
        )

    with open(f'penalty.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'id_season',
                'id_match',
                'home_team',
                'away_team',
                'PIM_time_sec',
                'PIM_team',
                'PIM_player_id',
                'PIM_player_name',
                'PIM_score',
                'PIM_type'
            )
        )


def get_test_html(url):
    response = requests.get(url=url, headers=HEADERS)
    with open(f'test.html', 'w', encoding="utf-8") as file:
        file.write(response.text)


def get_goal_score(info, match_soup):
    all_goals = get_all_table_1(match_soup)[0].findAll('tr')
    for goal in all_goals:
        goal_table = goal.findAll(class_='protocol-table__txt')
        id_season = info['season']
        id_match = int(info['href'].split('/')[-3])
        home_team = info['home_name']
        away_team = info['away_name']
        score_number = int(goal_table[0].text.strip())
        score_time_minute = int(goal_table[2].text.strip().split('′')[0]) + 1
        score_time_second = int(goal_table[2].text.strip().split('′')[0]) * 60 + int(
            goal_table[2].text.strip().split('′')[1])
        score_home = int(goal_table[3].text.strip().split(':')[0])
        score_away = int(goal_table[3].text.strip().split(':')[1])
        goal_format = goal_table[4].text.strip()
        G_player_id = int(goal_table[5].find('a').get('href').split('/')[2])
        G_player_name = goal_table[5].text.strip().split('.')[1].split('(')[0].strip()

        try:
            A1_player_id = int(goal_table[6].find('a').get('href').split('/')[2])
        except:
            A1_player_id = NaN

        try:
            A1_player_name = goal_table[6].text.strip().split('.')[1].split('(')[0].strip()
        except:
            A1_player_name = NaN

        try:
            A2_player_id = int(goal_table[7].find('a').get('href').split('/')[2])
        except:
            A2_player_id = NaN

        try:
            A2_player_name = goal_table[7].text.strip().split('.')[1].split('(')[0].strip()
        except:
            A2_player_name = NaN

        try:
            home_roster_on_ice = [int(x.text) for x in goal_table[8].findAll('a')]
        except:
            home_roster_on_ice = NaN

        try:
            away_roster_on_ice = [int(x.text) for x in goal_table[9].findAll('a')]
        except:
            away_roster_on_ice = NaN

        with open(f'goal_score.csv', 'a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    id_season,
                    id_match,
                    home_team,
                    away_team,
                    score_number,
                    score_time_minute,
                    score_time_second,
                    score_home,
                    score_away,
                    goal_format,
                    G_player_id,
                    G_player_name,
                    A1_player_id,
                    A1_player_name,
                    A2_player_id,
                    A2_player_name,
                    home_roster_on_ice,
                    away_roster_on_ice
                )
            )


def get_goalies_stats(info, match_soup):
    all_goalies_stats_home = get_all_table_1(match_soup)[1].findAll('tr')
    all_goalies_stats_away = get_all_table_1(match_soup)[4].findAll('tr')
    for home_away in [all_goalies_stats_home, all_goalies_stats_away]:
        for goalies_stat in home_away:
            goalies_table = goalies_stat.findAll(class_='fine-table__txt')
            id_season = info['season']
            id_match = int(info['href'].split('/')[-3])
            team = [info['home_name'] if home_away == all_goalies_stats_home else info['away_name']][0]
            player_position = 'G'
            player_num = int(goalies_table[0].text.strip())
            player_id = int(goalies_table[1].find('a').get('href').split('/')[2])
            player_name = goalies_table[1].text.strip()
            GP = int(goalies_table[2].text.strip())
            W = int(goalies_table[3].text.strip())
            L = int(goalies_table[4].text.strip())
            PH_series = int(goalies_table[5].text.strip())
            SA = int(goalies_table[6].text.strip())
            GA = int(goalies_table[7].text.strip())
            Svs = int(goalies_table[8].text.strip())
            G = int(goalies_table[11].text.strip())
            A = int(goalies_table[12].text.strip())
            SO = int(goalies_table[13].text.strip())
            PIM = int(goalies_table[14].text.strip())
            try:
                TOI = int(goalies_table[15].text.split(':')[0]) * 60 + int(goalies_table[15].text.split(':')[1])
            except:
                TOI = 0

            with open(f'goalies_stats.csv', 'a', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        id_season,
                        id_match,
                        team,
                        player_position,
                        player_num,
                        player_id,
                        player_name,
                        GP,
                        W,
                        L,
                        PH_series,
                        SA,
                        GA,
                        Svs,
                        G,
                        A,
                        SO,
                        PIM,
                        TOI
                    )
                )


def get_skaters_stats(info, match_soup):
    all_defenders_stats_home = get_all_table_1(match_soup)[2].findAll('tr')
    all_forwards_stats_home = get_all_table_1(match_soup)[3].findAll('tr')
    all_defenders_stats_away = get_all_table_1(match_soup)[5].findAll('tr')
    all_forwards_stats_away = get_all_table_1(match_soup)[6].findAll('tr')
    for home_away in [all_defenders_stats_home, all_forwards_stats_home, all_defenders_stats_away, all_forwards_stats_away]:
        for skaters_stat in home_away:
            skaters_table = skaters_stat.findAll(class_='fine-table__txt')
            id_season = info['season']
            id_match = int(info['href'].split('/')[-3])
            team = [info['home_name'] if home_away in [all_defenders_stats_home, all_forwards_stats_home] else info['away_name']][0]
            player_position = ['D' if home_away in [all_defenders_stats_home, all_defenders_stats_away] else 'F'][0]
            player_num = int(skaters_table[0].text.strip())
            player_id = int(skaters_table[1].find('a').get('href').split('/')[2])
            player_name = skaters_table[1].text.strip()
            GP =  int(skaters_table[2].text.strip())
            G = int(skaters_table[3].text.strip())
            A = int(skaters_table[4].text.strip())
            P = int(skaters_table[5].text.strip())
            pl_min = int(skaters_table[6].text.strip())
            try:
                plus = int(skaters_table[7].text.strip())
            except:
                plus = NaN
            try:
                minus = int(skaters_table[8].text.strip())
            except:
                minus = NaN
            PIM = int(skaters_table[9].text.strip())
            GWG = int(skaters_table[14].text.strip())
            SOG = int(skaters_table[16].text.strip())
            FO = int(skaters_table[18].text.strip())
            FOW = int(skaters_table[19].text.strip())
            try:
                TOI = int(skaters_table[21].text.split(':')[0]) * 60 + int(skaters_table[21].text.split(':')[1])
            except:
                TOI = 0

            try:
                shifts = int(skaters_table[22].text.strip())
            except:
                shifts = 0
            try:
                HIT = int(skaters_table[23].text.strip())
            except:
                HIT = NaN
            try:
                BS = int(skaters_table[24].text.strip())
            except:
                BS = NaN
            try:
                foul_on_player = int(skaters_table[26].text.strip())
            except:
                foul_on_player = 0

            try:
                attack_time = int(skaters_table[25].text.split(':')[0]) * 60 + int(skaters_table[25].text.split(':')[1])
            except:
                attack_time = 0

            try:
                avd_speed = float(skaters_table[27].text.strip())
            except:
                avd_speed = NaN

            try:
                max_speed = float(skaters_table[28].text.strip())
            except:
                max_speed = NaN

            try:
                distance_covered = float(skaters_table[29].text.strip())
            except:
                distance_covered = NaN

            with open(f'skaters_stats.csv', 'a', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        id_season,
                        id_match,
                        team,
                        player_position,
                        player_num,
                        player_id,
                        player_name,
                        GP,
                        G,
                        A,
                        P,
                        pl_min,
                        plus,
                        minus,
                        PIM,
                        GWG,
                        SOG,
                        FO,
                        FOW,
                        TOI,
                        shifts,
                        HIT,
                        BS,
                        foul_on_player,
                        attack_time,
                        avd_speed,
                        max_speed,
                        distance_covered
                    )
                )


def get_penalty(info, match_soup):
    penalty_table = match_soup.findAll(class_='fineTable-table__scroll')
    penalty_table_home = penalty_table[0].findAll(class_='fineTable-table__line-wrapp')
    penalty_table_away = penalty_table[1].findAll(class_='fineTable-table__line-wrapp')
    for i in range(1, len(penalty_table_home)):
        penalty_string = penalty_table_home[i].findAll(class_='fineTable-table__line-text')
        indicator = 'home'
        if penalty_string[0].text.strip() == '':
            penalty_string = penalty_table_away[i].findAll(class_='fineTable-table__line-text')
            indicator = 'away'
        id_season = info['season']
        id_match = int(info['href'].split('/')[-3])
        home_team = info['home_name']
        away_team = info['away_name']
        PIM_time_sec = int(penalty_string[0].text.split(':')[0]) * 60 + int(penalty_string[0].text.split(':')[1])
        PIM_team = [info['home_name'] if indicator == 'home' else info['away_name']][0]
        if 'командный штраф' in penalty_string[1].text.strip():
            PIM_player_id = NaN
            PIM_player_name = 'командный штраф'
        else:
            PIM_player_id = int(penalty_string[1].find('a').get('href').split('/')[2])
            PIM_player_name = penalty_string[1].text.split('.')[1].strip()
        PIM_score = int(penalty_string[2].text.strip())
        PIM_type = penalty_string[3].text.strip()

        with open(f'penalty.csv', 'a', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)

            writer.writerow(
                (
                    id_season,
                    id_match,
                    home_team,
                    away_team,
                    PIM_time_sec,
                    PIM_team,
                    PIM_player_id,
                    PIM_player_name,
                    PIM_score,
                    PIM_type
                )
            )


def get_ps_stats(info, match_soup):
    # all_ps_stats = get_all_table_2(match_soup)[3].findAll(
    #     'fineTable-totalTable__line  roboto roboto-normal roboto-sm color-black')
    # for ps in range(0, len(all_ps_stats), 2):
    #     ps_string = ps.findAll(class_='fineTable-totalTable__line-item')
    #     indicator = ['away' if ps_string[1].text.strip() == '' else 'home'][0]
    #     id_season = info['season']
    #     id_match = int(info['href'].split('/')[-3])
    #     home_team = info['home_name']
    #     away_team = info['away_name']
    #     PS_score_home = int(ps_string[0].text.split(':')[0])
    #     PS_score_away = int(ps_string[0].text.split(':')[1])
    #     PS_home_pl_id = int(ps_string[1].find('a').get('href').split('/')[2])
    #     PS_home_pl_name = ps_string[1].text.split('.')[1].strip()
    #     PS_away_gp_id = int(ps_string[4].find('a').get('href').split('/')[2])
    #     PS_away_gp_name = ps_string[1].text.split('.')[1].strip()
    #
    #     PS_away_pl_id = np.NaN
    #     PS_away_pl_name = np.NaN
    #     PS_home_gp_id = np.NaN
    #     PS_home_gp_name = np.NaN
        pass


def get_general_info(info, match_soup):
    id_season = info['season']
    id_match = int(info['href'].split('/')[-3])
    id_regular = info['num']
    basic_info = match_soup.find(class_='card-infos summary-header__card-infos').findAll(
        'div', class_='card-infos__item-info')
    start_time = basic_info[0].text.strip()
    location = basic_info[1].findAll('p')[0].text.strip()
    viewers = basic_info[1].findAll('p')[2].text.split()[0]
    coach_home = match_soup.findAll(class_='preview-frame__club-nameTrainer roboto roboto-bold roboto-xxl')[0].text.strip()
    coach_away = match_soup.findAll(class_='preview-frame__club-nameTrainer roboto roboto-bold roboto-xxl')[1].text.strip()
    if len(basic_info[2].findAll('a')) == 4:
        try:
            referee_1 = basic_info[2].findAll('a')[0].text.split('.')[1].strip()
        except:
            referee_1 = basic_info[2].findAll('a')[0].text.strip()
        try:
            referee_2 = basic_info[2].findAll('a')[1].text.split('.')[1].strip()
        except:
            referee_2 = basic_info[2].findAll('a')[1].text.strip()
        try:
            linesman_1 = basic_info[2].findAll('a')[2].text.split('.')[1].strip()
        except:
            linesman_1 = basic_info[2].findAll('a')[2].text.strip()
        try:
            linesman_2 = basic_info[2].findAll('a')[3].text.split('.')[1].strip()
        except:
            linesman_2 = basic_info[2].findAll('a')[3].text.strip()
    else:
        try:
            referee_1 = basic_info[2].findAll('a')[0].text.split('.')[1].strip()
        except:
            referee_1 = basic_info[2].findAll('a')[0].text.strip()
        referee_2 = NaN
        try:
            linesman_1 = basic_info[2].findAll('a')[1].text.split('.')[1].strip()
        except:
            linesman_1 = basic_info[2].findAll('a')[1].text.strip()
        try:
            linesman_2 = basic_info[2].findAll('a')[2].text.split('.')[1].strip()
        except:
            linesman_2 = basic_info[2].findAll('a')[2].text.strip()
    team_home = info['home_name']
    team_away = info['away_name']
    score_info = match_soup.find(
        class_='preview-frame__center-score roboto-condensed roboto-bold color-white title-xl').get_text()
    score_parts = re.findall(r'\d+', score_info)
    try:
        G_home = int(score_parts[0].strip())
    except:
        G_home = NaN
    try:
        G_away = int(score_parts[-1].strip())
    except:
        G_away = NaN
    try:
        end_match = score_info.text.split()[2].strip()
    except:
        end_match = 'RT'
    end_match = ['SO' if end_match == 'Б' else 'OT' if end_match == 'OT' else end_match][0]
    score_period_info = match_soup.find(class_='previw-frame__center-value roboto roboto-bold roboto-ll color-white')
    G_home_1per = int(score_period_info.text.strip().split()[0].split(':')[0])
    G_away_1per = int(score_period_info.text.strip().split()[0].split(':')[1])
    G_home_2per = int(score_period_info.text.strip().split()[1].split(':')[0])
    G_away_2per = int(score_period_info.text.strip().split()[1].split(':')[1])
    G_home_3per = int(score_period_info.text.strip().split()[2].split(':')[0])
    G_away_3per = int(score_period_info.text.strip().split()[2].split(':')[1])
    try:
        G_home_OT = int(score_period_info.text.strip().split()[3].split(':')[0])
        G_away_OT = int(score_period_info.text.strip().split()[3].split(':')[1])
    except:
        G_home_OT = NaN
        G_away_OT = NaN
    try:
        G_home_SO = int(score_period_info.text.strip().split()[4].split(':')[0])
        G_away_SO = int(score_period_info.text.strip().split()[4].split(':')[1])
    except:
        G_home_SO = NaN
        G_away_SO = NaN
    G_home_RT = int(G_home_1per + G_home_2per + G_home_3per)
    G_away_RT = int(G_away_1per + G_away_2per + G_away_3per)
    score_type_table = get_all_table_1(match_soup)[7].findAll('tr')
    if score_type_table[0].findAll(class_ = 'fine-table__txt')[0].text.strip() == info['home_name']:
        G_home_5on5 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[2].text.strip())
        G_home_5on4 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[3].text.strip())
        G_home_5on3 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[4].text.strip())
        G_home_4on4 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[5].text.strip())
        G_home_4on3 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[6].text.strip())
        G_home_3on3 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[7].text.strip())
        G_home_3on4 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[8].text.strip())
        G_home_3on5 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[9].text.strip())
        G_home_4on5 = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[10].text.strip())
        G_home_EN = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[11].text.strip())
        G_home_bul = int(score_type_table[0].findAll(class_ = 'fine-table__txt')[12].text.strip())
        G_away_5on5 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[2].text.strip())
        G_away_5on4 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[3].text.strip())
        G_away_5on3 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[4].text.strip())
        G_away_4on4 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[5].text.strip())
        G_away_4on3 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[6].text.strip())
        G_away_3on3 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[7].text.strip())
        G_away_3on4 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[8].text.strip())
        G_away_3on5 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[9].text.strip())
        G_away_4on5 = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[10].text.strip())
        G_away_EN = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[11].text.strip())
        G_away_bul = int(score_type_table[1].findAll(class_ = 'fine-table__txt')[12].text.strip())
    else:
        G_home_5on5 = int(score_type_table[1].findAll(class_='fine-table__txt')[2].text.strip())
        G_home_5on4 = int(score_type_table[1].findAll(class_='fine-table__txt')[3].text.strip())
        G_home_5on3 = int(score_type_table[1].findAll(class_='fine-table__txt')[4].text.strip())
        G_home_4on4 = int(score_type_table[1].findAll(class_='fine-table__txt')[5].text.strip())
        G_home_4on3 = int(score_type_table[1].findAll(class_='fine-table__txt')[6].text.strip())
        G_home_3on3 = int(score_type_table[1].findAll(class_='fine-table__txt')[7].text.strip())
        G_home_3on4 = int(score_type_table[1].findAll(class_='fine-table__txt')[8].text.strip())
        G_home_3on5 = int(score_type_table[1].findAll(class_='fine-table__txt')[9].text.strip())
        G_home_4on5 = int(score_type_table[1].findAll(class_='fine-table__txt')[10].text.strip())
        G_home_EN = int(score_type_table[1].findAll(class_='fine-table__txt')[11].text.strip())
        G_home_bul = int(score_type_table[1].findAll(class_='fine-table__txt')[12].text.strip())
        G_away_5on5 = int(score_type_table[0].findAll(class_='fine-table__txt')[2].text.strip())
        G_away_5on4 = int(score_type_table[0].findAll(class_='fine-table__txt')[3].text.strip())
        G_away_5on3 = int(score_type_table[0].findAll(class_='fine-table__txt')[4].text.strip())
        G_away_4on4 = int(score_type_table[0].findAll(class_='fine-table__txt')[5].text.strip())
        G_away_4on3 = int(score_type_table[0].findAll(class_='fine-table__txt')[6].text.strip())
        G_away_3on3 = int(score_type_table[0].findAll(class_='fine-table__txt')[7].text.strip())
        G_away_3on4 = int(score_type_table[0].findAll(class_='fine-table__txt')[8].text.strip())
        G_away_3on5 = int(score_type_table[0].findAll(class_='fine-table__txt')[9].text.strip())
        G_away_4on5 = int(score_type_table[0].findAll(class_='fine-table__txt')[10].text.strip())
        G_away_EN = int(score_type_table[0].findAll(class_='fine-table__txt')[11].text.strip())
        G_away_bul = int(score_type_table[0].findAll(class_='fine-table__txt')[12].text.strip())
    SOG_info_table = get_all_table_2(match_soup)[0].findAll(class_='fineTable-totalTable__line')
    SOG_home = int(SOG_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    SOG_away = int(SOG_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    SOG_home_1per = int(SOG_info_table[1].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    SOG_away_1per = int(SOG_info_table[1].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    SOG_home_2per = int(SOG_info_table[2].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    SOG_away_2per = int(SOG_info_table[2].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    SOG_home_3per = int(SOG_info_table[3].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    SOG_away_3per = int(SOG_info_table[3].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    try:
        SOG_home_OT = int(SOG_info_table[4].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        SOG_home_OT = NaN
    try:
        SOG_away_OT = int(SOG_info_table[4].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        SOG_away_OT = NaN
    SOG_home_RT = SOG_home_1per + SOG_home_2per + SOG_home_3per
    SOG_away_RT = SOG_away_1per + SOG_away_2per + SOG_away_3per
    HIT_info_table = get_all_table_2(match_soup)[1].findAll(class_='fineTable-totalTable__line')
    try:
        BLK_home = int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[0].text.strip())
    except:
        BLK_home = NaN
    try:
        BLK_away = int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[4].text.strip())
    except:
        BLK_away = NaN
    try:
        BLK_home_1per = int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[0].text.strip())
    except:
        BLK_home_1per = NaN
    try:
        BLK_away_1per = int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[4].text.strip())
    except:
        BLK_away_1per = NaN
    try:
        BLK_home_2per = int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[0].text.strip())
    except:
        BLK_home_2per = NaN
    try:
        BLK_away_2per = int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[4].text.strip())
    except:
        BLK_away_2per = NaN
    try:
        BLK_home_3per = int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[0].text.strip())
    except:
        BLK_home_3per = NaN
    try:
        BLK_away_3per = int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[4].text.strip())
    except:
        BLK_away_3per = NaN
    try:
        BLK_home_OT = int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[0].text.strip())
    except:
        BLK_home_OT = NaN
    try:
        BLK_away_OT = int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[4].text.strip())
    except:
        BLK_away_OT = NaN
    try:
        BLK_home_RT = BLK_home_1per + BLK_home_2per + BLK_home_3per
    except:
        BLK_home_RT = NaN
    try:
        BLK_away_RT = BLK_away_1per + BLK_away_2per + BLK_away_3per
    except:
        BLK_away_RT = NaN
    try:
        HIT_home = int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        HIT_home = NaN
    try:
        HIT_away = int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        HIT_away = NaN
    try:
        HIT_home_1per = int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        HIT_home_1per = NaN
    try:
        HIT_away_1per = int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        HIT_away_1per = NaN
    try:
        HIT_home_2per = int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        HIT_home_2per = NaN
    try:
        HIT_away_2per = int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        HIT_away_2per = NaN
    try:
        HIT_home_3per = int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        HIT_home_3per = NaN
    try:
        HIT_away_3per = int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        HIT_away_3per = NaN
    try:
        HIT_home_OT = int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        HIT_home_OT = NaN
    try:
        HIT_away_OT = int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        HIT_away_OT = NaN
    try:
        HIT_home_RT = HIT_home_1per + HIT_home_2per + HIT_home_3per
    except:
        HIT_home_RT = NaN
    try:
        HIT_away_RT = HIT_away_1per + HIT_away_2per + HIT_away_3per
    except:
        HIT_away_RT = NaN
    try:
        attack_time_home = int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[0]) * 60 + int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[1])
    except:
        attack_time_home = NaN
    try:
        attack_time_away = int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[0]) * 60 + int(HIT_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[1])
    except:
        attack_time_away = NaN
    try:
        attack_time_home_1per = int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[0]) * 60 + int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[1])
    except:
        attack_time_home_1per = NaN
    try:
        attack_time_away_1per = int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[0]) * 60 + int(HIT_info_table[1].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[1])
    except:
        attack_time_away_1per = NaN
    try:
        attack_time_home_2per = int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[0]) * 60 + int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[1])
    except:
        attack_time_home_2per = NaN
    try:
        attack_time_away_2per = int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[0]) * 60 + int(HIT_info_table[2].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[1])
    except:
        attack_time_away_2per = NaN
    try:
        attack_time_home_3per = int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[0]) * 60 + int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[1])
    except:
        attack_time_home_3per = NaN
    try:
        attack_time_away_3per = int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[0]) * 60 + int(HIT_info_table[3].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[1])
    except:
        attack_time_away_3per = NaN
    try:
        attack_time_home_OT = int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[0]) * 60 + int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[2].text.split(':')[1])
    except:
        attack_time_home_OT = NaN
    try:
        attack_time_away_OT = int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[0]) * 60 + int(HIT_info_table[4].findAll(class_='fineTable-totalTable__line-item')[6].text.split(':')[1])
    except:
        attack_time_away_OT = NaN
    try:
        attack_time_home_RT = attack_time_home_1per + attack_time_home_2per + attack_time_home_3per
    except:
        attack_time_home_RT = NaN
    try:
        attack_time_away_RT = attack_time_away_1per + attack_time_away_2per + attack_time_away_3per
    except:
        attack_time_away_RT = NaN
    control_info_table = get_all_table_2(match_soup)[2].findAll(class_='fineTable-totalTable__line')
    try:
        control_time_home = int(control_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[0]) * 60 + int(control_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[1])
    except:
        control_time_home = NaN
    try:
        control_time_away = int(control_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[0]) * 60 + int(control_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[1])
    except:
        control_time_away = NaN
    try:
        control_time_home_1per = int(control_info_table[1].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[0]) * 60 + int(control_info_table[1].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[1])
    except:
        control_time_home_1per = NaN
    try:
        control_time_away_1per = int(control_info_table[1].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[0]) * 60 + int(control_info_table[1].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[1])
    except:
        control_time_away_1per = NaN
    try:
        control_time_home_2per = int(control_info_table[2].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[0]) * 60 + int(control_info_table[2].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[1])
    except:
        control_time_home_2per = NaN
    try:
        control_time_away_2per = int(control_info_table[2].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[0]) * 60 + int(control_info_table[2].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[1])
    except:
        control_time_away_2per = NaN
    try:
        control_time_home_3per = int(control_info_table[3].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[0]) * 60 + int(control_info_table[3].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[1])
    except:
        control_time_home_3per = NaN
    try:
        control_time_away_3per = int(control_info_table[3].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[0]) * 60 + int(control_info_table[3].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[1])
    except:
        control_time_away_3per = NaN
    try:
        control_time_home_OT = int(control_info_table[4].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[0]) * 60 + int(control_info_table[4].findAll(class_='fineTable-totalTable__line-item')[0].text.split(':')[1])
    except:
        control_time_home_OT = NaN
    try:
        control_time_away_OT = int(control_info_table[4].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[0]) * 60 + int(control_info_table[4].findAll(class_='fineTable-totalTable__line-item')[4].text.split(':')[1])
    except:
        control_time_away_OT = NaN
    try:
        control_time_home_RT = control_time_home_1per + control_time_home_2per + control_time_home_3per
    except:
        control_time_home_RT = NaN
    try:
        control_time_away_RT = control_time_away_1per + control_time_away_2per + control_time_away_3per
    except:
        control_time_away_RT = NaN
    try:
        distance_covered_home = float(control_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        distance_covered_home = NaN
    try:
        distance_covered_away = float(control_info_table[-1].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        distance_covered_away = NaN
    try:
        distance_covered_home_1per = float(control_info_table[1].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        distance_covered_home_1per = NaN
    try:
        distance_covered_away_1per = float(control_info_table[1].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        distance_covered_away_1per = NaN
    try:
        distance_covered_home_2per = float(control_info_table[2].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        distance_covered_home_2per = NaN
    try:
        distance_covered_away_2per = float(control_info_table[2].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        distance_covered_away_2per = NaN
    try:
        distance_covered_home_3per = float(control_info_table[3].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        distance_covered_home_3per = NaN
    try:
        distance_covered_away_3per = float(control_info_table[3].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        distance_covered_away_3per = NaN
    try:
        distance_covered_home_OT = float(control_info_table[4].findAll(class_='fineTable-totalTable__line-item')[1].text.strip())
    except:
        distance_covered_home_OT = NaN
    try:
        distance_covered_away_OT = float(control_info_table[4].findAll(class_='fineTable-totalTable__line-item')[5].text.strip())
    except:
        distance_covered_away_OT = NaN
    try:
        distance_covered_home_RT = distance_covered_home_1per + distance_covered_home_2per + distance_covered_home_3per
    except:
        distance_covered_home_RT = NaN
    try:
        distance_covered_away_RT = distance_covered_away_1per + distance_covered_away_2per + distance_covered_away_3per
    except:
        distance_covered_away_RT = NaN

    with open(f'general_info.csv', 'a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                id_season,
                id_match,
                id_regular,
                start_time,
                location,
                viewers,
                coach_home,
                coach_away,
                referee_1,
                referee_2,
                linesman_1,
                linesman_2,
                team_home,
                team_away,
                G_home,
                G_away,
                end_match,
                G_home_1per,
                G_away_1per,
                G_home_2per,
                G_away_2per,
                G_home_3per,
                G_away_3per,
                G_home_OT,
                G_away_OT,
                G_home_SO,
                G_away_SO,
                G_home_RT,
                G_away_RT,
                G_home_5on5,
                G_home_5on4,
                G_home_5on3,
                G_home_4on4,
                G_home_4on3,
                G_home_3on3,
                G_home_3on4,
                G_home_3on5,
                G_home_4on5,
                G_home_EN,
                G_home_bul,
                G_away_5on5,
                G_away_5on4,
                G_away_5on3,
                G_away_4on4,
                G_away_4on3,
                G_away_3on3,
                G_away_3on4,
                G_away_3on5,
                G_away_4on5,
                G_away_EN,
                G_away_bul,
                SOG_home,
                SOG_away,
                SOG_home_1per,
                SOG_away_1per,
                SOG_home_2per,
                SOG_away_2per,
                SOG_home_3per,
                SOG_away_3per,
                SOG_home_OT,
                SOG_away_OT,
                SOG_home_RT,
                SOG_away_RT,
                BLK_home,
                BLK_away,
                BLK_home_1per,
                BLK_away_1per,
                BLK_home_2per,
                BLK_away_2per,
                BLK_home_3per,
                BLK_away_3per,
                BLK_home_OT,
                BLK_away_OT,
                BLK_home_RT,
                BLK_away_RT,
                HIT_home,
                HIT_away,
                HIT_home_1per,
                HIT_away_1per,
                HIT_home_2per,
                HIT_away_2per,
                HIT_home_3per,
                HIT_away_3per,
                HIT_home_OT,
                HIT_away_OT,
                HIT_home_RT,
                HIT_away_RT,
                attack_time_home,
                attack_time_away,
                attack_time_home_1per,
                attack_time_away_1per,
                attack_time_home_2per,
                attack_time_away_2per,
                attack_time_home_3per,
                attack_time_away_3per,
                attack_time_home_OT,
                attack_time_away_OT,
                attack_time_home_RT,
                attack_time_away_RT,
                control_time_home,
                control_time_away,
                control_time_home_1per,
                control_time_away_1per,
                control_time_home_2per,
                control_time_away_2per,
                control_time_home_3per,
                control_time_away_3per,
                control_time_home_OT,
                control_time_away_OT,
                control_time_home_RT,
                control_time_away_RT,
                distance_covered_home,
                distance_covered_away,
                distance_covered_home_1per,
                distance_covered_away_1per,
                distance_covered_home_2per,
                distance_covered_away_2per,
                distance_covered_home_3per,
                distance_covered_away_3per,
                distance_covered_home_OT,
                distance_covered_away_OT,
                distance_covered_home_RT,
                distance_covered_away_RT
            )
        )


def get_all_table_1(match_soup):
    all_table = match_soup.findAll(class_='roboto roboto-sm roboto-normal color-black')
    goal_table = all_table[0]
    goalie_home_table = all_table[1]
    defender_home_table = all_table[2]
    forward_home_table = all_table[3]
    goalie_away_table = all_table[4]
    defender_away_table = all_table[5]
    forward_away_table = all_table[6]
    score_type_table = all_table[8]
    return goal_table, goalie_home_table, defender_home_table, forward_home_table, goalie_away_table, \
           defender_away_table, forward_away_table, score_type_table


def get_all_table_2(match_soup):
    all_table = match_soup.findAll(class_='fineTable-totalTable d-none_768')
    if len(all_table) == 5:
        SOG_info_table = all_table[1]
        HIT_info_table = all_table[2]
        control_info_table = all_table[3]
        ps_stats_table = all_table[0]
        return SOG_info_table, HIT_info_table, control_info_table, ps_stats_table
    else:
        SOG_info_table = all_table[0]
        HIT_info_table = all_table[1]
        control_info_table = all_table[2]
        return SOG_info_table, HIT_info_table, control_info_table


def get_feature_match(season):
    create_column_feature()
    print(f"Получаем список будующих матчей")
    feature_matches = get_requests(season['url']).find_all('div', class_='calendary-body__item games_featured')
    for feature_match in feature_matches:
        matches = []
        matches.extend(feature_match.find_all('div', class_='card-game'))
        date_start = feature_match.find(class_='calendary-body__wrap-time color-primary')\
                .text.split(',')[0].strip()
        for match in matches:
            id_season = season['name']
            id_regular = int(match.find(
                class_='card-game__center-number roboto-condensed roboto-normal roboto-lg color-semiSecondary').text.split(
                '№')[1].strip())
            team_home = match.find_all(class_='card-game__club-name roboto roboto-bold roboto-lg color-dark link')[
                0].text.strip()
            team_away = match.find_all(class_='card-game__club-name roboto roboto-bold roboto-lg color-dark link')[
                1].text.strip()
            time_start = match.find(class_='card-game__center-time roboto-condensed roboto-bold title-md color-dark')\
                .text.split('мск')[0].strip()
            start_time = date_start + " " + time_start

            with open(f'feature_match.csv', 'a', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)

                writer.writerow(
                    (
                        id_season,
                        id_regular,
                        team_home,
                        team_away,
                        start_time
                    )
                )

    print(f"Готов список будующих матчей сезона: {season['name']}")


def create_column_feature():
    with open(f'feature_match.csv', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            (
                'id_season',
                'id_regular',
                'team_home',
                'team_away',
                'start_time'
            )
        )


def main():
    get_feature_match(SEASONS[-1:][0])
    all_match_info = read_json('all_match_info.json')
    start = len(all_match_info)
    recorded_matches = [x.get('season') for x in all_match_info if x.get('season') == SEASONS[-1]['name']]
    all_matches_on_site = get_match_info(SEASONS[-1:])
    if len(recorded_matches) - len(all_matches_on_site) != 0:
        new_match = all_matches_on_site[len(recorded_matches) - len(all_matches_on_site):]
        all_match_info.extend(new_match)
        write_json('all_match_info.json', all_match_info)
        all_match_info = read_json('all_match_info.json')
        # create_column()
        for info in all_match_info[start:]:
            # get_test_html(info['href'])
            print_info = info['num']
            print_season = info['season']
            print(f'Начинаем сезон {print_season}  матч номер {print_info}')
            match_soup = get_requests(info['href'])
            get_goal_score(info, match_soup)
            get_goalies_stats(info, match_soup)
            get_skaters_stats(info, match_soup)
            get_penalty(info, match_soup)
            get_general_info(info, match_soup)
    else:
        print("Всё, новых матчей больше нет")
    time.sleep(10)
    main_ml('general_info.csv', 'feature_match.csv')


def test(season):
    # feature_matches = get_requests(season['url']).find_all('div', class_='calendary-body__item games_featured')
    get_match_info(season)



def auto_run():
    print('Power ON')
    schedule.every().day.at('08:30').do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    # auto_run()
    main()
    # test(SEASONS[-1:])
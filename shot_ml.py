import pandas as pd
import numpy as np
import datetime
import json
from catboost import CatBoostRegressor
from sklearn.model_selection import train_test_split
import pickle
import telebot

with open('config.json') as file:
    config = json.load(file)

bot = telebot.TeleBot(config['API_TOKEN'])


def main_ml(file, new_match):
    tab = pd.read_csv(file)
    tab.loc[246, ['G_home', 'G_away', 'end_match']] = [3, 1, 'RT']
    tab['G_home'] = tab['G_home'].astype('int')
    team_name_dict = {
        'Адмирал': 'ADM',
        'Ак Барс': 'AKB',
        'Амур': 'AMR',
        'Авангард': 'AVG',
        'Автомобилист': 'AVT',
        'Барыс': 'BAR',
        'ЦСКА': 'CSKA',
        'Динамо Мн': 'DMN',
        'Динамо Р': 'DRG',
        'Динамо М': 'DYN',
        'Куньлунь РС': 'KRS',
        'Локомотив': 'LOK',
        'Металлург Мг': 'MMG',
        'Нефтехимик': 'NKH',
        'Салават Юлаев': 'SAL',
        'ХК Сочи': 'SCH',
        'Северсталь': 'SEV',
        'Сибирь': 'SIB',
        'СКА': 'SKA',
        'Спартак': 'SPR',
        'Торпедо НН': 'TOR',
        'Торпедо': 'TOR',
        'Трактор': 'TRK',
        'Витязь': 'VIT',
        'Йокерит': 'YOK',
        'Медвешчак': 'MDV',
        'Металлург Нк': 'MNK',
        'Югра': 'UGR',
        'Слован': 'SLV',
        'Лада': 'LAD',
        'Атлант': 'ATL',
        'Лев Пр': 'LEV',
        'Лев Пп': 'LEV',
        'ХК МВД': 'MVD',
        'Донбасс': 'DON',
        'Химик': 'HIM'}
    for col in ['team_home', 'team_away']:
        tab = tab.replace({col: team_name_dict})
    tab = tab[tab['team_home'].isin(team_name_dict.values())]
    tab = tab[tab['team_away'].isin(team_name_dict.values())].reset_index(drop=True)
    tab['season'] = tab['id_season'].apply(lambda x: int(x[3:5]))
    tab['is_playoff'] = tab['id_season'].apply(lambda x: 1 if x[6:8] == 'PO' else 0)
    tab['start_time'] = pd.to_datetime(tab['start_time'], format='%d.%m.%Y %H:%M')
    tab['day'] = tab['start_time'].dt.date
    tab['num_day'] = tab[['season', 'day']].groupby('season').rank(method='dense').astype(int)
    t = tab.copy()

    def elo_rating(row):
        '''получаем значения рейтинга для команд из словаря'''
        R_H = team_elo_dict.get(row['team_home'])
        R_A = team_elo_dict.get(row['team_away'])

        '''эти значения сразу записываем как данные по матчу'''
        row['elo_home'] = R_H
        row['elo_away'] = R_A
        row['elo_mean_league'] = pd.Series([team_elo_dict[k] for k in team_elo_dict]).mean()

        '''если матч плей офф, то тогда делаем поправку для разницы рейтингов между командами,
        исходя из предположеyий, что в важных матчах фаворит усиливает свое премущество.
        Домашняя команда по-умолчанию получает +50 к рейтингу Эло'''
        if row['is_playoff'] == 1:
            EloDf = (R_H + 50 - R_A) * 1.25
        else:
            EloDf = R_H + 50 - R_A

        '''Делаем расчет рейтинга по результату матча для обоих команд
        K - кф используйщийся в ретинге Эло. Подбирается эксперементально. Для хоккея оптимально 6
        H - множитель, учитывающий разницу голов в матче
        PF - множитель, учитывающий предматчевый вероятности победы команд
        AC - множитель, уменьшающий, набор очков в матчах, где побеждает команда с бОльшим рейтингом Эло
        shift - изменение рейтинга Эло по результату матча. Прибавится к рейтингу победителя и вычтится у проигравшего'''
        if row['G_home'] > row['G_away']:
            p_H = 1 / (10 ** ((-EloDf) / 400) + 1)
            K = 6
            H = 0.6686 * np.log(row['G_home'] - row['G_away']) + 0.8048
            PF = 1 - p_H
            if R_H > R_A:
                AC = 2.05 / ((R_H - R_A) * 0.001 + 2.05)
            else:
                AC = 1
            shift = K * H * PF * AC
            team_elo_dict.update({row['team_home']: R_H + shift, row['team_away']: R_A - shift})
        else:
            p_A = 1 / (10 ** ((EloDf) / 400) + 1)
            K = 6
            H = 0.6686 * np.log(row['G_away'] - row['G_home']) + 0.8048
            PF = 1 - p_A
            if R_A > R_H:
                AC = 2.05 / ((R_A - R_H) * 0.001 + 2.05)
            else:
                AC = 1
            shift = K * H * PF * AC
            '''лбновляем данные по рейтингам в словаре'''
            team_elo_dict.update({row['team_home']: R_H - shift, row['team_away']: R_A + shift})
        #     print(f"{row['team_home']} против {row['team_away']} Elo:{R_H:0.1f}-{R_A:0.1f}, счет матча: {row['G_home']}-{row['G_away']}, изменение Elo:{shift:0.1f}")
        return row

    def rating_adjustment(team_elo_dict):
        mean_rating = pd.Series([team_elo_dict[k] for k in team_elo_dict]).mean()
        for k, v in team_elo_dict.items():
            team_elo_dict[k] = v * 0.9 + mean_rating * 0.1
        return team_elo_dict

    first_season_team = t[t['season'] == 9]['team_home']
    team_elo_dict = dict(zip(first_season_team.unique(), [1500] * len(first_season_team.unique())))
    previous_season = set(first_season_team.unique())
    df = t[t['season'] == 9].apply(elo_rating, axis=1, result_type='expand')
    for s in t['season'].unique():
        season = t[t['season'] == s]
        team_set = set(season['team_home'].unique())
        if s > 9:
            team_elo_dict = rating_adjustment(team_elo_dict)
            new_team = team_set - previous_season
            if len(new_team) > 0:
                team_elo_dict.update(zip(new_team, [1450] * len(new_team)))
            new_season = season.apply(elo_rating, axis=1, result_type='expand')
            df = pd.concat([df, new_season])

        new_team = team_set - previous_season
        if len(new_team) > 0:
            team_elo_dict.update(zip(new_team, [1450] * len(new_team)))

        previous_season = team_set

    data = df[['SOG_home_RT', 'SOG_away_RT', 'season', 'num_day', 'start_time',
               'team_home', 'team_away', 'G_home_RT', 'G_away_RT', 'elo_home', 'elo_away', 'is_playoff']].copy()
    data['elo_home_diff_mean'] = df['elo_home'] - df['elo_mean_league']
    data['elo_away_diff_mean'] = df['elo_away'] - df['elo_mean_league']

    def get_team_stats(df):
        home_games = df[['SOG_home_RT', 'SOG_away_RT', 'season', 'num_day', 'start_time',
                         'team_home', 'team_away', 'G_home_RT', 'G_away_RT', 'elo_home',
                         'elo_away', 'is_playoff', 'elo_home_diff_mean', 'elo_away_diff_mean']].copy()
        home_games['loc_first_team'] = 'H'
        home_games.columns = ['SOG_1', 'SOG_2', 'season', 'num_day', 'start_time',
                              'team_1', 'team_2', 'G_1', 'G_2', 'elo_1', 'elo_2', 'is_playoff',
                              'elo_1_diff_mean', 'elo_2_diff_mean', 'loc_first_team']

        away_games = df[['SOG_away_RT', 'SOG_home_RT', 'season', 'num_day', 'start_time',
                         'team_away', 'team_home', 'G_away_RT', 'G_home_RT', 'elo_away',
                         'elo_home', 'is_playoff', 'elo_away_diff_mean', 'elo_home_diff_mean']].copy()
        away_games['loc_first_team'] = 'A'
        away_games.columns = ['SOG_1', 'SOG_2', 'season', 'num_day', 'start_time',
                              'team_1', 'team_2', 'G_1', 'G_2', 'elo_1', 'elo_2', 'is_playoff',
                              'elo_1_diff_mean', 'elo_2_diff_mean', 'loc_first_team']

        team_stats = pd.concat([home_games, away_games])
        team_stats = team_stats.sort_values('start_time')
        return team_stats

    team_stats = get_team_stats(data)


    def rolling_averages(group, cols, new_cols5, new_cols10, new_cols15):
        group = group.sort_values('start_time')
        rolling_stats_5 = group[cols].rolling(5, closed='left').mean()
        rolling_stats_10 = group[cols].rolling(10, closed='left').mean()
        rolling_stats_15 = group[cols].rolling(15, closed='left').mean()
        #     rolling_stats_30 = group[cols].rolling(30, closed='left').mean()
        group[new_cols5] = rolling_stats_5
        group[new_cols10] = rolling_stats_10
        group[new_cols15] = rolling_stats_15
        #     group[new_cols30] = rolling_stats_30
        group = group.dropna(subset=[*new_cols5, *new_cols10, *new_cols15])
        return group

    cols_t1 = ['G_1', 'G_2', 'elo_1', 'elo_2', 'SOG_1', 'SOG_2', 'is_playoff']
    cols_t1_home = ['G_1', 'G_2', 'SOG_1', 'SOG_2', 'is_playoff']
    cols_t2 = ['G_2', 'G_1', 'elo_2', 'elo_1', 'SOG_2', 'SOG_1', 'is_playoff']
    cols_t2_away = ['G_2', 'G_1', 'SOG_2', 'SOG_1', 'is_playoff']
    cols = ['GF', 'GA', 'eloF', 'eloA', 'SOGF', 'SOGA', 'is_playoff']
    cols_loc = ['GF', 'GA', 'SOGF', 'SOGA', 'is_playoff']
    new_cols5_t1 = [f"{c}_t1_roll_5" for c in cols]
    new_cols10_t1 = [f"{c}_t1_roll_10" for c in cols]
    new_cols15_t1 = [f"{c}_t1_roll_15" for c in cols]
    # new_cols30_t1 = [f"{c}_t1_roll_30" for c in cols]
    new_cols5_t1_home = [f"{c}_t1_roll_5_home" for c in cols_loc]
    new_cols10_t1_home = [f"{c}_t1_roll_10_home" for c in cols_loc]
    new_cols15_t1_home = [f"{c}_t1_roll_15_home" for c in cols_loc]
    # new_cols30_t1_home = [f"{c}_t1_roll_30_home" for c in cols_loc]
    new_cols5_t2 = [f"{c}_t2_roll_5" for c in cols]
    new_cols10_t2 = [f"{c}_t2_roll_10" for c in cols]
    new_cols15_t2 = [f"{c}_t2_roll_15" for c in cols]
    # new_cols30_t2 = [f"{c}_t2_roll_30" for c in cols]
    new_cols5_t2_away = [f"{c}_t2_roll_5_away" for c in cols_loc]
    new_cols10_t2_away = [f"{c}_t2_roll_10_away" for c in cols_loc]
    new_cols15_t2_away = [f"{c}_t2_roll_15_away" for c in cols_loc]
    # new_cols30_t2_away = [f"{c}_t2_roll_30_away" for c in cols_loc]

    '''Исправлено для демонстрации вне сезона'''
    test_data = {
        'id_season': ['23-24_PO'],
        'id_regular': [90],
        'team_home': ['LOK'],
        'team_away': ['MMG'],
        'start_time': ['17.06.2024 19:00']
    }

    new = pd.DataFrame(test_data)
    # new = pd.read_csv(new_match)
    for col in ['team_home', 'team_away']:
        new = new.replace({col: team_name_dict})
    new = new[new['team_home'].isin(team_name_dict.values())]
    new = new[new['team_away'].isin(team_name_dict.values())].reset_index(drop=True)
    m = {
        'января': '01',
        'февраля': '02',
        'марта': '03',
        'апреля': '04',
        'мая': '05',
        'июня': '06',
        'июля': '07',
        'августа': '08',
        'сентября': '09',
        'октября': '10',
        'ноября': '11',
        'декабря': '12'
    }

    def date_processing(row):
        num_date = row['start_time'].split(' ')[0]
        num_month = row['start_time'].split(' ')[1]
        num_month = num_month.replace(num_month, m[num_month])
        num_year = row['start_time'].split(' ')[2]
        msk_time = row['start_time'].split(' ')[3]
        row['start_time'] = num_date + '.' + num_month + '.' + num_year + ' ' + msk_time
        return row

    # new = new.apply(date_processing, axis=1)
    new['season'] = new['id_season'].apply(lambda x: int(x[3:5]))
    new['is_playoff'] = new['id_season'].apply(lambda x: 1 if x[6:8] == 'PO' else 0)
    new['start_time'] = pd.to_datetime(new['start_time'], format='%d.%m.%Y %H:%M')
    new['day'] = new['start_time'].dt.date
    d = tab[tab['id_season'] == new.loc[0]['id_season']][new.columns]
    d = pd.concat([d, new])
    d['num_day'] = d[['season', 'day']].groupby('season').rank(method='dense').astype(int)
    new = d[d.index.isin(new.index)].copy()
    new['elo_mean_league'] = df.iloc[-1, -1]
    new = new.drop(['id_season', 'id_regular', 'day'], axis=1)

    def get_new_feature(new, data, day='tm'):
        if day == 'td':
            new = new[new['start_time'].dt.date == datetime.date.today()].copy()
        elif day == 'tm':
            new = new[new['start_time'].dt.date == datetime.date.today() + datetime.timedelta(days=1)].copy()
        new[['SOG_home_RT', 'SOG_away_RT', 'G_home_RT', 'G_away_RT']] = 0
        new['elo_home'] = new['team_home'].apply(lambda x: team_elo_dict.get(x))
        new['elo_away'] = new['team_away'].apply(lambda x: team_elo_dict.get(x))
        new['elo_home_diff_mean'] = new['elo_home'] - new['elo_mean_league']
        new['elo_away_diff_mean'] = new['elo_away'] - new['elo_mean_league']
        new = new.drop(['elo_mean_league'], axis=1)
        new_rolling = pd.concat([data.tail(1000), new])
        team_stats = get_team_stats(new_rolling)

        matches_rolling_t1 = team_stats.groupby('team_1').apply(
            lambda x: rolling_averages(x, cols_t1, new_cols5_t1, new_cols10_t1, new_cols15_t1))
        matches_rolling_t1 = matches_rolling_t1.droplevel('team_1')

        matches_rolling_t1_home = team_stats[team_stats['loc_first_team'] == 'H'].groupby('team_1').apply(
            lambda x: rolling_averages(x, cols_t1_home, new_cols5_t1_home, new_cols10_t1_home,
                                       new_cols15_t1_home))
        matches_rolling_t1_home = matches_rolling_t1_home.droplevel('team_1')

        matches_rolling_t2 = team_stats.groupby('team_2').apply(
            lambda x: rolling_averages(x, cols_t2, new_cols5_t2, new_cols10_t2, new_cols15_t2))
        matches_rolling_t2 = matches_rolling_t2.droplevel('team_2')

        matches_rolling_t2_away = team_stats[team_stats['loc_first_team'] == 'H'].groupby('team_2').apply(
            lambda x: rolling_averages(x, cols_t2_away, new_cols5_t2_away, new_cols10_t2_away,
                                       new_cols15_t2_away))
        matches_rolling_t2_away = matches_rolling_t2_away.droplevel('team_2')

        matches_rolling_t = pd.merge(matches_rolling_t1, matches_rolling_t2, on=team_stats.columns.to_list())

        matches_rolling_t_loc = pd.merge(matches_rolling_t1_home, matches_rolling_t2_away,
                                         on=team_stats.columns.to_list())

        matches_rolling_t = matches_rolling_t.sort_values('start_time')
        matches_rolling_t_loc = matches_rolling_t_loc.sort_values('start_time').reset_index(drop=True)
        matches_rolling_t = matches_rolling_t[matches_rolling_t['loc_first_team'] == 'H'].reset_index(drop=True)

        matches_rolling = pd.merge(matches_rolling_t, matches_rolling_t_loc, on=team_stats.columns.to_list())

        matches_rolling = matches_rolling.sort_values('start_time').reset_index(drop=True)

        if day == 'td':
            new_match = matches_rolling[matches_rolling['start_time'].dt.date == datetime.date.today()]
        elif day == 'tm':
            new_match = matches_rolling[
                matches_rolling['start_time'].dt.date == datetime.date.today() + datetime.timedelta(days=1)]

        return new_match

    new_match = get_new_feature(new, data, 'tm')

    X_new = new_match.drop(['SOG_1', 'SOG_2', 'start_time', 'G_1', 'G_2', 'loc_first_team'], axis=1)
    shot_model = pickle.load(open('shot_model', 'rb'))
    predict = shot_model.predict(X_new)
    new_match[['SOG_1_pred', 'SOG_2_pred']] = pd.DataFrame(
        predict, columns=['SOG_1_pred', 'SOG_2_pred'], index=new_match.index)

    def print_predict(row):
        home = row['team_1']
        away = row['team_2']
        start_time = row['start_time']
        SOG_1_pred = row['SOG_1_pred']
        SOG_2_pred = row['SOG_2_pred']
        total = SOG_1_pred + SOG_2_pred
        handicap = (SOG_1_pred - SOG_2_pred) * -1
        first_row = f'{start_time} Матч {home} - {away}\n'
        second_row = f'Прогнозируемое кол-во бросков {SOG_1_pred:0.1f} - {SOG_2_pred:0.1f}\n'
        third_row = f'Прогнозируемый тотал бросков {total:0.1f}, Прогнозируемая фора {handicap:0.1f}\n'
        print(first_row + second_row + third_row)
        # bot.send_message(config['CHANNEL_LOGIN'], first_row + second_row + third_row)

    new_match.apply(print_predict, axis=1)


# if __name__ == '__shot_ml__':
#     main_ml('general_info.csv', 'feature_match.csv')
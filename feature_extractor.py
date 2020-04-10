import numpy as np
import pandas as pd
import matplotlib as plt
import seaborn as sns
import datetime as dt
import math
from scipy.spatial.distance import cdist

def is_event_creator_friend(row):
    if (type(row['friends']) != str):
        return False
    
    if row['creator_id'] in row['friends'].split():
        return True
    else:
        return False
    
def time_to_event(row):
    start_time = dt.datetime.strptime(row['start_time'][:19], "%Y-%m-%dT%H:%M:%S")
    not_time = dt.datetime.strptime(row['timestamp'][:19], "%Y-%m-%d %H:%M:%S")
    diff_time = not_time - start_time
    return diff_time.total_seconds()

def add_event_creator_friend_timestamp_feature(train_df, events_df, friends_df):
    events_df = events_df[['event_id', 'user_id', 'start_time']]
    merged_df = pd.merge(train_df, events_df, how='inner', left_on='event', right_on='event_id', suffixes=('', '_event'))
    
    merged_df = merged_df.rename(columns={'user_id': 'creator_id'})
    merged_df2 = pd.merge(merged_df, friends_df, how='inner', left_on='user', right_on='user', suffixes=('','_friends'))
    
    merged_df2['is_creator_friend'] = merged_df2.apply (lambda row: is_event_creator_friend(row), axis=1)
    merged_df2 = merged_df2.drop(columns=['friends'])
    
    merged_df2['not_start_diff'] = merged_df2.apply (lambda row: time_to_event(row), axis=1)
    return merged_df2
    
def is_same_city(row):
    if (type(row['location']) != str) or (type(row['city']) != str):
        return False
    
    if row['location'].lower() in 'na' or row['city'].lower() in 'na':
        return False
    
    if str(row['city']).lower() in row['location'].lower():
        return True
    else:
        return False

def is_same_country(row):
    if (type(row['location']) != str) or (type(row['country']) != str):
        return False
    
    if row['location'].lower() in 'na' or row['country'].lower() in 'na':
        return False
        
    if row['country'].lower() in row['location'].lower():
        return True
    else:
        return False
    
    return row

    
def add_location_features(train_df, events_df, users_df):
    events_df = events_df[['event_id', 'city', 'country']]
    merged_df = pd.merge(train_df, events_df, how='inner', left_on='event', right_on='event_id', suffixes=('', '_event'))
    
    merged_df2 = pd.merge(merged_df, users_df, how='inner', left_on='user', right_on='user_id', suffixes=('','_user'))
    
    merged_df2['same_city'] =  merged_df2.apply (lambda row: is_same_city(row), axis=1)
    merged_df2['same_country'] = merged_df2.apply (lambda row: is_same_country(row), axis=1)
    merged_df2 = merged_df2[['timestamp', 'interested', 'not_interested', 'event', 'same_city',
                            'same_country', 'user']]
    return merged_df2

def add_gender_age(train_df, users_df):
    users_df = users_df[['user_id', 'birthyear', 'gender']]
    merged_df = pd.merge(train_df, users_df, how='inner', left_on='user', right_on='user_id')
    cur_year = dt.datetime.now().year
    merged_df = merged_df.rename(columns = {'birthyear': 'age'})
    merged_df['age'] = merged_df['age'].astype(str).replace('None', np.nan)
    merged_df['age'] = merged_df['age'].ffill().bfill()
    merged_df['age'] = cur_year - pd.to_numeric(merged_df['age'])
    merged_df['gender'] = merged_df['gender'].ffill().bfill()
    return merged_df

def get_event_attendee_nums(train_df, event_attendees_df):
    merged_df = pd.merge(train_df, event_attendees_df, how='inner', left_on='event', right_on='event')
    merged_df['yes'] = merged_df['yes'].str.len()
    merged_df['no'] = merged_df['no'].str.len()
    merged_df['maybe'] = merged_df['maybe'].str.len()
    merged_df['invited'] = merged_df['invited'].str.len()
    merged_df['f4'] = merged_df['no'] / merged_df['yes']
    merged_df['f5'] = merged_df['maybe'] / merged_df['yes']
    merged_df['f6'] = merged_df['invited'] / merged_df['yes']

    return merged_df

def get_friends_status(row, event_attendees_df):
    # print(row)
    event = row['event']
    friends = str(row['friends']).split(' ')
    #
    ppl_attending = str(event_attendees_df.iloc[np.where(event_attendees_df['event']==event)[0][0]]['yes']).split(' ')
    ppl_not_attending = str(event_attendees_df.iloc[np.where(event_attendees_df['event']==event)[0][0]]['no']).split(' ')
    ppl_maybe_attending = str(event_attendees_df.iloc[np.where(event_attendees_df['event']==event)[0][0]]['maybe']).split(' ')
    ppl_invited = str(event_attendees_df.iloc[np.where(event_attendees_df['event']==event)[0][0]]['invited']).split(' ')
    #
    friends_attending = list(set(friends).intersection(set(ppl_attending)))
    friends_not_attending = list(set(friends).intersection(set(ppl_not_attending)))
    friends_maybe_attending = list(set(friends).intersection(set(ppl_maybe_attending)))
    friends_invited = list(set(friends).intersection(set(ppl_invited)))
    # 
    # row['friends_attending'] = len(friends_attending)
    # print(row)
    # return row
    return [len(friends_attending), len(friends_not_attending), len(friends_maybe_attending), len(friends_invited)]

def get_friends_attendee_nums(train_df, friends_df, event_attendees_df):
    # merge train_df with friends_df
    merged_df = pd.merge(train_df, friends_df, how='inner', left_on='user', right_on='user')
    merged_df['f7'], merged_df['f8'], merged_df['f9'], merged_df['f10'] = zip(*merged_df.apply(lambda row: get_friends_status(row, event_attendees_df), axis=1))
    # convert friends column to number of friends
    merged_df['friends'] = merged_df['friends'].str.len()
    return merged_df

def get_friends_attendee_ratios(train_df):
    train_df['f11'] = train_df['f8'] / train_df['f7']
    train_df['f12'] = train_df['f9'] / train_df['f7']
    train_df['f13'] = train_df['f10'] / train_df['f7']
    train_df['f14'] = train_df['f7'] / train_df['friends']
    train_df['f15'] = train_df['f8'] / train_df['friends']
    train_df['f16'] = train_df['f9'] / train_df['friends']
    train_df['f17'] = train_df['f10'] / train_df['friends']
    train_df['f18'] = train_df['no'] / train_df['invited']
    train_df = train_df.replace([np.inf, -np.inf, np.nan], 0)
    return train_df
    
def get_user_attendance(event_attendees_df, events_df):
    events_df = events_df.rename(columns = {'event_id': 'event'})
    events_df = events_df['event']
    event_attendees_df = pd.merge(event_attendees_df, events_df, on = 'event')

    # process yes
    user_attendance_yes = {}
    user_attendance_maybe = {}
    user_attendance_no = {}
    user_attendance_invited = {} 

    for k, row in event_attendees_df.iterrows():
        if not pd.isnull(row.yes):
            users = row.yes.split()
            for user in users:
                if user in user_attendance_yes:
                    user_attendance_yes[user].append(row.event)
                else:
                    user_attendance_yes[user] = [row.event]
        
        if not pd.isnull(row.maybe):
            users = row.maybe.split()
            for user in users:
                if user in user_attendance_maybe:
                    user_attendance_maybe[user].append(row.event)
                else:
                    user_attendance_maybe[user] = [row.event]
        
        if not pd.isnull(row.no):
            users = row.no.split()
            for user in users:
                if user in user_attendance_no:
                    user_attendance_no[user].append(row.event)
                else:
                    user_attendance_no[user] = [row.event]

        if not pd.isnull(row.invited):
            users = row.invited.split()
            for user in users:
                if user in user_attendance_invited:
                    user_attendance_invited[user].append(row.event)
                else:
                    user_attendance_invited[user] = [row.event]

    user_a_list = list(user_attendance_yes.items())
    user_attendance_yes = pd.DataFrame(user_a_list, columns=['user', 'yes'])
    user_attendance_yes = user_attendance_yes.astype({'user':'int64'})

    user_a_list = list(user_attendance_maybe.items())
    user_attendance_maybe = pd.DataFrame(user_a_list, columns=['user', 'maybe'])
    user_attendance_maybe = user_attendance_maybe.astype({'user':'int64'})

    user_a_list = list(user_attendance_no.items())
    user_attendance_no = pd.DataFrame(user_a_list, columns=['user', 'no'])
    user_attendance_no = user_attendance_no.astype({'user':'int64'})

    user_a_list = list(user_attendance_invited.items())
    user_attendance_invited = pd.DataFrame(user_a_list, columns=['user', 'invited'])
    user_attendance_invited = user_attendance_invited.astype({'user':'int64'})

    return (user_attendance_yes, user_attendance_maybe, user_attendance_no, user_attendance_invited)

def get_event_centroids(event_clusters, events):
    centroids = (event_clusters[event_clusters['event_id'].isin(events)]['centroid']).to_numpy(dtype=object)
    return np.vstack(centroids[:])

def get_cluster_sim_by_user_attendance(train_data, event_clusters, user_attendance_yes, user_attendance_maybe, user_attendance_no, user_attendance_invited):
    n = train_data.shape[0]
    sim_yes_cluster = np.zeros(n)
    sim_maybe_cluster = np.zeros(n)
    sim_no_cluster = np.zeros(n)
    sim_invited_cluster = np.zeros(n)

    train_interim = pd.merge(train_data, user_attendance_yes, how = 'left', on = 'user', suffixes=('', '_events'))
    train_interim = pd.merge(train_interim, user_attendance_maybe, how = 'left', on = 'user', suffixes=('', '_events'))
    train_interim = pd.merge(train_interim, user_attendance_no, how = 'left', on = 'user', suffixes=('', '_events'))
    train_interim = pd.merge(train_interim, user_attendance_invited, how = 'left', on = 'user', suffixes=('', '_events'))

    for k, row in train_interim.iterrows():
        cur_user = row.user
        cur_event = row.event
        cur_cluster_center = get_event_centroids(event_clusters, [cur_event])

        # similarity by users interested - yes
        isna = pd.isnull(row.yes_events)
        if (isinstance(isna, (bool)) and isna == True) or (not isinstance(isna, (bool)) and isna.all()):
            sim_yes_cluster[k] = None
        else:
            events = row.yes_events
            events_centers = get_event_centroids(event_clusters, events)
            dist = np.sum(cdist(cur_cluster_center, events_centers))/events_centers.shape[0]
            sim_yes_cluster[k] = dist

        # similarity by users interested - maybe
        isna = pd.isnull(row.maybe_events)
        if (isinstance(isna, (bool)) and isna == True) or (not isinstance(isna, (bool)) and isna.all()):
            sim_maybe_cluster[k] = None
        else:
            events = row.maybe_events
            events_centers = get_event_centroids(event_clusters, events)
            dist = np.sum(cdist(cur_cluster_center, events_centers))/events_centers.shape[0]
            sim_maybe_cluster[k] = dist

        # similarity by users interested - no
        isna = pd.isnull(row.no_events)
        if (isinstance(isna, (bool)) and isna == True) or (not isinstance(isna, (bool)) and isna.all()):
            sim_no_cluster[k] = None
        else:
            events = row.no_events
            events_centers = get_event_centroids(event_clusters, events)
            dist = np.sum(cdist(cur_cluster_center, events_centers))/events_centers.shape[0]
            sim_no_cluster[k] = dist

        # similarity by users interested - invited
        isna = pd.isnull(row.invited_events)
        if (isinstance(isna, (bool)) and isna == True) or (not isinstance(isna, (bool)) and isna.all()):
            sim_invited_cluster[k] = None
        else:
            events = row.invited_events
            events_centers = get_event_centroids(event_clusters, events)
            dist = np.sum(cdist(cur_cluster_center, events_centers))/events_centers.shape[0]
            sim_invited_cluster[k] = dist

    train_data['sim_yes_cluster'] = sim_yes_cluster
    train_data['sim_maybe_cluster'] = sim_maybe_cluster
    train_data['sim_no_cluster'] = sim_no_cluster
    train_data['sim_invited_cluster'] = sim_invited_cluster

    return train_data
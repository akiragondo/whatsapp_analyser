import pandas as pd
import re
import numpy as np
from sklearn.preprocessing import OrdinalEncoder
import streamlit as st


def preprocess_df(df):
    df['Message Length'] = df['Message'].apply(lambda x: len(x.split(' ')))
    for subject in df['Subject'].unique():
        df[subject] = df['Subject'].apply(lambda x: 1 if x == subject else 0)
        df[f"{subject}_mlength"] = df[subject].values * df['Message Length']

    df['Formatted Date'] = df.index.strftime('%b - %y').values

    conv_codes, conv_changes = cluster_into_conversations(df)
    df['Conv code'] = conv_codes
    df['Conv change'] = conv_changes
    is_reply, sender_changes = find_replies(df)
    df['Is reply'] = is_reply
    df['Sender change'] = sender_changes

    reply_times, indices = calculate_times_on_trues(df, 'Is reply')
    reply_times_df_list = []
    reply_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            reply_times_df_list.append(reply_times[reply_time_index].astype("timedelta64[m]").astype("float"))
            reply_time_index = reply_time_index + 1
        else:
            reply_times_df_list.append(0)

    df['Reply time'] = reply_times_df_list

    inter_conv_times, indices = calculate_times_on_trues(df, 'Conv change')
    inter_conv_times_df_list = []
    inter_conv_time_index = 0
    for i in range(0, len(df)):
        if i in indices:
            inter_conv_times_df_list.append(
                inter_conv_times[inter_conv_time_index].astype("timedelta64[m]").astype("float"))
            inter_conv_time_index = inter_conv_time_index + 1
        else:
            inter_conv_times_df_list.append(0)

    df['Inter conv time'] = inter_conv_times_df_list

    df['Hour'] = df['Date'].apply(lambda x: x.strftime('%H'))
    return df

def create_df_from_raw_file(raw_file_content):
    rows = raw_file_content.split('\\n')
    pattern_matches = pd.DataFrame([
        ['English', '^\d*/\d*/\d*'],
        ['German', '^\[\d*.\d*.\d*'],
    ], columns= ['Country', 'Pattern'])
    pattern_matches['Number_of_matches'] = pattern_matches['Pattern'].apply(lambda x : len([row for row in rows if re.match(x, row)]))
    if pattern_matches['Number_of_matches'].max() < 1000:
        st.error('These analysis need more data to work, at least 1000 messages exchanged, please come back after chatting to that person more!')
        return None
    else:
        matched_country = pattern_matches.sort_values(by = 'Number_of_matches', ascending=False)['Country'].values[0]
        if matched_country == 'English':
            valid_rows = [row for row in rows if re.match('^\d*/\d*/\d*', row)]
            ignore_rows = 10
            datetime = pd.DatetimeIndex([row.split(' - ')[0] for row in valid_rows[ignore_rows:]])
            subjects = [row.split(', ')[1].split(' - ')[1].split(':')[0] for row in valid_rows[ignore_rows:]]
            messages = [(':'.join(row.split(', ')[1].split(' - ')[1].split(': ')[1:])) for row in
                        valid_rows[ignore_rows:]]
            df = pd.DataFrame(
                zip(pd.to_datetime(datetime), subjects, messages),
                columns=['Date', 'Subject', 'Message'],
                index=datetime
            )
        elif matched_country == 'German':
            valid_rows = [row for row in rows if re.match('^\[\d*.\d*.\d*', row)]
            ignore_rows = 10
            datetime = pd.DatetimeIndex([row.split('] ')[0][1:] for row in valid_rows[ignore_rows:]], dayfirst=True)
            subjects = [row.split('] ')[1].split(':')[0] for row in valid_rows[ignore_rows:]]
            messages = [(':'.join(row.split('] ')[1].split(':')[1:])) for row in
                        valid_rows[ignore_rows:]]
            df = pd.DataFrame(
                zip(pd.to_datetime(datetime), subjects, messages),
                columns=['Date', 'Subject', 'Message'],
                index=datetime
            )

        return df


def get_df_from_data(raw_file_content):
    df = create_df_from_raw_file(raw_file_content)
    preprocessed = preprocess_df(df)
    return preprocessed


def cluster_into_conversations(df : pd.DataFrame, inter_conversation_threshold_time: int = 60):
    threshold_time_mins = np.timedelta64(inter_conversation_threshold_time, 'm')
    conv_delta = df.index.values - np.roll(df.index.values, 1)
    conv_delta[0] = 0
    conv_changes = conv_delta > threshold_time_mins
    conv_changes_indices = np.where(conv_changes)[0]
    conv_codes = []
    last_conv_change = 0
    for i, conv_change in enumerate(conv_changes_indices):
        conv_codes.extend([i]*(conv_change - last_conv_change))
        last_conv_change = conv_change

    conv_codes = pad_list_to_value(conv_codes, len(df), conv_codes[-1])
    conv_changes = pad_list_to_value(conv_changes, len(df), False)

    return conv_codes, conv_changes


def pad_list_to_value(input_list : list, length : int, value):
    assert(length >= len(input_list))
    output_list = list(input_list)
    padding = [value]*(length - len(output_list))
    output_list.extend(padding)
    return np.array(output_list)


def find_replies(df : pd.DataFrame):
    assert('Conv code' in df.columns)
    assert('Conv change' in df.columns)
    assert('Subject' in df.columns)
    message_senders = OrdinalEncoder().fit_transform(df['Subject'].values.reshape(-1,1))
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    is_reply = sender_changed & ~df['Conv change']
    return is_reply, sender_changed


def calculate_times_on_trues(df : pd.DataFrame, column : str):
    assert(column in df.columns)
    true_indices = np.where(df[column])[0]
    inter_conv_time = [df.index.values[ind] - df.index.values[ind-1] for ind in true_indices]
    return inter_conv_time, true_indices
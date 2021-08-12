import pandas as pd
import re

def get_df_from_data(raw_file_content):
    rows = raw_file_content.split('\\n')
    valid_rows = [row for row in rows if re.match('^\d*/\d*/\d*', row)]
    ignore_rows = 10
    dates = [row.split(',')[0] for row in valid_rows[ignore_rows:]]
    hours = [row.split(', ')[1].split(' - ')[0] for row in valid_rows[ignore_rows:]]
    subjects = [row.split(', ')[1].split(' - ')[1].split(':')[0] for row in valid_rows[ignore_rows:]]
    messages = [(':'.join(row.split(', ')[1].split(' - ')[1].split(': ')[1:])) for row in
                valid_rows[ignore_rows:]]
    df = pd.DataFrame(
        zip(hours, subjects, messages),
        columns=['Hour', 'Subject', 'Message'],
        index=pd.DatetimeIndex(dates)
    )
    df['Message Length'] = df['Message'].apply(lambda x: len(x.split(' ')))
    for subject in df['Subject'].unique():
        df[subject] = df['Subject'].apply(lambda x: 1 if x == subject else 0)
        df[f"{subject}_mlength"] = df[subject].values*df['Message Length']

    df['Formatted Date'] = df.index.strftime('%b - %y').values
    return df

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class GraphComponents:
    def __init__(self, params):
        plt.style.use('seaborn')
        self.params = params

    def _create_wide_area_fig(self,df : pd.DataFrame, legend : bool = True):
        fig, ax = plt.subplots(figsize = self.params['wide_figsize'])
        df.plot(
            kind = 'area',
            alpha = self.params['area_alpha'],
            cmap = self.params['cmap'],
            ax = ax,
            stacked = True
        )
        ax.patch.set_alpha(0.0)
        fig.patch.set_alpha(0.0)
        if legend:
            ax.legend(self.params['subjects'])
        return fig

    def _create_narrow_bar_fig(self, df : pd.DataFrame, buffer_perc : float):
        fig, ax = plt.subplots(figsize=self.params['narrow_figsize'])
        df.plot(kind='bar', color=self.params['colors'], ax=ax, alpha = 0.96)
        ax.patch.set_alpha(0.0)
        fig.patch.set_alpha(0.0)
        return fig

    def create_narrow_pie_fig(self, df : pd.DataFrame):
        fig1, ax = plt.subplots(figsize=self.params['narrow_figsize'])
        df.plot(kind='pie', cmap=self.params['cmap'], ax=ax, autopct='%1.1f%%', explode=[0.015] * len(df.index.unique()))
        centre_circle = plt.Circle((0, 0), 0.80, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        ax.patch.set_alpha(0.0)
        fig.patch.set_alpha(0.0)
        ax.set_ylabel('')
        return fig

    def create_messages_per_week_graph(self, df : pd.DataFrame):
        #Makes first graph
        date_df = df.resample('W').sum()[self.params['subjects']]
        fig = self._create_wide_area_fig(date_df)

        max_message_count = date_df[self.params['subjects']].sum(axis = 1).max()
        max_message_count_date = date_df.index[date_df[self.params['subjects']].sum(axis = 1).argmax()]
        return fig, max_message_count, max_message_count_date

    def create_average_wpm_graph(self, df : pd.DataFrame):
        other_y_columns = [f"{subject}_mlength" for subject in df['Subject'].unique()]
        date_avg_df = df[other_y_columns].resample('W').mean()
        fig = self._create_wide_area_fig(date_avg_df)
        return fig

    def average_reply_time_graph(self, df):
        fig, ax = plt.subplots(figsize=self.params['wide_figsize'])
        filtered_sender_changes = df[df['Is reply']]
        for index, subject in enumerate(self.params['subjects']):
            subject_df = filtered_sender_changes[filtered_sender_changes['Subject'] == subject].resample('W').mean().fillna(0)['Reply time']
            subject_df.plot(kind='line', alpha=0.95, cmap=self.params['cmap'], ax=ax, label=subject, color=self.params['colors'][index], marker='o',
                            markersize=5)
        ax.patch.set_alpha(0.0)
        return fig

    def average_conversation_hour_graph(self, df):
        hour_df = df.groupby('Hour').count()['Message'] / (df['Date'].values[-1] - df['Date'].values[0]).astype(
            'timedelta64[D]').astype('int')
        fig = self._create_wide_area_fig(hour_df, legend = False)
        return fig

    def conversation_starter_graph(self, df):
        subject_df = df[df['Conv change']].groupby('Subject').count()['Reply time']
        fig = self.create_narrow_pie_fig(subject_df)
        most_messages_winner = subject_df.index[subject_df.argmax()]
        return fig,most_messages_winner

    def reply_time_aggregated_graph(self, df):
        avg_msg_length = df.groupby('Subject').mean()['Reply time']
        fig = self._create_narrow_bar_fig(avg_msg_length, 0.05)

        most_wpm_winner = avg_msg_length.index[avg_msg_length.argmax()]
        return fig,most_wpm_winner

    def message_count_aggregated_graph(self, df):
        subject_df = df.groupby('Subject').count()['Message'].sort_values(ascending=False)
        most_messages_winner = subject_df.index[subject_df.argmax()]
        fig = self.create_narrow_pie_fig(subject_df)
        return fig, most_messages_winner

    def message_size_aggregated_graph(self, df):
        avg_msg_length = df.groupby('Subject').mean()['Message Length']

        most_wpm_winner = avg_msg_length.index[avg_msg_length.argmax()]
        fig = self._create_narrow_bar_fig(avg_msg_length, 0.01)
        return fig, most_wpm_winner

    def conversation_size_aggregated_graph(self, df):
        conversations_df = df.groupby('Conv code').agg(count=('Conv code', 'size'),
                                                       mean_date=('Date', 'mean')).reset_index()
        conversations_df.index = conversations_df['mean_date']
        conversations_df = conversations_df.resample('W').mean().fillna(0)
        print(conversations_df.head(50))
        fig, ax = plt.subplots(figsize=self.params['wide_figsize'])
        ax.plot(conversations_df.index, conversations_df['count'], color=self.params['colors'][0], alpha=0.7)
        ax.fill_between(x=conversations_df.index, y1=conversations_df['count'], color=self.params['colors'][0], alpha=0.5)
        ax.patch.set_alpha(0.0)
        return fig
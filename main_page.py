import streamlit as st
import requests
from streamlit_lottie import st_lottie
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from data_utils import get_df_from_data
import datetime as dt
from dateutil.relativedelta import relativedelta


plt.style.use('seaborn')

st.set_page_config(layout="centered")


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


lottie_chat = load_lottieurl('https://assets10.lottiefiles.com/packages/lf20_zezv30bd.json')
lottie_msg = load_lottieurl('https://assets1.lottiefiles.com/packages/lf20_eBcQGa.json')
# st_lottie(lottie_msg, speed=1, height=300, key="msg_lottie")
# st_lottie(lottie_chat, speed=1, height=600, key="chat_lottie")
github_link = 'https://github.com/akiragondo/whatsapp_analyser'
c1, c2 = st.columns((2, 1))
c1.title("""Whatsapp Chat Analyser""")
c1.subheader("""Discover trends, analyse your chat history and judge your friends!""")
c1.markdown(f"Dont worry, we wont peek, we're not about that, in fact, you can check the code in here: [link]({github_link})")
uploaded_file = c1.file_uploader(label="""Upload your Whatsapp chat, don't worry, we won't peek""")

with c2:
    st_lottie(lottie_chat, speed=1, height=400, key="msg_lottie")
if uploaded_file is not None:


    # with open(uploaded_file, 'r') as input_file:
    #     content = input_file.read()
    content = str(uploaded_file.read())
    df = get_df_from_data(content)


    st.subheader('Date Range')

    format = 'MMM DD, YYYY'  # format output
    start_date = df.index.to_pydatetime()[0]
    end_date = df.index.to_pydatetime()[-1]
    max_days = end_date - start_date
    slider = st.slider('Select date', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)

    df = df[slider[0]:slider[1]]

    wide_figsize = (14, 7)
    narrow_figsize = (7, 7)

    y_columns = [subject for subject in df['Subject'].unique()]

    cmap = plt.get_cmap('viridis')
    colors = [cmap(cmap.N*i/len(y_columns)) for i, _ in enumerate(y_columns)]


    date_df = df.resample('W').sum()
    fig, ax = plt.subplots(figsize=wide_figsize)
    date_df[y_columns].plot(kind='bar', alpha=0.6, cmap=cmap, ax=ax, stacked=True)
    ax.patch.set_alpha(0.0)
    ax.legend(y_columns)

    max_message_count = date_df[y_columns].sum(axis = 1).max()
    max_message_count_date = date_df.index[date_df[y_columns].sum(axis = 1).argmax()]

    st.subheader("Number of messages by date")
    st.markdown(f"This is how many messages each one of you have exchanged per **week** between the dates of **{slider[0].strftime('%m/%y')}** and **{slider[1].strftime('%m/%y')}**, the most messages you guys have exchanged in a week was **{max_message_count}** on **{max_message_count_date.strftime('%d/%m/%y')}**")
    st.pyplot(fig)

    other_y_columns = [f"{subject}_mlength" for subject in df['Subject'].unique()]
    date_avg_df = df.resample('M').mean()
    fig, ax = plt.subplots(figsize=wide_figsize)
    date_df[other_y_columns].plot(kind='area', alpha=0.6, cmap =cmap, ax=ax)
    ax.legend(y_columns)
    ax.patch.set_alpha(0.0)


    st.subheader("Average number of words in a message")
    st.markdown(f"This basically shows how much effort each person puts in each message, the more words per message, the more it feels like the person is putting in real effort")
    st.pyplot(fig)

    fig1, ax = plt.subplots(figsize=narrow_figsize)
    c_11,c_12 = st.columns((1,1))
    subject_df = df.groupby('Subject').count()['Message'].sort_values(ascending = False)
    subject_df.plot(kind = 'pie', cmap =cmap, ax = ax,autopct = '%1.1f%%', explode = [0.015]*len(subject_df.index.unique()))

    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    most_messages_winner = subject_df.index[subject_df.argmax()]
    ax.patch.set_alpha(0.0)
    c_11.subheader("Messages sent by user")
    c_11.markdown(f"How many messages has each one sent in your convo? apparently **{most_messages_winner}** did")
    c_11.pyplot(fig1)


    avg_msg_length = df.groupby('Subject').mean()['Message Length']
    fig, ax = plt.subplots(figsize=narrow_figsize)
    avg_msg_length.plot(kind='bar', cmap = cmap,ax=ax)
    ax.patch.set_alpha(0.0)

    most_wpm_winner = avg_msg_length.index[avg_msg_length.argmax()]
    c_12.subheader("Average message length by user")
    c_12.markdown(f"This one shows the average message length, apparently **{most_wpm_winner}** puts the most effort for each message")
    c_12.pyplot(fig)



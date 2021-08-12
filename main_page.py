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


c1, c2 = st.columns((2, 1))
c1.title("""Whatsapp Chat Analyser""")
c1.subheader("""Discover trends, analyse your chat history and judge your friends!""")
uploaded_file = c1.file_uploader(label="""Upload your Whatsapp chat, don't worry, we won't peek, really we won't, you can check the source code at {link}""")


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
    st.pyplot(fig)

    other_y_columns = [f"{subject}_mlength" for subject in df['Subject'].unique()]
    date_avg_df = df.resample('M').mean()
    fig, ax = plt.subplots(figsize=wide_figsize)
    date_df[other_y_columns].plot(kind='area', alpha=0.6, cmap =cmap, ax=ax)
    ax.legend(y_columns)
    ax.patch.set_alpha(0.0)
    st.pyplot(fig)

    fig1, ax = plt.subplots(figsize=narrow_figsize)
    c_11,c_12 = st.columns((1,1))
    subject_df = df.groupby('Subject').count()['Message']
    subject_df.plot(kind = 'pie', cmap =cmap, ax = ax,autopct = '%1.1f%%', explode = [0.015]*len(subject_df.index.unique()))

    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    ax.patch.set_alpha(0.0)
    ax.legend(y_columns)
    c_11.pyplot(fig1)


    avg_msg_length = df.groupby('Subject').mean()['Message Length']
    fig, ax = plt.subplots(figsize=narrow_figsize)
    avg_msg_length.plot(kind='bar', color=colors,ax=ax)
    ax.patch.set_alpha(0.0)
    c_12.pyplot(fig)



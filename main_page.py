import streamlit as st
import requests
from streamlit_lottie import st_lottie
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import numpy as np
from data_utils import get_df_from_data
import base64
import json
import uuid
import re
plt.style.use('seaborn')

st.set_page_config(layout="centered")


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def download_button(object_to_download, download_filename, button_text):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """

    if isinstance(object_to_download, bytes):
        pass

    # Try JSON encode for everything else
    else:
        object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(towrite.read()).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: .25rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">{button_text}</a><br></br>'

    return dl_link

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

file_path = 'sample_whatsapp_export.txt'
with open(file_path, 'r') as f:
    dl_button = download_button(f.read(), 'sample_file.txt', 'Try it out with my sample file!')
    c1.markdown(dl_button, unsafe_allow_html=True)

with c2:
    st_lottie(lottie_chat, speed=1, height=400, key="msg_lottie")
if uploaded_file is not None:


    wide_figsize = (12, 5)
    narrow_figsize = (6, 5)
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
    all_subjects = [subject for subject in df['Subject'].unique()]

    y_columns = st.multiselect(
        "Select and deselect the people you would like to include in the analysis. You can clear the current selection by clicking the corresponding x-button on the right",
        all_subjects, default=all_subjects)
    print(df.head(50))
    subject_filter = [subject in y_columns for subject in df['Subject'].values]
    df = df[subject_filter]

    cmap = plt.get_cmap('viridis')
    colors = pl.get_cmap('viridis')(np.linspace(0,1, len(y_columns)))

    if len(y_columns) > 0:
        #Makes first graph
        date_df = df.resample('W').sum()
        fig, ax = plt.subplots(figsize=wide_figsize)
        date_df[y_columns].plot(kind='area', alpha=0.6, cmap=cmap, ax=ax, stacked=True)
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


        #Makes second graph

        filtered_sender_changes  = df[df['Is reply']]
        fig, ax = plt.subplots(figsize=wide_figsize)
        for index, subject in enumerate(y_columns):
            subject_df = df[df['Subject'] == subject].resample('W').mean().fillna(0)['Reply time']
            subject_df.plot(kind='line', alpha=0.95, cmap =cmap, ax=ax, label = subject, color = colors[index], marker='o', markersize = 5)
        ax.patch.set_alpha(0.0)
        st.subheader("Average reply time of messages by date")
        st.markdown(f"This how long it took, on average for each person to reply to the previous message within a conversation")
        ax.legend(loc = 'upper right')
        st.pyplot(fig)

        #Makes graph row
        fig1, ax = plt.subplots(figsize=narrow_figsize)
        c_11,c_12 = st.columns((1,1))
        subject_df = df[df['Conv change']].groupby('Subject').count()['Reply time']
        subject_df.plot(kind = 'pie', cmap =cmap, ax = ax,autopct = '%1.1f%%', explode = [0.015]*len(subject_df.index.unique()))

        centre_circle = plt.Circle((0, 0), 0.80, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        most_messages_winner = subject_df.index[subject_df.argmax()]
        ax.patch.set_alpha(0.0)
        c_11.subheader("Who's starts the conversations?")
        c_11.markdown(f"This clearly shows that **{most_messages_winner}** started all the convos")
        ax.set_ylabel('')
        c_11.pyplot(fig1)


        buffer_perc = 0.05
        avg_msg_length = df.groupby('Subject').mean()['Reply time']
        fig, ax = plt.subplots(figsize=narrow_figsize)
        avg_msg_length.plot(kind='bar', color = colors,ax=ax)
        ax.patch.set_alpha(0.0)

        most_wpm_winner = avg_msg_length.index[avg_msg_length.argmax()]
        max = avg_msg_length.max()*(1)
        min = avg_msg_length.min()*(1-buffer_perc)
        ax.set_ylim([min,max])
        c_12.subheader("Average Reply time by user")
        c_12.markdown(f"Who takes the longest to reply? **{most_wpm_winner}** won this one")
        c_12.pyplot(fig)




        #Makes graph row
        fig1, ax = plt.subplots(figsize=narrow_figsize)
        c_11,c_12 = st.columns((1,1))
        subject_df = df.groupby('Subject').count()['Message'].sort_values(ascending = False)
        subject_df.plot(kind = 'pie', cmap =cmap, ax = ax,autopct = '%1.1f%%', explode = [0.015]*len(subject_df.index.unique()))

        centre_circle = plt.Circle((0, 0), 0.80, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        most_messages_winner = subject_df.index[subject_df.argmax()]
        ax.patch.set_alpha(0.0)
        c_11.subheader("Messages sent by user")
        c_11.markdown(f"How many messages has each one sent in your convo? apparently **{most_messages_winner}** did")
        ax.set_ylabel('')
        c_11.pyplot(fig1)

        buffer_perc = 0.01
        avg_msg_length = df.groupby('Subject').mean()['Message Length']
        fig, ax = plt.subplots(figsize=narrow_figsize)
        avg_msg_length.plot(kind='bar', color = colors,ax=ax)
        ax.patch.set_alpha(0.0)

        most_wpm_winner = avg_msg_length.index[avg_msg_length.argmax()]
        max = avg_msg_length.max()*(1)
        min = avg_msg_length.min()*(1-buffer_perc)
        ax.set_ylim([min,max])
        c_12.subheader("Average message length by user")
        c_12.markdown(f"This one shows the average message length, apparently **{most_wpm_winner}** puts the most effort for each message")
        c_12.pyplot(fig)



        conversations_df = df.groupby('Conv code').agg(count=('Conv code', 'size'), mean_date=('Date', 'mean')).reset_index()
        conversations_df.index = conversations_df['mean_date']
        conversations_df = conversations_df.resample('W').sum().fillna(0)
        print(conversations_df.head(50))
        fig, ax = plt.subplots(figsize=wide_figsize)
        ax.plot(conversations_df.index, conversations_df['count'], color = colors[0], alpha= 0.7)
        ax.fill_between(x = conversations_df.index,y1 = conversations_df['count'], color = colors[0], alpha = 0.5)
        ax.patch.set_alpha(0.0)
        st.subheader("Average conversation size")
        st.markdown(f"This is how many messages (on average) your conversations had, the more of them there are, the more messages you guys exchanged everytime one of you started the convo!")
        st.pyplot(fig)





        conversation_dist = df.groupby('Conv code').count()['Message']
        fig, ax = plt.subplots(figsize=wide_figsize)
        tax = ax.twinx()
        conversation_dist.plot(kind='hist', cmap = cmap,ax=ax, alpha = 0.5, bins=[2**i for i in range(0,10)])
        conversation_dist.plot(kind='kde', cmap = cmap,ax=tax, alpha = 0.7)
        y_min, y_max = tax.get_ylim()
        tax.set_ylim([0, y_max])
        ax.patch.set_alpha(0.0)
        ax.set_xscale('log')
        x_min, x_max = tax.get_xlim()
        tax.set_xlim([1, x_max])

        st.subheader("Number of messages per conversation")
        st.markdown(f"What does the distribution of the length of your conversations look like? This is a log scale so pay close attention to the x axis")
        st.pyplot(fig)


thanks_line = """Special thanks to Charly Wargnier for the suggestions and jrieke for making the custom CSS download button!"""
st.markdown("""    <style>
footer {
	visibility: hidden;
	}
footer:after {
	content:'"""+ thanks_line+ """'; 
	visibility: visible;
	display: block;
	position: relative;
	#background-color: red;
	padding: 5px;
	top: 2px;
}</style>""", unsafe_allow_html=True)
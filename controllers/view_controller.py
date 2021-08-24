import streamlit as st
from streamlit_lottie import st_lottie
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import numpy as np

from components.graph_components import GraphComponents
from components.ui_components import download_button
from components.ui_components import load_lottieurl
from data_utils import get_df_from_data

class ViewController:
    def __init__(self):

        st.set_page_config(
            page_title='Whatsapp Chat Analyser',
            page_icon=':test_tube:',
            layout='centered',
            initial_sidebar_state='collapsed',

        )

        self.lottie_chat = load_lottieurl('animations_data/36311-phone-chat.json')
        self.lottie_message = load_lottieurl('animations_data/message_lottie.json')
        self.github_link = 'https://github.com/akiragondo/whatsapp_analyser'
        self.file_path = 'sample_whatsapp_export.txt'

    def build_conversation_explanation(self):
        st.title('How does the chat analyser work?')

    def build_graph_ui(self):
        c1, c2 = st.columns((2, 1))
        c1.title("""Whatsapp Chat Analyser""")
        c1.subheader("""Discover trends, analyse your chat history and judge your friends!""")
        c1.markdown(f"Dont worry, we wont peek, we're not about that, in fact, you can check the code in here: [link]({self.github_link})")
        uploaded_file = c1.file_uploader(label="""Upload your Whatsapp chat, don't worry, we won't peek""")

        with open(self.file_path, 'r') as f:
            dl_button = download_button(f.read(), 'sample_file.txt', 'Try it out with my sample file!')
            c1.markdown(dl_button, unsafe_allow_html=True)

        with c2:
            st_lottie(self.lottie_chat, speed=1, height=400, key="msg_lottie")
        if uploaded_file is not None:
            df = get_df_from_data(uploaded_file)

            st.subheader('Date Range')

            format = 'MMM, YYYY'  # format output
            start_date = df.index.to_pydatetime()[0]
            end_date = df.index.to_pydatetime()[-1]

            slider = st.slider('Select date', min_value=start_date, value=(start_date, end_date), max_value=end_date, format=format)

            df = df[slider[0]:slider[1]]
            all_subjects = [subject for subject in df['Subject'].unique()]

            y_columns = st.multiselect(
                "Select and deselect the people you would like to include in the analysis. You can clear the current selection by clicking the corresponding x-button on the right",
                all_subjects, default=all_subjects)
            subject_filter = [subject in y_columns for subject in df['Subject'].values]
            df = df[subject_filter]


            cmap = plt.get_cmap('viridis')
            colors = pl.get_cmap('viridis')(np.linspace(0,1, len(y_columns)))
            wide_figsize = (12, 5)
            narrow_figsize = (6, 5)
            params = {
                'subjects' : y_columns,
                'wide_figsize' : wide_figsize,
                'narrow_figsize': narrow_figsize,
                'cmap' : cmap,
                'colors' : colors,
                'area_alpha' : 0.6,
            }
            graphs = GraphComponents(params)
            if len(y_columns) > 0:
                fig, max_message_count, max_message_count_date = graphs.create_messages_per_week_graph(df)
                st.subheader("When did you talk the most?")
                st.markdown(f"This is how many messages each one of you have exchanged per **week** between the dates of **{slider[0].strftime('%m/%y')}** and **{slider[1].strftime('%m/%y')}**, the most messages you guys have exchanged in a week was **{max_message_count}** on **{max_message_count_date.strftime('%d/%m/%y')}**")
                st.pyplot(fig)

                fig = graphs.create_average_wpm_graph(df)
                st.subheader("How many words do your messages have?")
                st.markdown(f"This basically shows how much effort each person puts in each message, the more words per message, the more it feels like the person is putting in real effort")
                st.pyplot(fig)


                #Makes second graph
                fig = graphs.average_reply_time_graph(df)
                st.subheader("How long does it take for you to reply?")
                st.markdown(f"This how long it took, on average for each person to reply to the previous message within a conversation")
                st.pyplot(fig)

                #Makes second graph
                fig = graphs.average_conversation_hour_graph(df)
                st.subheader("When do you talk the most?")
                st.markdown(f"This shows when during the day you guys talk the most! Change the slider dates to see how that has changed with time")
                st.pyplot(fig)

                #Makes graph row
                c_11,c_12 = st.columns((1,1))
                fig1, most_messages_winner = graphs.conversation_starter_graph(df)
                c_11.subheader("Who's starts the conversations?")
                c_11.markdown(f"This clearly shows that **{most_messages_winner}** started all the convos")
                c_11.pyplot(fig1)


                fig, most_wpm_winner = graphs.reply_time_aggregated_graph(df)
                c_12.subheader("Who takes the longest to reply?")
                c_12.markdown(f"Who takes the longest to reply? **{most_wpm_winner}** won this one")
                c_12.pyplot(fig)


                #Makes graph row
                c_11,c_12 = st.columns((1,1))
                fig1, most_messages_winner = graphs.message_count_aggregated_graph(df)
                c_11.subheader("Who talks the most?")
                c_11.markdown(f"How many messages has each one sent in your convo? apparently **{most_messages_winner}** did")
                c_11.pyplot(fig1)

                fig, most_wpm_winner = graphs.message_size_aggregated_graph(df)
                c_12.subheader("Who sends the bigger messages?")
                c_12.markdown(f"This one shows the average message length, apparently **{most_wpm_winner}** puts the most effort for each message")
                c_12.pyplot(fig)


                fig = graphs.conversation_size_aggregated_graph(df)
                st.subheader("How long are your conversations?")
                st.markdown(f"This is how many messages (on average) your conversations had, the more of them there are, the more messages you guys exchanged everytime one of you started the convo!")
                st.pyplot(fig)

        thanks_line = """Special thanks to Charly Wargnier and Timon Schmelzer for the suggestions and jrieke for making the custom CSS download button!"""
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

    def build_about_me_ui(self):
        st.title("About the Creator")

    def build_sidebar(self):

        with st.sidebar:
            st_lottie(self.lottie_message, quality='High', height=100, key='message_lottie')
        st.sidebar.title("WhatsApp Chat Analyser")
        pages = [
            'WhatsApp Chat Analyser',
            'How does the Chat Analyser Work?',
            'About the Creator'
        ]
        selected_page = st.sidebar.radio(
            label = 'Page',
            options= pages
        )
        return selected_page

    def build_ui(self):
        selected_page = self.build_sidebar()
        if selected_page == 'WhatsApp Chat Analyser':
            self.build_graph_ui()
        elif selected_page == 'How does the Chat Analyser Work?':
            self.build_conversation_explanation()
        elif selected_page == 'About the Creator':
            self.build_about_me_ui()
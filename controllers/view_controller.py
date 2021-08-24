import streamlit as st
from streamlit_lottie import st_lottie
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import numpy as np
from components.graph_components import GraphComponents
from components.ui_components import download_button
from components.ui_components import load_lottieurl
from data_utils import get_df_from_data
import base64

class ViewController:
    def __init__(self):

        st.set_page_config(
            page_title='Whatsapp Chat Analyser',
            page_icon=':test_tube:',
            layout='centered',
            initial_sidebar_state='auto',

        )

        self.lottie_chat = load_lottieurl('animations_data/phone_chat.json')
        self.lottie_message = load_lottieurl('animations_data/message_lottie.json')
        self.lottie_data = load_lottieurl('animations_data/data_charts.json')
        self.github_link = 'https://github.com/akiragondo/whatsapp_analyser'
        self.file_path = 'sample_whatsapp_export.txt'


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
        c1, c2 = st.columns([1,1])
        c1.markdown("Hey! My name is Gustavo Akira Gondo, a Computer Engineer from Brazil! This page is still under "
                    "construction since I want to finish the rest of the app before I focus on this bit, but if you "
                    "would like to ask me anything of if you have any projects you think I could be a good addition "
                    "to, please, send me a message at gustavogondo@alunos.utfpr.edu.br")
        c2.image('images/me.jpg')

    def build_conversation_explanation(self):
        st.title('How does the chat analyser work?')
        c1, c2 = st.columns([1,1])
        c1.header('Data Analysis')
        c1.markdown("""The core of this app is made up of very simple data analysis, such as the aggregation of the 
        time of day the messages were sent, or by counting the number of messages were sent each month, however, 
        calculations such as reply times and number of messages in a conversation aren't so trivial, in which we'll 
        dive deeper right now!""")
        with c2:
            st_lottie(self.lottie_data, height=300)
        st.header('Conversations')
        st.markdown("""In order to analyse conversations, we need to first find a way to define conversations based 
        on a sequence of individual messages. To do that, let's make our definition of a conversation:""")
        st.info("""Conversations:        
        The event of the exchange of messages between two people during a certain period of time""")
        st.markdown("""To implement that in our messages, I have implemented a code that, if it detects a significant 
        amount of time between two messages, say around 1 hour, it'll define the end of a conversation and the 
        beginning of a new one! Here's the code for it:""")
        image = open('images/ConvDiagram.svg', 'r').read()
        self.render_svg(image)
        st.code("""def cluster_into_conversations(
        df : pd.DataFrame, 
        inter_conversation_threshold_time: int = 60
        ):
    threshold_time_mins = np.timedelta64(inter_conversation_threshold_time, 'm')

    # This calculates the time between the current message and the previous one
    conv_delta = df.index.values - np.roll(df.index.values, 1)
    conv_delta[0] = 0

    # This detects where the time between messages is higher than the threshold
    conv_changes = conv_delta > threshold_time_mins
    conv_changes_indices = np.where(conv_changes)[0]
    conv_codes = []

    # This encodes each message with its own conversation code
    last_conv_change = 0
    for i, conv_change in enumerate(conv_changes_indices):
        conv_codes.extend([i]*(conv_change - last_conv_change))
        last_conv_change = conv_change

    # This serves to ensure that the conversation codes 
    # and the number of messages are aligned
    conv_codes = pad_list_to_value(conv_codes, len(df), conv_codes[-1])
    conv_changes = pad_list_to_value(conv_changes, len(df), False)

    return conv_codes, conv_changes
        """)
        st.header('Replies')
        st.markdown("""This is basically the same issue as the one we had in the conversations, we first need to 
        define it:""")
        st.info("""Reply:
        The response of one person to the messages sent by the previous one within a conversation""")
        st.markdown("""This is faily easy to implement, I will say that a reply happens when the subject changes 
        within a conversation, here's the code for it!:""")
        image = open('images/ReplyDiagram.svg', 'r').read()
        self.render_svg(image)
        st.code("""def find_replies(df : pd.DataFrame):
    # These are sanity checks in order to see if I made any ordering mistakes
    assert('Conv code' in df.columns)
    assert('Conv change' in df.columns)
    assert('Subject' in df.columns)
    # Ordinal encoders will encode each subject with its own number
    message_senders = OrdinalEncoder().fit_transform(df['Subject'].values.reshape(-1,1))
    # This compares the current subject with the previous subject 
    # In a way that computers can optimize
    sender_changed = (np.roll(message_senders, 1) - message_senders).reshape(1, -1)[0] != 0
    sender_changed[0] = False
    # This checks if the reply isn't within a different conversation
    is_reply = sender_changed & ~df['Conv change']
    return is_reply, sender_changed""")
        st.markdown("""Notice how that implies that if a reply is the start of a new conversation, it's not a reply, 
        it's the start of a new conversation. This helps us segregate the replies to only those that happen within a 
        conversation, say, when you two are really **Talking** to each other, which I think is more indicative of the 
        level of interaction you two are having""")

    def render_svg(self, svg):
        """Renders the given svg string."""
        b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
        html = f"""<img style = "width: 100%" src="data:image/svg+xml;base64,{b64}"/>"""
        st.write(html, unsafe_allow_html=True)

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
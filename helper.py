from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extractor = URLExtract()

# ------------------ Statistics ------------------ #
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    words = sum(len(msg.split()) for msg in df['message'])
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]
    links = sum(len(extractor.find_urls(msg)) for msg in df['message'])

    return num_messages, words, num_media_messages, links


def most_busy_users(df):
    top_users = df['user'].value_counts().head()
    percent_df = (
        df['user']
        .value_counts(normalize=True)
        .mul(100)
        .round(2)
        .reset_index()
    )
    percent_df.columns = ['name', 'percent']
    return top_users, percent_df

# ------------------ Text & WordCloud ------------------ #
def create_word_cloud(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

    wc = WordCloud(
        width=600,
        height=400,
        min_font_size=10,
        background_color='white'
    )
    return wc.generate(temp['message'].str.cat(sep=" "))


def most_common_words(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[(df['user'] != 'group_notification') & (df['message'] != '<Media omitted>\n')]

    words = []
    for message in temp['message']:
        words.extend(message.split())

    return pd.DataFrame(Counter(words).most_common(20), columns=['word', 'count'])

# ------------------ Emoji ------------------ #
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        if isinstance(message, str):
            emojis.extend([c for c in message if emoji.is_emoji(c)])

    return pd.DataFrame(Counter(emojis).most_common(), columns=['emoji', 'count'])

# ------------------ Timelines ------------------ #
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.groupby('only_date').count()['message'].reset_index()

# ------------------ Activity Maps ------------------ #
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def monthly_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df.pivot_table(
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)

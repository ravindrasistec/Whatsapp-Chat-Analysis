import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# ------------------ Page Config ------------------ #
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    layout="wide",
    page_icon="💬"
)

st.sidebar.title("📂 WhatsApp Chat Analyzer")

# ------------------ File Upload ------------------ #
uploaded_file = st.sidebar.file_uploader("Choose a WhatsApp chat text file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # ------------------ Sidebar Filters ------------------ #
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Analyze chat for", user_list)

    if st.sidebar.button("Show Analysis"):
        # ------------------ Top Stats ------------------ #
        num_messages, words, num_media_messages, links = helper.fetch_stats(selected_user, df)
        st.markdown("## 📊 Top Statistics")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Shared", num_media_messages)
        col4.metric("Links Shared", links)

        st.markdown("---")

        # ------------------ Monthly Timeline ------------------ #
        st.markdown("## 📅 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig = px.line(timeline, x="time", y="message", markers=True, title="Messages per Month")
        st.plotly_chart(fig, use_container_width=True)

        # ------------------ Daily Timeline ------------------ #
        st.markdown("## 📆 Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig = px.line(daily_timeline, x="only_date", y="message", markers=True, title="Messages per Day")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ------------------ Activity Map ------------------ #
        st.markdown("## 📌 Activity Maps")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color="orange")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        with col2:
            st.subheader("Most Busy Month")
            busy_month = helper.monthly_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color="green")
            plt.xticks(rotation="vertical")
            st.pyplot(fig)

        # Heatmap
        st.subheader("⏰ Weekly Activity Heatmap")
        activity_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(activity_heatmap, cmap="YlGnBu", linewidths=.5, annot=True, fmt=".0f")
        st.pyplot(fig)

        st.markdown("---")

        # ------------------ Most Busy Users ------------------ #
        if selected_user == "Overall":
            st.markdown("## 🧑‍🤝‍🧑 Most Busy Users")
            x, new_df = helper.most_busy_users(df)
            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(x, x=x.index, y=x.values, title="Top 5 Users", color=x.index)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.dataframe(new_df)

            st.markdown("---")

        # ------------------ Word Cloud ------------------ #
        st.markdown("## ☁️ Word Cloud")
        wc = helper.create_word_cloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(wc)
        ax.axis("off")
        st.pyplot(fig)

        # ------------------ Most Common Words ------------------ #
        st.markdown("## 🔤 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig = px.bar(
            most_common_df,
            x="word",
            y="count",
            text="count",
            title="Top 20 Common Words",
            color="word"
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        # ------------------ Emoji Analysis ------------------ #
        st.markdown("## 😎 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(emoji_df.head(10))

        with col2:
            fig = px.pie(
                emoji_df.head(10),
                values="count",
                names="emoji",
                title="Top Emojis",
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)

        if not emoji_df.empty:
            top_emoji = emoji_df.iloc[0]
            st.info(f"✨ Most used emoji is **{top_emoji['emoji']}** with {top_emoji['count']} uses.")

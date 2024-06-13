import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from wordcloud_component import display_wordcloud
import os
import extra_streamlit_components as stx

# Set the page configuration
st.set_page_config(layout="wide")

# Cookie handling beyond refresh
@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# Load existing data or create a new DataFrame
def load_data(file_path):
    try:
        data = pd.read_csv(file_path, parse_dates=['date'], index_col=False)
    except FileNotFoundError:
        data = pd.DataFrame(columns=['date', 'rating', 'comment'])
    return data

# Save data to a CSV file
def save_data(data, file_path):
    data.to_csv(file_path, index=False)

# Add or update an entry
def add_or_update_data(data, date, rating, comment):
    date = pd.to_datetime(date)
    if date in data['date'].values:
        data.loc[data['date'] == date, 'rating'] = rating
        data.loc[data['date'] == date, 'comment'] = comment
    else:
        new_entry = pd.DataFrame({'date': [date], 'rating': [rating], 'comment': [comment]})
        data = pd.concat([data, new_entry], ignore_index=True)
    return data

# Delete an entry
def delete_data(data, date):
    date = pd.to_datetime(date)
    data = data[data['date'] != date]
    return data

def display_login():
    password = st.text_input("Enter password", type="password")
    if st.button("Login"):
        if password == os.environ.get("DAILY_RATING_PASSWORD"):
            st.session_state.logged_in = True
            cookie_manager.set('logged_in', True)
            st.rerun()
        else:
            st.error("Incorrect password!")

def display_content():
    # CONTENT START
    user = st.sidebar.selectbox("Tell me who you are!", ["Martin", "Moritz", "Example"])
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        cookie_manager.delete('logged_in')
        st.rerun()

    st.markdown(f"### Welcome, {user}!")
    st.warning("Any information added here is publicly available. So don't add anything you don't want anyone to see...")

    col1, col2 = st.columns([1, 2])
    with col1:

        # File path for storing data
        file_path = f'daily_ratings_{user}.csv'

        # Load data
        st.session_state.data = load_data(file_path)

        # Input section for adding or editing a rating
        st.markdown("##### Add or Edit a Rating")
        date = st.date_input("Date", datetime.date.today()).strftime('%Y-%m-%d')

        # Check if there's already a rating for the selected date
        existing_entry = st.session_state.data[st.session_state.data['date'] == pd.to_datetime(date)]
        if not existing_entry.empty:
            rating = st.slider("Rating", 1, 10, int(existing_entry['rating'].values[0]))
            comment = st.text_area("Comment", existing_entry['comment'].values[0])
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Changes"):
                    st.session_state.data = add_or_update_data(st.session_state.data, date, rating, comment)
                    save_data(st.session_state.data, file_path)
                    st.success(f"Rating for {date} has been updated!")
            with col2:
                if st.button("Delete Entry"):
                    st.session_state.data = delete_data(st.session_state.data, date)
                    save_data(st.session_state.data, file_path)
                    st.success(f"Rating for {date} has been deleted!")
        else:
            rating = st.slider("Rating", 1, 10, 5)
            comment = st.text_area("Comment")
            if st.button("Add Rating"):
                st.session_state.data = add_or_update_data(st.session_state.data, date, rating, comment)
                save_data(st.session_state.data, file_path)
                st.success(f"Rating for {date} has been added!")
    with col2:
        st.markdown("##### Ratings Over Time")
        if st.session_state.data.empty: st.write("No ratings available to display.")
        else:
            # View Ratings Chart
            view_option = st.selectbox("View", ["Daily", "Weekly"])

            if view_option == "Daily":
                fig, ax = plt.subplots()
                ax.plot(st.session_state.data['date'], st.session_state.data['rating'], marker='o')
                ax.set_xlabel("Date")
                ax.set_ylabel("Rating")
                ax.set_title("Daily Ratings")
                st.pyplot(fig)
            else:
                st.session_state.data['week'] = st.session_state.data['date'].dt.to_period('W').apply(lambda r: r.start_time)
                weekly_data = st.session_state.data.groupby('week')['rating'].mean().reset_index()
                fig, ax = plt.subplots()
                ax.plot(weekly_data['week'], weekly_data['rating'], marker='o')
                ax.set_xlabel("Week")
                ax.set_ylabel("Average Rating")
                ax.set_title("Weekly Average Ratings")
                st.pyplot(fig)
                
            # Display Data as a Table
            with st.expander("All ratings", expanded=False):
                st.dataframe(st.session_state.data)
        
        # Word Cloud
        st.markdown("##### Word Cloud of Comments")
        if st.session_state.data.empty:
            st.write("No comments available to generate a word cloud.")
        else: display_wordcloud()

if __name__ == "__main__":
    if ("logged_in" not in st.session_state or not st.session_state.logged_in) and cookie_manager.get('logged_in') != True:
        st.title("Daily Ratings Dashboard")
        display_login()
    else:
        display_content()

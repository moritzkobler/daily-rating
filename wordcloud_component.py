import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud, STOPWORDS


# Generate bigrams
def generate_ngrams(text, n=2):
    words = word_tokenize(text)
    words = [word for word in words if word.isalnum()]
    ngrams = zip(*[words[i:] for i in range(n)])
    return [' '.join(ngram) for ngram in ngrams]

def display_wordcloud():
    nltk.data.path.append('nltk_data')  # Replace 'path_to_nltk_data' with the actual path to the directory

    # Word Cloud
    time_period = st.selectbox("Time Period", ["All Time", "Last 7 Days", "Last 30 Days"])

    if time_period == "Last 7 Days":
        start_date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=7))
        filtered_data = st.session_state.data[st.session_state.data['date'] >= start_date]
    elif time_period == "Last 30 Days":
        start_date = pd.to_datetime(datetime.date.today() - datetime.timedelta(days=30))
        filtered_data = st.session_state.data[st.session_state.data['date'] >= start_date]
    else:
        filtered_data = st.session_state.data

    # Combine comments into a single text
    text = " ".join(filtered_data['comment'].dropna()).lower()

    # Define stopwords
    custom_stopwords = set(STOPWORDS).union(set(stopwords.words('english')))
    custom_stopwords.update(['day', 'much', 'gone', 'got'])

    # Generate bigrams and update the text
    bigrams = generate_ngrams(text, n=2)
    bigrams_text = ' '.join(bigrams)

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white', stopwords=custom_stopwords).generate(bigrams_text)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
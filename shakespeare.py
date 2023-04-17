import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from wordcloud import WordCloud, STOPWORDS
import glob, nltk, os, re
from nltk.corpus import stopwords 
import nltk
nltk.download('punkt')
import string

st.markdown('''
# Analyzing Shakespeare Texts
''')

# Create a dictionary (not a list)
books = {" ":" ","A Mid Summer Night's Dream":"data/summer.txt","The Merchant of Venice":"data/merchant.txt","Romeo and Juliet":"data/romeo.txt"}

# Sidebar
st.sidebar.header('Word Cloud Settings')
max_word = st.sidebar.slider("Max Words",min_value=10, max_value=200, value=100, step=10)
size_largestword = st.sidebar.slider("Size of Largest Word",min_value=50, max_value=350, value=60, step=10)
image_width = st.sidebar.slider("Image Width",min_value=100, max_value=800, value=400, step=10)
random_state = st.sidebar.slider("Random State",min_value=20, max_value=100, value=20, step=1)
remove_stop_words = st.sidebar.checkbox("Remove Stop Words?",value=True)
st.sidebar.header('Word Count Settings')
min_countwords = st.sidebar.slider("Minimum count of words",min_value=5, max_value=100, value=40, step=1)

## Select text files
image = st.selectbox("Choose a text file", books.keys())

## Get the value
image = books.get(image)

if image != " ":
    stop_words = []
    raw_text = open(image,"r").read().lower()
    nltk_stop_words = stopwords.words('english')

    if remove_stop_words:
        stop_words = set(nltk_stop_words)
        stop_words.update(['us', 'one', 'though','will', 'said', 'now', 'well', 'man', 'may',
        'little', 'say', 'must', 'way', 'long', 'yet', 'mean',
        'put', 'seem', 'asked', 'made', 'half', 'much',
        'certainly', 'might', 'came','thou'])
        # These are all lowercase

    tokens = nltk.word_tokenize(raw_text)


    tab1, tab2, tab3 = st.tabs(['Word Cloud', 'Bar Chart', 'View Text'])

    with tab1:
        # Tokenization without punctuation
        tokens = [word for word in nltk.word_tokenize(raw_text) if word not in string.punctuation]

        # Tokenization without punctuation and tokens starting with an apostrophe
        tokens = [word for word in nltk.word_tokenize(raw_text) if word not in string.punctuation and not word.startswith("'")]

        # Calculate word frequencies
        word_frequencies = nltk.FreqDist(tokens)

        # Remove stopwords from the word frequencies
        if remove_stop_words:
            word_frequencies = {word: count for word, count in word_frequencies.items() if word not in stop_words}

        # Filter based on minimum count of words
        filtered_word_frequencies = {word: count for word, count in word_frequencies.items() if count >= min_countwords}

        # Generate the word cloud image
        image_height = image_width // 2
        wordcloud = WordCloud(width=image_width, height=image_height,  # Use the image_width variable from the sidebar
                            background_color='white',
                            stopwords=stop_words,
                            max_words=max_word,
                            max_font_size=size_largestword,
                            random_state=random_state
                            ).generate_from_frequencies(filtered_word_frequencies)

        # Display the generated image
        st.image(wordcloud.to_array(), use_column_width=False)  # Use the image_width variable from the sidebar

    with tab2:
        st.subheader("Bar Chart")
        # Tokenization without punctuation and tokens starting with an apostrophe
        tokens = [word for word in nltk.word_tokenize(raw_text) if word not in string.punctuation and not word.startswith("'")]

        # Remove stopwords from the tokens
        if remove_stop_words:
            stop_words = set(nltk_stop_words)
            tokens = [word for word in tokens if word.lower() not in stop_words]

        # Calculate word frequencies
        word_frequencies = nltk.FreqDist(tokens)

        # Sort the word frequencies by count in descending order
        sorted_word_frequencies = {k: v for k, v in sorted(word_frequencies.items(), key=lambda item: item[1], reverse=True)}

        # Filter the top 24 most frequent words
        filtered_word_frequencies = {word: count for i, (word, count) in enumerate(sorted_word_frequencies.items()) if i < 24}

        # Create a dataframe from the filtered word frequencies
        word_freq_df = pd.DataFrame(list(filtered_word_frequencies.items()), columns=['word', 'count'])

        # Create a bar chart using Altair
        bar_chart = alt.Chart(word_freq_df).mark_bar().encode(
        y=alt.Y('word:N', sort='-x', title='Word'),
        x=alt.X('count:Q', title='Count'),
        text=alt.Text('count:Q')
        ).properties(width=120)

        st.altair_chart(bar_chart, use_container_width=True)
        
    with tab3:
        st.subheader("All Text")
        if image != " ":
            raw_text = open(image,"r").read().lower()
            st.write(raw_text)

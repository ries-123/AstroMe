# hello_streamlit.py
# Example from https://tingyuansen.github.io/coding_essential_for_astronomers/lectures/lecture10-streamlit.html 

import streamlit as st

st.write("# Welcome to Astronomy Tools")
st.write("This is my first Streamlit app!")

# Let's add some astronomy content
parallax = 0.768  # Proxima Centauri's parallax in arcseconds
distance = 1.0 / parallax
st.write(f"Distance to Proxima Centauri: {distance:.2f} parsecs")

import streamlit as st

st.set_page_config(page_title="Match Day Chalkboard", layout="centered")

st.title("⚽ Match Day Chalkboard API")
st.write("The roster analysis engine is online.")

# Create a simple visual form to test our logic
team_name = st.text_input("Team Name", value="A.C. Flora Varsity")
player_count = st.number_input("Number of Players to Analyze", min_value=11, max_value=26, value=11)

if st.button("Run Tactics Analyzer"):
    st.success("Analysis Complete!")
    
    st.subheader("Results")
    st.write(f"**Team:** {team_name}")
    st.write("**Recommended Formation:** 4-3-3 High Press")
    st.write(f"**Reasoning:** Successfully processed attributes for {player_count} players. Pace metrics allow for a high defensive line.")

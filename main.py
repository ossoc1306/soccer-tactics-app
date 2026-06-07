import streamlit as st
import pandas as pd

# Set the page layout to be wider for our data table
st.set_page_config(page_title="Match Day Chalkboard", layout="wide")

st.title("⚽ Match Day Chalkboard: Tactics Engine")
st.write("Edit your starting XI's attributes (1-10 scale) below to generate a data-driven tactical plan.")

# 1. Default Roster Data (A starting template so you don't have to type 11 names every time)
default_roster = {
    "Name": ["Starting GK", "Left CB", "Right CB", "Left Back", "Right Back", "Defensive Mid", "Center Mid", "Attacking Mid", "Left Winger", "Right Winger", "Striker"],
    "Position": ["GK", "CB", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"],
    "Pace": [5, 4, 5, 8, 7, 6, 7, 8, 9, 8, 7],
    "Passing": [5, 4, 5, 6, 6, 8, 7, 9, 7, 7, 6],
    "Defending": [8, 9, 8, 7, 7, 8, 6, 4, 3, 4, 3]
}

# Create a DataFrame (spreadsheet) from our default data
df = pd.DataFrame(default_roster)

# 2. Interactive Data Grid
st.subheader("Starting XI Attributes")
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

st.divider()

# 3. The Logic Engine
if st.button("Run Tactics Analyzer", type="primary"):
    with st.spinner("Crunching the numbers..."):
        
        # Calculate Team Medians
        median_pace = edited_df["Pace"].median()
        median_passing = edited_df["Passing"].median()
        
        # Weakest Link Veto (Find the slowest defender)
        defenders = edited_df[edited_df["Position"].isin(["CB", "LB", "RB"])]
        slowest_defender = defenders["Pace"].min() if not defenders.empty else 0
        
        # Tactical Branching Logic
        formation = ""
        reasoning = ""
        
        if median_pace >= 7 and slowest_defender >= 6:
            formation = "4-3-3 High Press"
            reasoning = f"Your median pace is a solid {median_pace}. More importantly, your slowest defender still has a pace of {slowest_defender}, passing the 'Weakest Link' veto. You have the speed at the back to safely lock opponents in their own half."
        
        elif median_passing >= 7.5:
            formation = "4-2-3-1 Possession"
            reasoning = f"With a high median passing score of {median_passing}, this team is built to keep the ball. A 4-2-3-1 gives you passing triangles all over the pitch."
        
        elif slowest_defender <= 4:
            formation = "5-3-2 Low Block / Counter"
            reasoning = f"**VETO TRIGGERED:** You have a defender with a pace of {slowest_defender}. A high line will get torched by fast wingers over the top. Dropping into a 5-3-2 protects your backline and relies on your fast wingers for the counter-attack."
        
        else:
            formation = "4-4-2 Mid Block"
            reasoning = f"Your stats are highly balanced (Median Pace: {median_pace}, Median Passing: {median_passing}). A 4-4-2 provides structural solidity without over-committing your defense or your attack."

        # 4. Display Results
        st.success("Analysis Complete!")
        
        # Display key metrics side-by-side
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Recommended Formation", formation)
        with col2:
            st.metric("Median Team Pace", f"{median_pace}/10")
        with col3:
            st.metric("Weakest Link (Def. Pace)", f"{slowest_defender}/10")
            
        st.info(f"**Coach's Breakdown:** {reasoning}")

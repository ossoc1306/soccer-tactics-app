import streamlit as st
import pandas as pd

# Set the page layout to be wider for our data table
st.set_page_config(page_title="Match Day Chalkboard", layout="wide")

st.title("⚽ Match Day Chalkboard: Tactics Engine")
st.write("Customize your starting XI below. Select their preferred position and rate their attributes on a 1-5 scale (5 being elite).")

# 1. Default Roster Data (Blank Slate)
# 10 rows of empty names, unassigned positions, and average (3) attributes
default_roster = {
    "Name": [""] * 10,
    "Position": [None] * 10, 
    "Pace": [3] * 10,
    "Passing": [3] * 10,
    "Defending": [3] * 10
}

df = pd.DataFrame(default_roster)

# 2. Interactive Data Grid with Dropdowns and Limits
st.subheader("Outfield Attributes")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Name": st.column_config.TextColumn(
            "Player Name", 
            placeholder="Enter name..."
        ),
        "Position": st.column_config.SelectboxColumn(
            "Preferred Position",
            help="Select the player's tactical role",
            options=["CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST", "CF"],
            required=True
        ),
        "Pace": st.column_config.NumberColumn("Pace (1-5)", min_value=1, max_value=5, step=1),
        "Passing": st.column_config.NumberColumn("Passing (1-5)", min_value=1, max_value=5, step=1),
        "Defending": st.column_config.NumberColumn("Defending (1-5)", min_value=1, max_value=5, step=1),
    }
)

st.divider()

# 3. The Logic Engine (Updated for 1-5 Scale)
if st.button("Run Tactics Analyzer", type="primary"):
    
    # Safety Check: Make sure they actually selected positions before analyzing
    if edited_df["Position"].isnull().any() or (edited_df["Position"] == "").any():
        st.error("⚠️ Please assign a Position to all 10 players before running the analyzer.")
    else:
        with st.spinner("Crunching the numbers..."):
            
            # Calculate Team Medians
            median_pace = edited_df["Pace"].median()
            median_passing = edited_df["Passing"].median()
            
            # Weakest Link Veto (Find the slowest defender)
            defenders = edited_df[edited_df["Position"].isin(["CB", "LB", "RB"])]
            slowest_defender = defenders["Pace"].min() if not defenders.empty else 0
            
            # Tactical Branching Logic (Scaled down for 1-5)
            formation = ""
            reasoning = ""
            
            if median_pace >= 3.5 and slowest_defender >= 3:
                formation = "4-3-3 High Press"
                reasoning = f"Your outfield median pace is a fast {median_pace:.1f}/5. More importantly, your slowest defender still has a pace of {slowest_defender}/5, passing the veto. You have the speed at the back to safely lock opponents in their own half."
            
            elif median_passing >= 3.5:
                formation = "4-2-3-1 Possession"
                reasoning = f"With a high median passing score of {median_passing:.1f}/5, this team is built to keep the ball. A 4-2-3-1 gives you passing triangles all over the pitch."
            
            elif slowest_defender <= 2 and not defenders.empty:
                formation = "5-3-2 Low Block / Counter"
                reasoning = f"**VETO TRIGGERED:** You have a defender with a pace of {slowest_defender}/5. A high line will get torched by fast wingers over the top. Dropping into a 5-3-2 protects your backline and relies on your fast wingers for the counter-attack."
            
            else:
                formation = "4-4-2 Mid Block"
                reasoning = f"Your stats are highly balanced (Median Pace: {median_pace:.1f}, Median Passing: {median_passing:.1f}). A 4-4-2 provides structural solidity without over-committing your defense or your attack."

            # 4. Display Results
            st.success("Analysis Complete!")
            
            # Display key metrics side-by-side
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Recommended Formation", formation)
            with col2:
                st.metric("Median Outfield Pace", f"{median_pace:.1f}/5")
            with col3:
                st.metric("Weakest Link (Def. Pace)", f"{slowest_defender}/5" if not defenders.empty else "N/A")
                
            st.info(f"**Coach's Breakdown:** {reasoning}")

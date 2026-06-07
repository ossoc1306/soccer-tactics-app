import streamlit as st
import pandas as pd

# Set the page layout to be wider for our data table
st.set_page_config(page_title="Match Day Chalkboard", layout="wide")

st.title("⚽ Match Day Chalkboard: Tactics Engine")
st.write("Manage your 25-man squad below. Check the 'Starter' box for your Matchday XI, and the engine will analyze your tactical setup.")

# 1. Default Roster Data (25-man roster with Coaching Pillars)
default_roster = {
    "Starter": [False] * 25,
    "Name": [""] * 25,
    "Position": [None] * 25, 
    "Technical": [3] * 25,
    "Tactical": [3] * 25,
    "Physical": [3] * 25
}

df = pd.DataFrame(default_roster)

# 2. Interactive Data Grid with Dropdowns and Limits
st.subheader("Squad Roster")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Starter": st.column_config.CheckboxColumn(
            "Starter?",
            help="Select exactly 11 players for the Matchday XI",
            default=False,
        ),
        "Name": st.column_config.TextColumn(
            "Player Name", 
            help="Enter the player's name"
        ),
        "Position": st.column_config.SelectboxColumn(
            "Preferred Position",
            help="Select the player's tactical role",
            options=["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST", "CF"],
            required=True
        ),
        "Technical": st.column_config.NumberColumn(
            "Technical (1-5)", 
            help="Skill on the ball: passing, receiving, striking, defending technique, aerial challenges.", 
            min_value=1, max_value=5, step=1
        ),
        "Tactical": st.column_config.NumberColumn(
            "Tactical (1-5)", 
            help="Soccer brain: understanding concepts, learning/executing movements, positional awareness.", 
            min_value=1, max_value=5, step=1
        ),
        "Physical": st.column_config.NumberColumn(
            "Physical (1-5)", 
            help="Athleticism: height, strength, jumping ability, and pace.", 
            min_value=1, max_value=5, step=1
        ),
    }
)

st.divider()

# 3. The Logic Engine (Rewired for Technical/Tactical/Physical)
if st.button("Run Tactics Analyzer", type="primary"):
    
    # Filter the dataframe to only look at the checked starters
    starters_df = edited_df[edited_df["Starter"] == True]
    
    # Filter out Goalkeepers for the outfield math
    outfield_starters = starters_df[starters_df["Position"] != "GK"]
    
    # Safety Checks: Enforce 11 starters and exactly 10 outfield players
    if len(starters_df) != 11:
        st.error(f"⚠️ You currently have {len(starters_df)} players selected. Please check exactly 11 boxes for your starting lineup.")
    elif len(outfield_starters) != 10:
        st.error(f"⚠️ Your starting XI must include exactly 1 GK and 10 outfield players. You currently have {len(outfield_starters)} outfielders selected.")
    elif outfield_starters["Position"].isnull().any() or (outfield_starters["Position"] == "").any():
        st.error("⚠️ Please assign a Position to all starting outfield players before running the analyzer.")
    else:
        with st.spinner("Crunching the numbers..."):
            
            # Calculate Team Medians (using ONLY the 10 outfield starters)
            median_tech = outfield_starters["Technical"].median()
            median_tact = outfield_starters["Tactical"].median()
            median_phys = outfield_starters["Physical"].median()
            
            # Weakest Link Veto (Find the least physical defender to assess high-line viability)
            defenders = outfield_starters[outfield_starters["Position"].isin(["CB", "LB", "RB"])]
            weakest_defender_phys = defenders["Physical"].min() if not defenders.empty else 0
            
            # Tactical Branching Logic
            formation = ""
            reasoning = ""
            
            if median_phys >= 3.5 and weakest_defender_phys >= 3:
                formation = "4-3-3 High Press"
                reasoning = f"Your squad's Physical median is a high {median_phys:.1f}/5. Crucially, your least athletic defender still has a Physical rating of {weakest_defender_phys}/5, passing the veto. You have the raw athleticism and pace at the back to safely lock opponents in their own half."
            
            elif median_tech >= 3.5 and median_tact >= 3.5:
                formation = "4-2-3-1 Possession"
                reasoning = f"With elite Technical ({median_tech:.1f}/5) and Tactical ({median_tact:.1f}/5) medians, this team is built to keep the ball. A 4-2-3-1 relies heavily on players with high soccer IQs and clean technique to create passing triangles all over the pitch."
            
            elif weakest_defender_phys <= 2 and not defenders.empty:
                formation = "5-3-2 Low Block / Counter"
                reasoning = f"**VETO TRIGGERED:** You have a defender with a Physical rating of {weakest_defender_phys}/5. A high line will get exposed by faster attackers. Dropping into a 5-3-2 protects your less athletic backline while relying on your tactical shape to frustrate the opponent."
            
            else:
                formation = "4-4-2 Mid Block"
                reasoning = f"Your squad profiles as highly balanced across all pillars (Tech: {median_tech:.1f}, Tact: {median_tact:.1f}, Phys: {median_phys:.1f}). A 4-4-2 provides structural solidity without over-committing your defense or demanding extreme athleticism."

            # 4. Display Results
            st.success("Analysis Complete!")
            
            # Display key metrics side-by-side
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Recommended Formation", formation)
            with col2:
                st.metric("Median Technical", f"{median_tech:.1f}/5")
            with col3:
                st.metric("Median Tactical", f"{median_tact:.1f}/5")
            with col4:
                st.metric("Weakest Link (Def. Phys)", f"{weakest_defender_phys}/5" if not defenders.empty else "N/A")
                
            st.info(f"**Coach's Breakdown:** {reasoning}")

import streamlit as st
import pandas as pd

# Set the page layout to be wider for our data table
st.set_page_config(page_title="Match Day Chalkboard", layout="wide")

st.title("⚽ Match Day Chalkboard: Auto-Optimizer")
st.write("Input your squad's ratings. The engine will identify your top talent and build the optimal formation around them.")

# 1. Default Roster Data 
default_roster = {
    "Name": [""] * 25,
    "Position": [None] * 25, 
    "Technical": [3] * 25,
    "Tactical": [3] * 25,
    "Physical": [3] * 25
}

df = pd.DataFrame(default_roster)

# 2. Interactive Data Grid
st.subheader("Squad Roster")

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Name": st.column_config.TextColumn("Player Name", help="Enter the player's name"),
        "Position": st.column_config.SelectboxColumn(
            "Preferred Position",
            options=["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST", "CF"],
            required=True
        ),
        "Technical": st.column_config.NumberColumn("Technical (1-5)", min_value=1, max_value=5, step=1),
        "Tactical": st.column_config.NumberColumn("Tactical (1-5)", min_value=1, max_value=5, step=1),
        "Physical": st.column_config.NumberColumn("Physical (1-5)", min_value=1, max_value=5, step=1),
    }
)

st.divider()

# 3. The Optimizer Engine
if st.button("Optimize Best XI", type="primary"):
    
    # Clean the data: Only look at rows where the coach actually entered a Name and Position
    active_roster = edited_df.dropna(subset=["Position"])
    active_roster = active_roster[active_roster["Name"].str.strip() != ""]
    
    # Calculate a simple Composite Score (Max 15)
    active_roster["Composite"] = active_roster["Technical"] + active_roster["Tactical"] + active_roster["Physical"]
    
    # Separate GK and Outfielders, sorting them by their Composite score (highest first)
    gks = active_roster[active_roster["Position"] == "GK"].sort_values(by="Composite", ascending=False)
    outfielders = active_roster[active_roster["Position"] != "GK"].sort_values(by="Composite", ascending=False)
    
    # Safety Checks
    if len(gks) < 1:
        st.error("⚠️ You must evaluate at least 1 Goalkeeper.")
    elif len(outfielders) < 10:
        st.error(f"⚠️ You need to evaluate at least 10 outfield players. Currently evaluated: {len(outfielders)}")
    else:
        with st.spinner("Finding optimal combinations..."):
            
            # Grab the absolute Best XI
            best_gk = gks.head(1)
            best_10_outfield = outfielders.head(10)
            best_11 = pd.concat([best_gk, best_10_outfield])
            
            # Analyze the positional QUALITY of the Best 10 Outfielders
            wingers = best_10_outfield[best_10_outfield["Position"].isin(["LW", "RW"])]
            winger_avg = wingers["Composite"].mean() if not wingers.empty else 0
            winger_count = len(wingers)
            
            cms = best_10_outfield[best_10_outfield["Position"].isin(["CDM", "CM", "CAM"])]
            cm_avg = cms["Composite"].mean() if not cms.empty else 0
            cm_count = len(cms)
            
            cbs = best_10_outfield[best_10_outfield["Position"].isin(["CB"])]
            cb_avg = cbs["Composite"].mean() if not cbs.empty else 0
            cb_count = len(cbs)
            
            formation = ""
            reasoning = ""
            
            # Dynamic Tactical Logic Based on POSITIONAL QUALITY
            if cb_count >= 3 and cb_avg >= cm_avg and cb_avg >= winger_avg:
                formation = "3-5-2 / 5-3-2 Wingback"
                reasoning = f"Your Center Backs are among the highest-performing units in your Best XI (Avg Score: {cb_avg:.1f}/15). A 3-at-the-back system maximizes this defensive quality."
            
            elif cm_avg > winger_avg and cm_count >= 3:
                formation = "4-4-2 Diamond or 4-3-2-1 Narrow"
                reasoning = f"Your central midfielders heavily outperform your wide players (CM Avg: {cm_avg:.1f}/15 vs Winger Avg: {winger_avg:.1f}/15). Packing the midfield allows you to control the game through your best players and hide weaknesses out wide."
            
            elif winger_avg > cm_avg and winger_count >= 2:
                formation = "4-3-3 High Press"
                reasoning = f"Your wide players are a major strength compared to the center of the park (Winger Avg: {winger_avg:.1f}/15 vs CM Avg: {cm_avg:.1f}/15). A 4-3-3 isolates these high-quality players on the flanks where they can do the most damage."
            
            else:
                formation = "4-2-3-1 Balanced"
                reasoning = "Your squad's talent is relatively balanced across all positional units. The 4-2-3-1 is the most flexible shape to accommodate this without exposing any glaring weaknesses."

            # Display Results
            st.success("Optimization Complete!")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Recommended Formation", formation)
            with col2:
                st.info(f"**Why?** {reasoning}")
                
            # Display the generated Best XI roster table below the recommendation
            st.subheader("Generated Best XI Roster")
            
            # Formatting the table to look clean
            display_df = best_11[["Name", "Position", "Composite", "Technical", "Tactical", "Physical"]].reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True)

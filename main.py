import streamlit as st
import pandas as pd

# Set the page layout to be wider for our data table
st.set_page_config(page_title="Match Day Chalkboard", layout="wide")

st.title("⚽ Match Day Chalkboard: Auto-Optimizer")
st.write("Input your squad's ratings. The engine will identify your top talent and build the optimal formation around them.")

# 1. Default Roster Data (No more Starter checkbox)
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
            
            # Analyze the position spread of the Best 10 Outfielders
            cb_count = best_10_outfield["Position"].isin(["CB"]).sum()
            cm_count = best_10_outfield["Position"].isin(["CDM", "CM", "CAM"]).sum()
            winger_count = best_10_outfield["Position"].isin(["LW", "RW"]).sum()
            
            formation = ""
            reasoning = ""
            
            # Dynamic Tactical Logic Based on Top Personnel
            if cb_count >= 3:
                formation = "3-5-2 / 5-3-2 Wingback"
                reasoning = f"Three of your highest-rated overall players are Center Backs. A 3-at-the-back system ensures your best defensive talent is on the pitch simultaneously."
            elif winger_count == 0 and cm_count >= 4:
                formation = "4-4-2 Diamond"
                reasoning = f"Your top talent is heavily concentrated centrally ({cm_count} elite midfielders) with no natural wingers making the cut. The diamond allows you to overload the center of the pitch."
            elif winger_count >= 2:
                formation = "4-3-3 High Press"
                reasoning = f"You have elite wide players ({winger_count} top wingers) in your best XI. A 4-3-3 gets your best attackers isolated on the flanks while maintaining a balanced midfield."
            else:
                formation = "4-2-3-1 Balanced"
                reasoning = "Your best 10 players represent a highly balanced mix across all lines. The 4-2-3-1 is the most flexible shape to accommodate this spread of talent naturally."

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

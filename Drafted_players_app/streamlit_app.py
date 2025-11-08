# ============================================================
# streamlit_app.py — College Basketball Assisted Explorer
# Clean, tab-based layout (no sidebar navigation header)
# ============================================================

import pandas as pd
import streamlit as st
from pathlib import Path
from utils import compute_metrics, grouped_player_role_year_overall_chart

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="NCAA-NBA Players Assistant Explorer",
    layout="wide",
)

# ============================================================
# GLOBAL STYLES
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0820;
        color: #f5f5f5;
    }
    thead tr th {
        background-color: #130f30 !important;
    }
    table {
        color: #f5f5f5 !important;
        width: 100% !important;
    }
    hr {
        border: 1px solid #444;
    }
    .stDataFrame div[role="table"] {
        scrollbar-color: #5A4AE3 #0b0820;
    }

    section[data-testid="stSidebar"] div.stMarkdown {
        margin-bottom: 0.4rem !important;
        margin-top: 0.4rem !important;
    }
    section[data-testid="stSidebar"] .stNumberInput {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    section[data-testid="stSidebar"] hr {
        margin-top: 0.3rem !important;
        margin-bottom: 0.6rem !important;
        opacity: 0.3;
    }
    section[data-testid="stSidebar"] label {
        margin-bottom: 0rem !important;
    }
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stSidebarNav"] + div { padding-top: 0 !important; }
    /* --- tighten and center min/max inputs --- */
section[data-testid="stSidebar"] div[data-testid="stNumberInput"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 4px !important;
    margin-top: -6px !important;
    margin-bottom: -6px !important;
}
section[data-testid="stSidebar"] small {
    text-align: center !important;
    display: block !important;
    margin-top: -2px !important;
    margin-bottom: 4px !important;
    color: #aaa !important;
}

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# PATHS + LOAD
# ============================================================
ROOT = Path(__file__).parent
PATH_ASSISTED = ROOT / "temp_data" / "nba_complete_assisted.csv"
PATH_CAREER = ROOT / "temp_data" / "career_drafted.csv"
PATH_BART = ROOT / "temp_data" / "Bart_Core_Positions.csv"


@st.cache_data
def load_data():
    # Debug: Check if files exist
    if not PATH_ASSISTED.exists():
        st.error(f"File not found: {PATH_ASSISTED}")
        st.error(f"Current directory: {Path.cwd()}")
        st.error(
            f"Files in temp_data: {list((ROOT / 'temp_data').glob('*')) if (ROOT / 'temp_data').exists() else 'temp_data folder not found'}")
        st.stop()

    # Load the complete dataset that already has all metrics calculated
    with st.spinner("Loading comprehensive NBA player dataset (1,235 players)..."):
        df_complete = pd.read_csv(PATH_ASSISTED, low_memory=False)
        df_career = pd.read_csv(PATH_CAREER, low_memory=False)
        df_bart = pd.read_csv(PATH_BART, low_memory=False)

    # Ensure player_lower column exists
    if "player_lower" not in df_complete.columns:
        df_complete["player_lower"] = df_complete["Player"].astype(
            str).str.lower().str.strip()

    for df in (df_career, df_bart):
        if "Player_lower" in df.columns:
            df["player_lower"] = df["Player_lower"].astype(
                str).str.lower().str.strip()
        else:
            df["player_lower"] = df["Player"].astype(
                str).str.lower().str.strip()

    # Merge role and year information
    df_career_slim = df_career[["player_lower",
                                "Role", "YR"]].drop_duplicates("player_lower")
    df_bart_slim = df_bart[["player_lower", "Role",
                            "YYR"]].drop_duplicates("player_lower")

    df = df_complete.merge(df_career_slim, on="player_lower", how="left")
    df = df.merge(df_bart_slim, on="player_lower",
                  how="left", suffixes=("", "_bart"))
    df["Role_final"] = df["Role"].fillna(df["Role_bart"])
    df["Year_final"] = df["YR"].fillna(df["YYR"])

    return df, df_complete, df_career, df_bart


# Load data with progress indicator
with st.spinner("Initializing NCAA-NBA Player Explorer..."):
    df, df_complete, df_career, df_bart = load_data()


# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3 = st.tabs([
    "🏀 Assisted & Rim Explorer",
    "📊 Player Profile & Compare Players",
    "🎯 Player Similarity & Radar Charts"
])

# ============================================================
# TAB 1 — ASSISTED & RIM EXPLORER
# ============================================================
with tab1:
    st.title("Assisted Percentage Explorer")

    st.markdown("#### Column Descriptions")

    # Three-column layout for better organization
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            **🎯 Field Goal %**  
            **NonDunk_Rim%** — FG% at rim excluding dunks  
            **Total_Rim%** — FG% at rim including dunks  
            **Mid_FG%** — Midrange FG%  
            **TwoPt_FG%** — Combined 2P FG%  
            **Three_FG%** — 3P FG%
            """
        )

    with col2:
        st.markdown(
            """
            **📊 Shot Frequency**  
            **Rim_Freq** — % of shots at rim  
            **Mid_Freq** — % of shots midrange  
            **Three_Freq** — % of shots from 3PT  
            **TwoPt_Freq** — % of shots inside arc
            """
        )

    with col3:
        st.markdown(
            """
            **🤝 Assisted %**  
            **NonDunk_Assisted%** — Non-dunk rim assists  
            **Total_Assisted_Rim%** — Total rim assists  
            **Mid_Assisted%** — Midrange assists  
            **TwoPt_Assisted%** — 2P assists  
            **Three_Assisted%** — 3P assists  
            **Total_Assisted%** — Overall assists
            """
        )

    # Footer info
    st.markdown(
        """
        ---
        *Data source: BartTorvik.com* | *Page by Dray Mottishaw (@draymottishaw on Twitter/X)*  
        📊 **Dataset**: Complete career totals for 1,235 NCAA players who made it to the NBA
        """)

    st.markdown("<br>", unsafe_allow_html=True)

    # Sidebar filters
    st.sidebar.header("Filters")

    # Add performance controls
    st.sidebar.markdown("### 📊 Display Options")
    max_players = st.sidebar.selectbox(
        "Max Players to Display",
        [100, 250, 500, 1000, 1235],
        index=1,  # Default to 250
        help="Limit results for better performance"
    )

    # Create sort options from all available stat columns
    stat_cols = [
        "NonDunk_Rim%", "Total_Rim%", "Mid_FG%", "Three_FG%", "TwoPt_FG%",
        "Rim_Freq", "Mid_Freq", "Three_Freq", "TwoPt_Freq",
        "NonDunk_Assisted%", "Total_Assisted_Rim%", "Mid_Assisted%",
        "Three_Assisted%", "TwoPt_Assisted%", "Total_Assisted%"
    ]

    pretty_names = {
        "NonDunk_Rim%": "Non-Dunk Rim FG%",
        "Total_Rim%": "Total Rim FG%",
        "Mid_FG%": "Midrange FG%",
        "Three_FG%": "3PT FG%",
        "TwoPt_FG%": "2PT FG%",
        "Rim_Freq": "Rim Shot Freq%",
        "Mid_Freq": "Midrange Shot Freq%",
        "Three_Freq": "3PT Shot Freq%",
        "TwoPt_Freq": "2PT Shot Freq%",
        "NonDunk_Assisted%": "Non-Dunk Rim Assisted%",
        "Total_Assisted_Rim%": "Total Rim Assisted%",
        "Mid_Assisted%": "Midrange Assisted%",
        "Three_Assisted%": "3PT Assisted%",
        "TwoPt_Assisted%": "2PT Assisted%",
        "Total_Assisted%": "Overall Assisted%"
    }

    # Create sort options with pretty names
    sort_options = ["Player"] + stat_cols
    sort_display = ["Player Name"] + [pretty_names[col] for col in stat_cols]
    sort_mapping = dict(zip(sort_display, sort_options))

    sort_display_selected = st.sidebar.selectbox(
        "Sort by",
        sort_display,
        index=15,  # Default to "Overall Assisted%" (Total_Assisted%)
        help="Choose column to sort results by"
    )
    sort_by = sort_mapping[sort_display_selected]

    roles = sorted(df["Role_final"].dropna().unique())
    years = sorted(df["Year_final"].dropna().unique(), key=lambda x: {
                   "Fr": 1, "So": 2, "Jr": 3, "Sr": 4}.get(x, 99))

    # Add "Unknown" option for players without role/year data
    roles_with_unknown = roles + ["Unknown (500 players)"]
    years_with_unknown = years + ["Unknown"]

    selected_roles = st.sidebar.multiselect(
        "Role", roles_with_unknown, default=roles)
    selected_years = st.sidebar.multiselect(
        "Year", years_with_unknown, default=years)
    search_txt = st.sidebar.text_input(
        "Search Player", placeholder="Type player name...")

    st.sidebar.markdown("### QUERY")

    range_filters = {}

    for col in stat_cols:
        st.sidebar.markdown(f"**{pretty_names.get(col, col)}**")
        c1, c2 = st.sidebar.columns(2)
        with c1:
            min_val = st.number_input(
                f"min_{col}", min_value=0.0, max_value=100.0,
                value=0.0, step=0.5, label_visibility="collapsed"
            )
            st.markdown("<small style='color:#aaa;'>Min</small>",
                        unsafe_allow_html=True)
        with c2:
            max_val = st.number_input(
                f"max_{col}", min_value=0.0, max_value=100.0,
                value=100.0, step=0.5, label_visibility="collapsed"
            )
            st.markdown("<small style='color:#aaa;'>Max</small>",
                        unsafe_allow_html=True)

        range_filters[col] = (min_val / 100, max_val / 100)
        st.sidebar.markdown(
            "<hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)

    # Apply filters
    filt = df.copy()

    # Role filtering - handle "Unknown" option
    if selected_roles:
        if "Unknown (500 players)" in selected_roles:
            # Include players with no role data
            known_roles = [r for r in selected_roles if r !=
                           "Unknown (500 players)"]
            if known_roles:
                role_mask = df["Role_final"].isin(
                    known_roles) | df["Role_final"].isna()
            else:
                role_mask = df["Role_final"].isna()
        else:
            role_mask = df["Role_final"].isin(selected_roles)
        filt = filt[role_mask]

    # Year filtering - handle "Unknown" option
    if selected_years:
        if "Unknown" in selected_years:
            known_years = [y for y in selected_years if y != "Unknown"]
            if known_years:
                year_mask = df["Year_final"].isin(
                    known_years) | df["Year_final"].isna()
            else:
                year_mask = df["Year_final"].isna()
        else:
            year_mask = df["Year_final"].isin(selected_years)
        filt = filt[year_mask]

    if search_txt:
        filt = filt[filt["Player"].str.contains(
            search_txt, case=False, na=False)]
    for col, (low, high) in range_filters.items():
        if col not in filt.columns:
            continue  # skip columns that don't exist to avoid KeyError
        # Include both values in range AND NA values (for players with no attempts in certain categories)
        mask = filt[col].between(
            low, high, inclusive="both") | filt[col].isna()
        filt = filt[mask]

    # Sort and limit results for performance
    if len(filt) > 0:
        if sort_by in filt.columns:
            filt = filt.sort_values(
                sort_by, ascending=False, na_position='last')
        else:
            filt = filt.sort_values("Player")

        # Limit results for performance
        if len(filt) > max_players:
            filt = filt.head(max_players)
            st.sidebar.warning(
                f"⚠️ Showing top {max_players} results. Use filters to narrow down.")

    # Role averages - use the same stat_cols as the filters for consistency
    # Safe role average calculation with error handling
    role_avg_map = {}
    for role, g in df.groupby("Role_final"):
        for col in stat_cols:
            if col in g.columns and not g[col].empty:
                role_avg_map[(role, col)] = g[col].mean()
            else:
                # Default value if column missing or empty
                role_avg_map[(role, col)] = 0.0

    # Only include columns that actually exist in the DataFrame
    available_pct_cols = [col for col in stat_cols if col in filt.columns]
    display_cols = ["Player", "Year_final", "Role_final"] + available_pct_cols

    def highlight_row(row):
        role = row["Role_final"]
        styles = []
        for col in display_cols:
            if col in available_pct_cols:
                val = row.get(col)  # Use .get() to safely access columns
                avg = role_avg_map.get((role, col))
                if pd.notna(val) and pd.notna(avg) and avg != 0:
                    diff = val - avg
                    if diff <= -0.10:
                        color = "rgba(255, 71, 71,0.15)"   # bad
                    elif diff <= -0.04:
                        color = "rgba(255, 110, 110,0.25)"  # below
                    elif abs(diff) < 0.02:
                        color = "rgba(211, 219, 160,0.25)"  # avg
                    elif diff < 0.06:
                        color = "rgba(153,245,144,0.35)"   # above
                    else:
                        color = "rgba(47,194,69,0.35)"   # excellent
                else:
                    color = ""
                styles.append(f"background-color: {color}")
            else:
                styles.append("")
        return styles

    st.subheader("NCAA Players Who Played in NBA (2010–2025)")

    # Performance info
    total_after_filters = len(filt) if max_players >= len(filt) else "1000+"
    c1, c2 = st.columns([0.4, 0.6])
    c1.markdown(f"**Showing:** {len(filt):,} players")
    c1.markdown(f"**Total in DB:** {len(df):,}")

    if len(filt) >= max_players:
        c1.markdown(f"**⚡ Limited to:** {max_players:,} for performance")

    c2.markdown(
        """
        <div style="margin-top:12px;text-align:right;color:#aaa;font-size:13px;margin-bottom:4px;">
            Ratings are based on positional averages
        </div>
        <div style="display:flex;gap:8px;justify-content:flex-end;margin-bottom:8px;">
            <span>Legend:</span>
            <span style="background:rgba(255, 71, 71,0.15);padding:4px 10px;border-radius:4px;">Bad</span>
            <span style="background:rgba(255, 110, 110,0.25);padding:4px 10px;border-radius:4px;">Below</span>
            <span style="background:rgba(211, 219, 160,0.250);padding:4px 10px;border-radius:4px;">Avg</span>
            <span style="background:rgba(153,245,144,0.35);padding:4px 10px;border-radius:4px;">Above</span>
            <span style="background:rgba(47,194,69,0.35);padding:4px 10px;border-radius:4px;">Excellent</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Performance optimization: only apply styling to limited rows
    if len(filt) > 0:
        styled_df = (
            filt[display_cols]
            .style.format({c: "{:.1%}" for c in available_pct_cols})
            .apply(highlight_row, axis=1)
        )

        # Adjust height based on number of rows for better performance
        table_height = min(600, max(300, len(filt) * 35 + 100))
        st.dataframe(styled_df, height=table_height, use_container_width=True)
    else:
        st.info("No players match your current filters. Try adjusting the criteria.")

# ============================================================
# TAB 2 — PLAYER COMPARE
# ============================================================
with tab2:
    from pages._Player_Compare import player_compare_app
    # Pass the merged df instead of df_complete
    player_compare_app(df, df_career, df_bart)

# ============================================================
# TAB 3 — PLAYER SIMILARITY & RADAR CHARTS
# ============================================================
with tab3:
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity

    st.title("Player Similarity & Radar Charts")
    st.markdown(
        "Find players with similar playing styles using statistical similarity and compare them with radar charts.")

    # Create metrics for similarity analysis
    similarity_metrics = [
        'Total_Rim%', 'Mid_FG%', 'Three_FG%', 'Rim_Freq', 'Mid_Freq', 'Three_Freq',
        'Total_Assisted%', 'NonDunk_Assisted%', 'Mid_Assisted%', 'Three_Assisted%'
    ]

    # Filter players with complete data for similarity analysis
    df_similarity = df[similarity_metrics + ['Player', 'Role_final']].dropna()

    # Player search
    search_player = st.selectbox(
        "Select a player to find similar players:",
        [""] + sorted(df_similarity['Player'].unique()),
        help="Choose a player to find others with similar playing styles",
        key="search_player_selector"
    )

    if search_player:
        # Calculate similarity
        player_data = df_similarity[df_similarity['Player']
                                    == search_player][similarity_metrics].values

        if len(player_data) > 0:
            # Normalize the data
            scaler = StandardScaler()
            normalized_data = scaler.fit_transform(
                df_similarity[similarity_metrics])
            player_normalized = scaler.transform(player_data)

            # Calculate cosine similarity
            similarities = cosine_similarity(
                player_normalized, normalized_data)[0]

            # Create similarity dataframe
            similarity_df = df_similarity.copy()
            similarity_df['Similarity'] = similarities
            similarity_df = similarity_df.sort_values(
                'Similarity', ascending=False)

            # Remove the selected player from results
            similarity_df = similarity_df[similarity_df['Player']
                                          != search_player]

            st.markdown(f"### 🎯 Shot Diet & FG% Similarity to **{search_player}**:")

            # Show top 28 similar players in 4 columns (7 rows each)
            top_similar = similarity_df.head(28)

            col1, col2, col3, col4 = st.columns(4)
            columns = [col1, col2, col3, col4]

            for idx, (i, row) in enumerate(top_similar.iterrows()):
                similarity_score = row['Similarity'] * 100
                role = row['Role_final'] if pd.notna(
                    row['Role_final']) else 'Unknown'

                # Create gradient color based on similarity rank
                # High similarity = green, lower similarity = red
                if idx < 7:  # Top 7 - green shades
                    color_intensity = 1.0 - (idx / 7) * 0.4  # 1.0 to 0.6
                    color = f"rgba(76, 194, 69, {color_intensity})"
                elif idx < 14:  # Next 7 - yellow/orange shades
                    color_intensity = 0.8 - ((idx - 7) / 7) * 0.3  # 0.8 to 0.5
                    color = f"rgba(255, 193, 7, {color_intensity})"
                elif idx < 21:  # Next 7 - orange shades
                    color_intensity = 0.7 - \
                        ((idx - 14) / 7) * 0.2  # 0.7 to 0.5
                    color = f"rgba(255, 152, 0, {color_intensity})"
                else:  # Last 7 - red shades
                    color_intensity = 0.6 - \
                        ((idx - 21) / 7) * 0.2  # 0.6 to 0.4
                    color = f"rgba(244, 67, 54, {color_intensity})"

                # Distribute across 4 columns
                target_col = columns[idx % 4]
                with target_col:
                    st.markdown(
                        f"""
                        <div style="background-color: {color}; padding: 8px; border-radius: 5px; margin-bottom: 5px; border: 1px solid rgba(255,255,255,0.1);">
                            <strong>{row['Player']}</strong> ({role})<br>
                            <span style="color: #E8E8E8; font-size: 0.9em;">{similarity_score:.1f}% similar</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("---")

    # Universal player comparison selector (outside the similarity section)
    st.markdown("### 🎯 Compare Any Two Players")

    col_left, col_right = st.columns(2)

    with col_left:
        player1 = st.selectbox(
            "Select first player:",
            [""] + (sorted(df_similarity['Player'].unique()) if not search_player else [search_player] +
                    [p for p in sorted(df_similarity['Player'].unique()) if p != search_player]),
            index=0 if not search_player else 0,
            help="Choose any player for comparison",
            key="player1_selector"
        )

    with col_right:
        player2 = st.selectbox(
            "Select second player:",
            [""] + sorted(df_similarity['Player'].unique()),
            help="Choose any player to compare with the first player",
            key="player2_selector"
        )

    if player1 and player2:
        col_chart, col_metrics = st.columns([1, 1])

        with col_chart:
            st.markdown("#### 📊 Radar Chart")

            # Get data for both players
            player1_data = df_similarity[df_similarity['Player']
                                         == player1].iloc[0]
            player2_data = df_similarity[df_similarity['Player']
                                         == player2].iloc[0]

            # Create radar chart for both players
            metrics = ['Total_Rim%', 'Mid_FG%', 'Three_FG%', 'Rim_Freq', 'Mid_Freq', 'Three_Freq',
                       'Total_Assisted%', 'NonDunk_Assisted%', 'Mid_Assisted%', 'Three_Assisted%']

            values1 = [player1_data[metric] for metric in metrics]
            values2 = [player2_data[metric] for metric in metrics]

            angles = [n / float(len(metrics)) * 2 *
                      np.pi for n in range(len(metrics))]
            angles += angles[:1]
            values1 += values1[:1]
            values2 += values2[:1]

            fig, ax = plt.subplots(
                figsize=(7, 7), subplot_kw=dict(projection='polar'))

            # Plot both players
            ax.plot(angles, values1, 'o-', linewidth=2,
                    label=player1, color='#FF6B6B', alpha=0.8)
            ax.fill(angles, values1, alpha=0.25, color='#FF6B6B')

            ax.plot(angles, values2, 'o-', linewidth=2,
                    label=player2, color='#4ECDC4', alpha=0.8)
            ax.fill(angles, values2, alpha=0.25, color='#4ECDC4')

            # Customize chart with transparent background and white text/lines
            metrics_labels = ['Rim FG%', 'Mid FG%', '3PT FG%', 'Rim Freq', 'Mid Freq', '3PT Freq',
                              'Overall Assist%', 'Rim Assist%', 'Mid Assist%', '3PT Assist%']

            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics_labels, size=9,
                               color='white', fontweight='bold')
            ax.set_ylim(0, 1)
            ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'],
                               size=8, color='white', fontweight='bold')

            # White grid lines
            ax.grid(True, color='white', alpha=0.7, linewidth=1)
            ax.set_facecolor('none')  # Transparent background

            # Transparent figure background
            fig.patch.set_facecolor('none')
            fig.patch.set_alpha(0)

            # Legend styling
            legend = ax.legend(loc='upper right',
                               bbox_to_anchor=(1.2, 1.1), frameon=False)
            for text in legend.get_texts():
                text.set_color('white')
                text.set_fontweight('bold')

            st.pyplot(fig, use_container_width=True)

        with col_metrics:
            st.markdown("#### 📈 Side-by-Side Metrics")

            # Create a comparison table
            comparison_data = []
            for metric in metrics:
                comparison_data.append({
                    'Metric': metric,
                    player1: f"{player1_data[metric]:.1%}",
                    player2: f"{player2_data[metric]:.1%}"
                })

            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True,
                         hide_index=True)

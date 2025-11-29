# ============================================================
# streamlit_app.py — College Basketball Assisted Explorer
# Clean, tab-based layout (no sidebar navigation header)
# Force redeploy v2.1 - Fixed chart rendering
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
    
    /* Compact sidebar spacing */
    section[data-testid="stSidebar"] .stRadio {
        margin-top: -0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] .stCheckbox {
        margin-top: -0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] .stSelectbox {
        margin-top: -0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.3rem !important;
        font-size: 1rem !important;
    }
    
    /* Compact main content */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
    }
    h1 {
        margin-bottom: 0.5rem !important;
        padding-bottom: 0 !important;
    }
    h2 {
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
    }
    
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
PATH_NBA_PLAYERS = ROOT / "temp_data" / "nba_players.csv"
PATH_CAREER = ROOT / "temp_data" / "career_drafted.csv"
PATH_BART = ROOT / "temp_data" / "Bart_Core_Positions.csv"
PATH_ALL_ASSISTED = ROOT / "temp_data" / "all_assisted.csv"
PATH_2026_STATS = ROOT / "temp_data" / "2026_stats.csv"
PATH_2026_CURRENT = ROOT / "temp_data" / "2026_current_players.csv"


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
    with st.spinner("Loading comprehensive player dataset..."):
        df_complete = pd.read_csv(PATH_ASSISTED, low_memory=False)
        df_nba_players = pd.read_csv(PATH_NBA_PLAYERS, low_memory=False)
        df_career = pd.read_csv(PATH_CAREER, low_memory=False)
        df_bart = pd.read_csv(PATH_BART, low_memory=False)

        # Load 2026 current players if available
        if PATH_2026_CURRENT.exists():
            df_2026_current = pd.read_csv(PATH_2026_CURRENT, low_memory=False)
        else:
            df_2026_current = None

        # Load 2026 stats if available
        if PATH_2026_STATS.exists():
            df_2026 = pd.read_csv(PATH_2026_STATS, low_memory=False)
        else:
            df_2026 = None

        # Load all_assisted if available (optional for cloud deployment)
        if PATH_ALL_ASSISTED.exists():
            df_all_assisted = pd.read_csv(PATH_ALL_ASSISTED, low_memory=False)
        else:
            df_all_assisted = None

    # Ensure player_lower column exists
    if "player_lower" not in df_complete.columns:
        df_complete["player_lower"] = df_complete["Player"].astype(
            str).str.lower().str.strip()

    for df_temp in (df_nba_players, df_career, df_bart):
        if "Player_lower" in df_temp.columns:
            df_temp["player_lower"] = df_temp["Player_lower"].astype(
                str).str.lower().str.strip()
        else:
            df_temp["player_lower"] = df_temp["Player"].astype(
                str).str.lower().str.strip()

    # Add player_lower to 2026 stats if available
    if df_2026 is not None:
        if "Player_lower" in df_2026.columns:
            df_2026["player_lower"] = df_2026["Player_lower"].astype(
                str).str.lower().str.strip()
        else:
            df_2026["player_lower"] = df_2026["Player"].astype(
                str).str.lower().str.strip()

    # Use complete NBA players data first (includes undrafted), then fallback to drafted-only data
    df_nba_slim = df_nba_players[["player_lower",
                                  "Role", "YR"]].drop_duplicates("player_lower")
    df_career_slim = df_career[["player_lower",
                                "Role", "YR"]].drop_duplicates("player_lower")
    df_bart_slim = df_bart[["player_lower", "Role",
                            "YYR"]].drop_duplicates("player_lower")

    # Add 2026 stats slim version
    if df_2026 is not None:
        df_2026_slim = df_2026[["player_lower", "Role",
                                "YR"]].drop_duplicates("player_lower")
    else:
        df_2026_slim = None

    # Merge with priority: 2026_stats > nba_players (all) > career_drafted > bart
    df = df_complete.copy()

    if df_2026_slim is not None:
        df = df.merge(df_2026_slim, on="player_lower",
                      how="left", suffixes=("", "_2026"))

    df = df.merge(df_nba_slim, on="player_lower", how="left",
                  suffixes=("", "_nba") if df_2026_slim is not None else ("", ""))
    df = df.merge(df_career_slim, on="player_lower",
                  how="left", suffixes=("", "_career"))
    df = df.merge(df_bart_slim, on="player_lower",
                  how="left", suffixes=("", "_bart"))

    # Create final role and year with priority order: 2026 > nba > career > bart
    if df_2026_slim is not None:
        df["Role_final"] = df.get("Role", df.get("Role_2026")).fillna(
            df.get("Role_nba", df.get("Role"))).fillna(
            df.get("Role_career")).fillna(df.get("Role_bart"))
        df["Year_final"] = df.get("YR", df.get("YR_2026")).fillna(
            df.get("YR_nba", df.get("YR")))
    else:
        df["Role_final"] = df["Role"].fillna(
            df["Role_career"]).fillna(df["Role_bart"])
        df["Year_final"] = df["YR"].fillna(df["YYR"])

    # Process all_assisted data (non-NBA players) if available
    df_all_computed = None
    if df_all_assisted is not None:
        if "Player_lower" in df_all_assisted.columns:
            df_all_assisted["player_lower"] = df_all_assisted["Player_lower"].astype(
                str).str.lower().str.strip()
        elif "player_lower" not in df_all_assisted.columns:
            df_all_assisted["player_lower"] = df_all_assisted["Player"].astype(
                str).str.lower().str.strip()

        # Compute metrics for all_assisted data
        from utils import compute_metrics
        df_all_computed = compute_metrics(df_all_assisted, df_career, df_bart)

    # Add dunk metrics to NBA dataset (df) as well
    if "DunkMade" in df.columns and "DunkMiss" in df.columns:
        df["DunkAtt"] = df["DunkMade"] + df["DunkMiss"]
        df["Total_Att"] = df.get("RimAtt", 0) + \
            df.get("Mid_Att", 0) + df.get("Three_Att", 0)
        df["Dunk_Freq"] = df["DunkAtt"].div(
            df["Total_Att"].replace({0: pd.NA}))
        df["Dunk_FG%"] = df["DunkMade"].div(df["DunkAtt"].replace({0: pd.NA}))

    # Process 2026 current players if available
    if df_2026_current is not None:
        # Ensure player_lower exists
        if "player_lower" not in df_2026_current.columns:
            df_2026_current["player_lower"] = df_2026_current["Player"].astype(
                str).str.lower().str.strip()
        # Add Role_final and Year_final
        df_2026_current["Role_final"] = df_2026_current["Role"]
        df_2026_current["Year_final"] = df_2026_current["YR"]

        # Convert Height from "6-5" format to inches
        if "Height" in df_2026_current.columns:
            def height_to_inches(height_str):
                try:
                    if pd.isna(height_str) or height_str == '':
                        return None
                    parts = str(height_str).split('-')
                    if len(parts) == 2:
                        feet, inches = int(parts[0]), int(parts[1])
                        return feet * 12 + inches
                    return None
                except:
                    return None

            df_2026_current['Height'] = df_2026_current['Height'].apply(
                height_to_inches)

    return df, df_complete, df_nba_players, df_career, df_bart, df_all_computed, df_2026_current


# Load data with progress indicator
with st.spinner("Initializing NCAA-NBA Player Explorer..."):
    df, df_complete, df_nba_players, df_career, df_bart, df_all_computed, df_2026_current = load_data()

# Create combined dataset for comparison/similarity tabs (NBA + 2026 current)
if df_2026_current is not None and len(df_2026_current) > 0:
    df_combined = pd.concat([df, df_2026_current], ignore_index=True)
    # Remove duplicates, keeping NBA version if player is in both
    df_combined = df_combined.drop_duplicates(
        subset=['player_lower'], keep='first')
else:
    df_combined = df
    df_2026_current = None  # Ensure it's explicitly None if empty


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
    st.markdown("### Assisted Percentage Explorer")

    # Sidebar filters
    # === SIDEBAR FILTERS ===
    st.sidebar.markdown("**Filters**")

    # Player type filter - only show all options if all_assisted data is available
    if df_all_computed is not None:
        player_type_options = ["NBA Players Only", "2026 Current Players",
                               "Non-NBA Players Only", "All College Players"]
    else:
        player_type_options = ["NBA Players Only", "2026 Current Players"]

    player_type = st.sidebar.radio(
        "Player Dataset",
        player_type_options,
        index=0,
        help="Filter by players who made it to the NBA, 2026 current season players" +
        (", didn't make it to NBA, or show everyone" if df_all_computed is not None else "")
    )
    show_all_players = (
        player_type == "All College Players") if df_all_computed is not None else False
    show_non_nba_only = (
        player_type == "Non-NBA Players Only") if df_all_computed is not None else False
    show_2026_only = (player_type == "2026 Current Players")

    # Draft Year Range Filter (based on when they left college)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📅 Draft Year Range**")

    min_year = st.sidebar.number_input(
        "From Year",
        min_value=2010,
        max_value=2026,
        value=2010,
        step=1,
        help="Players who would have been drafted starting this year (based on their final college season)"
    )

    max_year = st.sidebar.number_input(
        "To Year",
        min_value=2010,
        max_value=2026,
        value=2026,
        step=1,
        help="Players who would have been drafted through this year (based on their final college season)"
    )

    # Ensure min_year <= max_year
    if min_year > max_year:
        st.sidebar.warning("⚠️ 'From' year cannot be greater than 'To' year")
        max_year = min_year

    # Volume Filter
    # Footer info (after player type is defined)
    if show_non_nba_only:
        player_count_text = "28,290 NCAA players who did NOT make it to the NBA"
    elif show_all_players:
        player_count_text = "all 29,525 NCAA Division I players (2010-2025)"
    elif show_2026_only:
        player_count_text = f"{len(df_2026_current) if df_2026_current is not None else 0:,} NCAA players in the 2026 season"
    else:
        player_count_text = "1,235 NCAA players who made it to the NBA"

    st.markdown(
        f"""
        ---
        *Data source: BartTorvik.com* | *Page by Dray Mottishaw (@draymottishaw on Twitter/X)*  
        📊 **Dataset**: Complete career totals for {player_count_text} (2010-2026)
        """)

    # Add performance controls
    st.sidebar.markdown("---")
    st.sidebar.markdown("**📊 Display Options**")

    use_pagination = st.sidebar.checkbox(
        "Use Pagination",
        value=True,
        help="Break results into pages for better performance with large datasets"
    )

    if use_pagination:
        page_size = st.sidebar.selectbox(
            "Players Per Page",
            [100, 250, 500, 1000],
            index=1,  # Default to 250
            help="Number of players to show per page"
        )
    else:
        max_players = st.sidebar.selectbox(
            "Max Players to Display",
            [100, 250, 500, 1000, 2500, 5000, 10000],
            index=2,  # Default to 500
            help="Limit results (no pagination - may be slow for large datasets)"
        )

    # Create sort options from all available stat columns
    stat_cols = [
        "Total_Att", "RimAtt", "Mid_Att", "Three_Att",
        "NonDunk_Rim%", "Total_Rim%", "Mid_FG%", "Three_FG%", "TwoPt_FG%",
        "Rim_Freq", "Mid_Freq", "Three_Freq", "TwoPt_Freq", "Dunk_Freq", "Dunk_FG%",
        "NonDunk_Assisted%", "Total_Assisted_Rim%", "Mid_Assisted%",
        "Three_Assisted%", "TwoPt_Assisted%", "Total_Assisted%"
    ]

    pretty_names = {
        "Total_Att": "Total Attempts",
        "RimAtt": "Rim Attempts",
        "Mid_Att": "Mid Attempts",
        "Three_Att": "Three Attempts",
        "NonDunk_Rim%": "Non-Dunk Rim FG%",
        "Total_Rim%": "Total Rim FG%",
        "Mid_FG%": "Midrange FG%",
        "Three_FG%": "3PT FG%",
        "TwoPt_FG%": "2PT FG%",
        "Rim_Freq": "Rim Shot Freq%",
        "Mid_Freq": "Midrange Shot Freq%",
        "Three_Freq": "3PT Shot Freq%",
        "TwoPt_Freq": "2PT Shot Freq%",
        "Dunk_Freq": "Dunk Shot Freq%",
        "Dunk_FG%": "Dunk FG%",
        "NonDunk_Assisted%": "Non-Dunk Rim Assisted%",
        "Total_Assisted_Rim%": "Total Rim Assisted%",
        "Mid_Assisted%": "Midrange Assisted%",
        "Three_Assisted%": "3PT Assisted%",
        "TwoPt_Assisted%": "2PT Assisted%",
        "Total_Assisted%": "Overall Assisted%"
    }

    # Create sort options with pretty names
    sort_options = ["Player", "Year_final", "Role_final"] + stat_cols
    sort_display = ["Player Name", "Year", "Role"] + \
        [pretty_names[col] for col in stat_cols]
    sort_mapping = dict(zip(sort_display, sort_options))

    sort_display_selected = st.sidebar.selectbox(
        "Sort by",
        sort_display,
        # Default to "Overall Assisted%" (Total_Assisted%) - adjusted for new volume columns
        index=20,
        help="Choose column to sort results by"
    )
    sort_by = sort_mapping[sort_display_selected]

    # Get roles and years from the appropriate dataset
    if show_non_nba_only and df_all_computed is not None:
        # Filter to only non-NBA players (players in all_assisted but not in nba_complete)
        nba_players_lower = set(df["player_lower"].str.lower().str.strip())
        base_df = df_all_computed[~df_all_computed["player_lower"].str.lower(
        ).str.strip().isin(nba_players_lower)].copy()
    elif show_all_players and df_all_computed is not None:
        base_df = df_all_computed
    elif show_2026_only and df_2026_current is not None:
        # Show only 2026 current players
        base_df = df_2026_current.copy()
    else:
        base_df = df

    # Get unique roles and years from selected dataset
    roles = sorted(base_df["Role_final"].dropna().unique()
                   ) if "Role_final" in base_df.columns else []
    years = sorted(base_df["Year_final"].dropna().unique(), key=lambda x: {
                   "Fr": 1, "So": 2, "Jr": 3, "Sr": 4}.get(x, 99)) if "Year_final" in base_df.columns else []

    # Only add "Unknown" option if there are actually unknown values
    has_unknown_roles = base_df["Role_final"].isna(
    ).any() if "Role_final" in base_df.columns else False
    has_unknown_years = base_df["Year_final"].isna(
    ).any() if "Year_final" in base_df.columns else False

    roles_with_unknown = roles + ["Unknown"] if has_unknown_roles else roles
    years_with_unknown = years + ["Unknown"] if has_unknown_years else years

    # Show role/year filters - use N/A if no data to prevent filtering issues
    if roles_with_unknown:
        selected_roles = st.sidebar.multiselect(
            "Role", roles_with_unknown, default=roles_with_unknown, key=f"roles_{player_type}")
    else:
        selected_roles = None  # None means don't filter by role
        st.sidebar.info("⚠️ No Role data for this dataset")

    if years_with_unknown:
        selected_years = st.sidebar.multiselect(
            "Year", years_with_unknown, default=years_with_unknown, key=f"years_{player_type}")
    else:
        selected_years = None  # None means don't filter by year
        st.sidebar.info("⚠️ No Year data for this dataset")
    search_txt = st.sidebar.text_input(
        "Search Player", placeholder="Type player name...")

    st.sidebar.markdown("---")
    st.sidebar.markdown("**QUERY**")

    range_filters = {}

    # Only create range filters for percentage columns, not volume columns
    volume_cols_to_skip = ["Total_Att", "RimAtt", "Mid_Att", "Three_Att"]
    query_cols = [col for col in stat_cols if col not in volume_cols_to_skip]

    # Group columns by type for organized expanders
    fg_pct_cols = ["NonDunk_Rim%", "Total_Rim%",
                   "Mid_FG%", "Three_FG%", "TwoPt_FG%", "Dunk_FG%"]
    freq_cols = ["Rim_Freq", "Mid_Freq",
                 "Three_Freq", "TwoPt_Freq", "Dunk_Freq"]
    assisted_cols = ["NonDunk_Assisted%", "Total_Assisted_Rim%",
                     "Mid_Assisted%", "Three_Assisted%", "TwoPt_Assisted%", "Total_Assisted%"]

    # Volume Filters
    with st.sidebar.expander("📈 Volume Filters"):
        min_volume_input = st.text_input(
            "Minimum Total Attempts",
            value="0",
            help="Filter by minimum total career attempts",
            key="min_total_filter"
        )
        min_volume = int(min_volume_input) if min_volume_input.isdigit() else 0

        min_rim_input = st.text_input(
            "Minimum Rim Attempts",
            value="0",
            help="Filter by minimum rim attempts",
            key="min_rim_filter"
        )
        min_rim = int(min_rim_input) if min_rim_input.isdigit() else 0

        min_mid_input = st.text_input(
            "Minimum Mid Attempts",
            value="0",
            help="Filter by minimum midrange attempts",
            key="min_mid_filter"
        )
        min_mid = int(min_mid_input) if min_mid_input.isdigit() else 0

        min_three_input = st.text_input(
            "Minimum Three Attempts",
            value="0",
            help="Filter by minimum three-point attempts",
            key="min_three_filter"
        )
        min_three = int(min_three_input) if min_three_input.isdigit() else 0

    # FG% Filters
    with st.sidebar.expander("🎯 Field Goal % Filters"):
        for col in fg_pct_cols:
            if col in query_cols:
                st.markdown(f"**{pretty_names.get(col, col)}**")
                c1, c2 = st.columns(2)
                with c1:
                    min_val = st.number_input(
                        f"min_{col}", min_value=0.0, max_value=100.0,
                        value=0.0, step=0.5, label_visibility="collapsed", key=f"min_{col}"
                    )
                    st.markdown(
                        "<small style='color:#aaa;'>Min</small>", unsafe_allow_html=True)
                with c2:
                    max_val = st.number_input(
                        f"max_{col}", min_value=0.0, max_value=100.0,
                        value=100.0, step=0.5, label_visibility="collapsed", key=f"max_{col}"
                    )
                    st.markdown(
                        "<small style='color:#aaa;'>Max</small>", unsafe_allow_html=True)
                range_filters[col] = (min_val / 100, max_val / 100)
                st.markdown("<hr style='border:0.5px solid #333;'>",
                            unsafe_allow_html=True)

    # Shot Frequency Filters
    with st.sidebar.expander("📊 Shot Frequency Filters"):
        for col in freq_cols:
            if col in query_cols:
                st.markdown(f"**{pretty_names.get(col, col)}**")
                c1, c2 = st.columns(2)
                with c1:
                    min_val = st.number_input(
                        f"min_{col}", min_value=0.0, max_value=100.0,
                        value=0.0, step=0.5, label_visibility="collapsed", key=f"min_{col}"
                    )
                    st.markdown(
                        "<small style='color:#aaa;'>Min</small>", unsafe_allow_html=True)
                with c2:
                    max_val = st.number_input(
                        f"max_{col}", min_value=0.0, max_value=100.0,
                        value=100.0, step=0.5, label_visibility="collapsed", key=f"max_{col}"
                    )
                    st.markdown(
                        "<small style='color:#aaa;'>Max</small>", unsafe_allow_html=True)
                range_filters[col] = (min_val / 100, max_val / 100)
                st.markdown("<hr style='border:0.5px solid #333;'>",
                            unsafe_allow_html=True)

    # Assisted % Filters
    with st.sidebar.expander("🤝 Assisted % Filters"):
        for col in assisted_cols:
            if col in query_cols:
                st.markdown(f"**{pretty_names.get(col, col)}**")
                c1, c2 = st.columns(2)
                with c1:
                    min_val = st.number_input(
                        f"min_{col}", min_value=0.0, max_value=100.0,
                        value=0.0, step=0.5, label_visibility="collapsed", key=f"min_{col}"
                    )
                    st.markdown(
                        "<small style='color:#aaa;'>Min</small>", unsafe_allow_html=True)
                with c2:
                    max_val = st.number_input(
                        f"max_{col}", min_value=0.0, max_value=100.0,
                        value=100.0, step=0.5, label_visibility="collapsed", key=f"max_{col}"
                    )
                    st.markdown(
                        "<small style='color:#aaa;'>Max</small>", unsafe_allow_html=True)
                range_filters[col] = (min_val / 100, max_val / 100)
                # Apply filters - use the appropriate dataset based on toggle
                st.markdown("<hr style='border:0.5px solid #333;'>",
                            unsafe_allow_html=True)
    if show_all_players and df_all_computed is not None:
        base_df = df_all_computed
    elif show_non_nba_only and df_all_computed is not None:
        nba_players_lower = set(df["player_lower"].str.lower().str.strip())
        base_df = df_all_computed[~df_all_computed["player_lower"].str.lower(
        ).str.strip().isin(nba_players_lower)].copy()
    elif show_2026_only and df_2026_current is not None:
        # Show only 2026 current players
        base_df = df_2026_current.copy()
    else:
        base_df = df
    filt = base_df.copy()

    # Role filtering - handle "Unknown" option and None (no data)
    if selected_roles is not None and selected_roles:
        if "Unknown" in selected_roles:
            # Include players with no role data
            known_roles = [r for r in selected_roles if r != "Unknown"]
            if known_roles:
                role_mask = base_df["Role_final"].isin(
                    known_roles) | base_df["Role_final"].isna()
            else:
                role_mask = base_df["Role_final"].isna()
        else:
            role_mask = base_df["Role_final"].isin(selected_roles)
        filt = filt[role_mask]

    # Year filtering - handle "Unknown" option and None (no data)
    if selected_years is not None and selected_years:
        if "Unknown" in selected_years:
            known_years = [y for y in selected_years if y != "Unknown"]
            if known_years:
                year_mask = base_df["Year_final"].isin(
                    known_years) | base_df["Year_final"].isna()
            else:
                year_mask = base_df["Year_final"].isna()
        else:
            year_mask = base_df["Year_final"].isin(selected_years)
        filt = filt[year_mask]

    # Draft year filtering (based on Last_Season = final college year)
    if 'Last_Season' in filt.columns and not show_2026_only:
        # Filter players whose final college season falls within the range
        # For 2026, also include players who only have First_Season = 2026 (current season)
        if max_year == 2026:
            season_mask = (
                ((filt['Last_Season'] >= min_year) & (filt['Last_Season'] <= max_year)) |
                ((filt['Last_Season'].isna()) & (filt['First_Season']
                 >= min_year) & (filt['First_Season'] <= max_year))
            )
        else:
            season_mask = (
                (filt['Last_Season'] >= min_year) &
                (filt['Last_Season'] <= max_year)
            ) | filt['Last_Season'].isna()
        filt = filt[season_mask]

    if search_txt:
        filt = filt[filt["Player"].str.contains(
            search_txt, case=False, na=False)]

    # Apply volume filters
    if min_volume > 0 and "Total_Att" in filt.columns:
        filt = filt[filt["Total_Att"] >= min_volume]

    if min_rim > 0 and "RimAtt" in filt.columns:
        filt = filt[filt["RimAtt"] >= min_rim]

    if min_mid > 0 and "Mid_Att" in filt.columns:
        filt = filt[filt["Mid_Att"] >= min_mid]

    if min_three > 0 and "Three_Att" in filt.columns:
        filt = filt[filt["Three_Att"] >= min_three]

    for col, (low, high) in range_filters.items():
        if col not in filt.columns:
            continue  # skip columns that don't exist to avoid KeyError
        # Include both values in range AND NA values (for players with no attempts in certain categories)
        mask = filt[col].between(
            low, high, inclusive="both") | filt[col].isna()
        filt = filt[mask]

    # Sort results
    if len(filt) > 0:
        if sort_by in filt.columns:
            filt = filt.sort_values(
                sort_by, ascending=False, na_position='last')
        else:
            filt = filt.sort_values("Player")

        # Apply pagination or limit
        if use_pagination:
            total_results = len(filt)
            total_pages = (total_results + page_size -
                           1) // page_size  # Ceiling division

            if total_pages > 1:
                page_num = st.number_input(
                    f"Page (1-{total_pages})",
                    min_value=1,
                    max_value=total_pages,
                    value=1,
                    step=1,
                    help=f"Showing {page_size} players per page out of {total_results:,} total results"
                )
                start_idx = (page_num - 1) * page_size
                end_idx = start_idx + page_size
                filt = filt.iloc[start_idx:end_idx]

                st.info(
                    f"📄 Page {page_num} of {total_pages} | Showing results {start_idx + 1:,}-{min(end_idx, total_results):,} of {total_results:,} total")
            else:
                st.info(
                    f"📄 Showing all {total_results:,} results (single page)")
        else:
            # Non-pagination mode - just limit
            if len(filt) > max_players:
                filt = filt.head(max_players)
                st.sidebar.warning(
                    f"⚠️ Showing top {max_players} results. Use filters to narrow down or enable pagination.")

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
    # Put volume columns first among stats for visibility
    volume_cols = ["Total_Att", "RimAtt", "Mid_Att", "Three_Att"]
    other_cols = [col for col in available_pct_cols if col not in volume_cols]
    display_cols = ["Player", "Year_final",
                    "Role_final"] + volume_cols + other_cols

    def highlight_row(row):
        role = row["Role_final"]
        styles = []
        volume_cols_set = {"Total_Att", "RimAtt", "Mid_Att", "Three_Att"}
        for col in display_cols:
            # Don't color volume columns or player info columns
            if col in available_pct_cols and col not in volume_cols_set:
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

    # Set title based on selected dataset
    if show_non_nba_only:
        dataset_title = "Non-NBA Players (2010–2025)"
    elif show_all_players:
        dataset_title = "All NCAA D-I Players (2010–2025)"
    else:
        dataset_title = "NCAA Players → NBA (2010–2025)"
    st.markdown(f"**{dataset_title}**")

    # Performance info with legend on same line
    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <div style="font-size:14px;">
                <strong>Page:</strong> {len(filt):,} players | <strong>Total:</strong> {len(base_df):,}
            </div>
            <div style="display:flex;gap:8px;align-items:center;font-size:12px;">
                <span style="font-weight:500;color:#aaa;">Legend:</span>
                <span style="background:rgba(255, 71, 71,0.15);padding:3px 10px;border-radius:4px;">Bad</span>
                <span style="background:rgba(255, 110, 110,0.25);padding:3px 10px;border-radius:4px;">Below</span>
                <span style="background:rgba(211, 219, 160,0.250);padding:3px 10px;border-radius:4px;">Avg</span>
                <span style="background:rgba(153,245,144,0.35);padding:3px 10px;border-radius:4px;">Above</span>
                <span style="background:rgba(47,194,69,0.35);padding:3px 10px;border-radius:4px;">Excellent</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Performance optimization: only apply styling to limited rows
    if len(filt) > 0:
        # Format only percentage columns, not volume columns
        volume_cols_set = {"Total_Att", "RimAtt", "Mid_Att", "Three_Att"}
        pct_cols_to_format = {
            c: "{:.1%}" for c in available_pct_cols if c not in volume_cols_set}

        styled_df = (
            filt[display_cols]
            .style.format(pct_cols_to_format)
            .apply(highlight_row, axis=1)
        )

        # Adjust height based on number of rows for better performance
        table_height = min(600, max(300, len(filt) * 35 + 100))
        st.dataframe(styled_df, height=table_height, use_container_width=True)

        # Column descriptions below the table
        st.markdown("---")
        st.markdown("**Column Descriptions**")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                """
                **📈 Volume**  
                **Total_Att** — Total career shot attempts  
                **RimAtt** — Rim attempts  
                **Mid_Att** — Midrange attempts  
                **Three_Att** — Three-point attempts
                
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
                
                **🏀 Dunk Metrics**  
                **Dunk_Freq** — % of shots that are dunks  
                **Dunk_FG%** — Dunk field goal %
                """
            )
    else:
        st.info("No players match your current filters. Try adjusting the criteria.")

# ============================================================
# TAB 2 — PLAYER COMPARE
# ============================================================
with tab2:
    from pages._Player_Compare import player_compare_app
    # Pass the combined df (NBA + 2026 current players)
    # Don't pass optional parameters to avoid Streamlit Cloud issues
    player_compare_app(
        df_merged=df_combined,
        df_career=df_career,
        df_bart=df_bart
    )  # ============================================================
# TAB 3 — PLAYER SIMILARITY & RADAR CHARTS
# ============================================================
with tab3:
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity

    st.markdown("### Player Similarity & Radar Charts")
    st.markdown(
        "Find players with similar **shot diets** (where they get their shots), volume, height, and playing styles. Similarity includes shot location frequencies, volume, height, shooting efficiency, and shot creation style.")

    # Unique metrics for dataframe selection
    unique_metrics = [
        'Rim_Freq', 'Mid_Freq', 'Three_Freq', 'TwoPt_Freq',
        'RimAtt', 'Mid_Att', 'Three_Att',
        'Total_Assisted%', 'Mid_Assisted%', 'Three_Assisted%', 'TwoPt_Assisted%', 'NonDunk_Assisted%',
        'Three_FG%', 'Total_Rim%',
        'Height'
    ]

    # Filter players with complete data for similarity analysis (includes 2026 current players)
    df_similarity = df_combined[unique_metrics +
                                ['Player', 'Role_final']].dropna()

    # Player search
    search_player = st.selectbox(
        "Select a player to find similar players:",
        [""] + sorted(df_similarity['Player'].unique()),
        help="Choose a player to find others with similar playing styles",
        key="search_player_selector"
    )

    if search_player:
        # Check if selected player is from 2026
        is_2026_player = (df_2026_current is not None and
                          len(df_2026_current) > 0 and
                          search_player in df_2026_current['Player'].values)

        # If 2026 player, only compare against NBA players
        if is_2026_player:
            df_comparison = df_similarity[df_similarity['Player'].isin(
                df['Player'])]
        else:
            df_comparison = df_similarity

        # Calculate similarity with boosted weights for volume and height
        player_data = df_similarity[df_similarity['Player']
                                    == search_player][unique_metrics].values

        if len(player_data) > 0:
            # Get data and apply weights by duplicating columns
            comparison_data = df_comparison[unique_metrics].values
            
            # Replace any NaN or inf values with 0
            comparison_data = np.nan_to_num(comparison_data, nan=0.0, posinf=0.0, neginf=0.0)
            player_data = np.nan_to_num(player_data, nan=0.0, posinf=0.0, neginf=0.0)

            # Create weighted data by duplicating volume and height columns
            # Indices: 4,5,6 are RimAtt, Mid_Att, Three_Att; 14 is Height
            try:
                weighted_comparison = np.column_stack([
                    comparison_data,  # All original columns (15)
                    comparison_data[:, 4],  # RimAtt duplicate
                    comparison_data[:, 5],  # Mid_Att duplicate
                    comparison_data[:, 6],  # Three_Att duplicate
                    comparison_data[:, 14]  # Height duplicate
                ])

                weighted_player = np.column_stack([
                    player_data,
                    player_data[:, 4],
                    player_data[:, 5],
                    player_data[:, 6],
                    player_data[:, 14]
                ])
            except IndexError:
                # Fallback if Height column doesn't exist
                weighted_comparison = np.column_stack([
                    comparison_data,
                    comparison_data[:, 4],
                    comparison_data[:, 5],
                    comparison_data[:, 6]
                ])

                weighted_player = np.column_stack([
                    player_data,
                    player_data[:, 4],
                    player_data[:, 5],
                    player_data[:, 6]
                ])

            # Normalize the weighted data
            scaler = StandardScaler()
            normalized_data = scaler.fit_transform(weighted_comparison)
            player_normalized = scaler.transform(weighted_player)

            # Calculate cosine similarity
            similarities = cosine_similarity(
                player_normalized, normalized_data)[0]

            # Create similarity dataframe
            similarity_df = df_comparison.copy()
            similarity_df['Similarity'] = similarities
            similarity_df = similarity_df.sort_values(
                'Similarity', ascending=False)

            # Remove the selected player from results
            similarity_df = similarity_df[similarity_df['Player']
                                          != search_player]

            comparison_text = " (vs NBA Players)" if is_2026_player else ""
            st.markdown(
                f"### 🎯 Shot Diet & FG% Similarity to **{search_player}**{comparison_text}:")

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

            # Create unique metrics list for radar chart (no duplicates)
            unique_metrics = [
                'Rim_Freq', 'Mid_Freq', 'Three_Freq', 'TwoPt_Freq',
                'RimAtt', 'Mid_Att', 'Three_Att',
                'Total_Assisted%', 'Mid_Assisted%', 'Three_Assisted%', 'TwoPt_Assisted%', 'NonDunk_Assisted%',
                'Three_FG%', 'Total_Rim%',
                'Height'
            ]

            # Get raw values
            values1_raw = [player1_data[metric] for metric in unique_metrics]
            values2_raw = [player2_data[metric] for metric in unique_metrics]

            # Normalize values to 0-1 scale for radar chart display
            # Use min-max normalization for each metric across all players
            values1_normalized = []
            values2_normalized = []

            for i, metric in enumerate(unique_metrics):
                metric_data = df_combined[metric].dropna()
                min_val = metric_data.min()
                max_val = metric_data.max()

                # Avoid division by zero
                if max_val - min_val > 0:
                    v1_norm = (values1_raw[i] - min_val) / (max_val - min_val)
                    v2_norm = (values2_raw[i] - min_val) / (max_val - min_val)
                else:
                    v1_norm = 0.5
                    v2_norm = 0.5

                values1_normalized.append(v1_norm)
                values2_normalized.append(v2_norm)

            angles = [n / float(len(unique_metrics)) * 2 *
                      np.pi for n in range(len(unique_metrics))]
            angles += angles[:1]
            values1_normalized += values1_normalized[:1]
            values2_normalized += values2_normalized[:1]

            fig, ax = plt.subplots(
                figsize=(7, 7), subplot_kw=dict(projection='polar'))

            # Plot both players with normalized values
            ax.plot(angles, values1_normalized, 'o-', linewidth=2,
                    label=player1, color='#FF6B6B', alpha=0.8)
            ax.fill(angles, values1_normalized, alpha=0.25, color='#FF6B6B')

            ax.plot(angles, values2_normalized, 'o-', linewidth=2,
                    label=player2, color='#4ECDC4', alpha=0.8)
            ax.fill(angles, values2_normalized, alpha=0.25, color='#4ECDC4')

            # Customize chart with transparent background and white text/lines
            metrics_labels = ['Rim Freq', 'Mid Freq', '3PT Freq', '2PT Freq',
                              'Rim Vol', 'Mid Vol', '3PT Vol',
                              'Overall Assist%', 'Mid Assist%', '3PT Assist%', '2PT Assist%', 'NonDunk Assist%',
                              '3PT FG%', 'Rim FG%', 'Height']

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

            # Create a comparison table with proper formatting
            comparison_data = []
            for metric in unique_metrics:
                val1 = player1_data[metric]
                val2 = player2_data[metric]

                # Format based on metric type
                if metric in ['RimAtt', 'Mid_Att', 'Three_Att']:
                    # Volume metrics - show as whole numbers
                    formatted_val1 = f"{val1:.0f}"
                    formatted_val2 = f"{val2:.0f}"
                elif metric == 'Height':
                    # Height in inches - show as whole number
                    formatted_val1 = f"{val1:.0f}\""
                    formatted_val2 = f"{val2:.0f}\""
                else:
                    # Percentages and frequencies
                    formatted_val1 = f"{val1:.1%}"
                    formatted_val2 = f"{val2:.1%}"

                comparison_data.append({
                    'Metric': metric,
                    player1: formatted_val1,
                    player2: formatted_val2
                })

            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, use_container_width=True,
                         hide_index=True)

# ============================================================
# pages/_Player_Compare.py — Player Profile & Comparison (fixed)
# ============================================================

from utils import compute_metrics, grouped_player_role_year_overall_chart
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def player_compare_app(df_merged: pd.DataFrame,
                       df_career: pd.DataFrame,
                       df_bart: pd.DataFrame,
                       df_nba: pd.DataFrame = None,
                       df_2026: pd.DataFrame = None) -> None:
    # Use the pre-computed and merged dataset directly since it already has all metrics and role/year data
    df = df_merged.copy()

    # Separate NBA and 2026 players for dropdown filtering
    if df_nba is not None and df_2026 is not None and len(df_2026) > 0:
        nba_players = set(df_nba["Player"].dropna().unique())
        current_2026_players = set(df_2026["Player"].dropna().unique())
    else:
        # If no 2026 data, all players are considered NBA players
        nba_players = set(df["Player"].dropna().unique())
        current_2026_players = set()
        current_2026_players = set()

    # ========================================================
    # SINGLE PLAYER SECTION
    # ========================================================
    st.subheader("Individual Player Profile")

    player_list = ["(none)"] + sorted(df["Player"].dropna().unique())
    player_pick = st.selectbox("Select Player", options=player_list, index=0)

    if player_pick == "(none)":
        st.info("Select a player to view their assisted and efficiency breakdowns.")
        return

    prow = df.loc[df["Player"] == player_pick].iloc[0]
    role = prow.get("Role_final", "—")
    year = prow.get("Year_final", "—")

    st.markdown(f"**{player_pick}**  |  Role: **{role}**  |  Year: **{year}**")

    c1, c2 = st.columns([2, 1])
    with c1:
        metrics = {
            "Non-dunk Rim%": prow.get("NonDunk_Rim%"),
            "Non-dunk Assisted%": prow.get("NonDunk_Assisted%"),
            "Total Rim%": prow.get("Total_Rim%"),
            "Total Assisted Rim%": prow.get("Total_Assisted_Rim%"),
            "Mid FG%": prow.get("Mid_FG%"),
            "Mid Assisted%": prow.get("Mid_Assisted%"),
            "TwoPt FG%": prow.get("TwoPt_FG%"),
            "TwoPt Assisted%": prow.get("TwoPt_Assisted%"),
            "Three FG%": prow.get("Three_FG%"),
            "Three Assisted%": prow.get("Three_Assisted%"),
            "Total Assisted%": prow.get("Total_Assisted%"),
        }
        dfm = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
        dfm["Value"] = dfm["Value"].apply(
            lambda x: f"{x:.1%}" if pd.notna(x) else "—")
        st.table(dfm)

    with c2:
        # Calculate averages from the current dataset
        player_role = prow.get("Role_final")
        player_year = prow.get("Year_final")

        role_df = df[df["Role_final"] == player_role] if pd.notna(
            player_role) else pd.DataFrame()
        year_df = df[df["Year_final"] == player_year] if pd.notna(
            player_year) else pd.DataFrame()

        role_avg = role_df["Total_Assisted%"].mean(
        ) if not role_df.empty else None
        year_avg = year_df["Total_Assisted%"].mean(
        ) if not year_df.empty else None
        overall_avg = df["Total_Assisted%"].mean(
        ) if "Total_Assisted%" in df.columns else None

        fig_total = grouped_player_role_year_overall_chart(
            "Total Assisted% — Player vs Role/Year/Overall",
            prow.get("Total_Assisted%"),
            role_avg,
            year_avg,
            overall_avg,
        )
        st.pyplot(fig_total)

    def zone_group_section(title: str, stat_map: dict):
        st.markdown(f"#### {title}")
        player_role = prow.get("Role_final")
        player_year = prow.get("Year_final")

        role_df = df[df["Role_final"] == player_role] if pd.notna(
            player_role) else pd.DataFrame()
        year_df = df[df["Year_final"] == player_year] if pd.notna(
            player_year) else pd.DataFrame()

        cols = st.columns(5)
        for (title, (colname, pval)), area in zip(stat_map.items(), cols):
            rmean = role_df[colname].mean() if not role_df.empty else None
            ymean = year_df[colname].mean() if not year_df.empty else None
            overall_mean = df[colname].mean(
            ) if colname in df.columns else None
            with area:
                fig = grouped_player_role_year_overall_chart(
                    title, pval, rmean, ymean, overall_mean)
                st.pyplot(fig)

    # Assisted% (5 charts)
    zone_group_section(
        "Assisted% by Zone (Player vs Role vs Year vs Overall)",
        {
            "Rim (non-dunk) Assisted%": ("NonDunk_Assisted%", prow.get("NonDunk_Assisted%")),
            "Total Rim Assisted%": ("Total_Assisted_Rim%", prow.get("Total_Assisted_Rim%")),
            "Mid Assisted%": ("Mid_Assisted%", prow.get("Mid_Assisted%")),
            "TwoPt Assisted%": ("TwoPt_Assisted%", prow.get("TwoPt_Assisted%")),
            "Three Assisted%": ("Three_Assisted%", prow.get("Three_Assisted%")),
        },
    )

    # Efficiency% (5 charts)
    zone_group_section(
        "Efficiency% by Zone (Player vs Role vs Year vs Overall)",
        {
            "Non-dunk Rim%": ("NonDunk_Rim%", prow.get("NonDunk_Rim%")),
            "Total Rim%": ("Total_Rim%", prow.get("Total_Rim%")),
            "Mid FG%": ("Mid_FG%", prow.get("Mid_FG%")),
            "TwoPt FG%": ("TwoPt_FG%", prow.get("TwoPt_FG%")),
            "Three FG%": ("Three_FG%", prow.get("Three_FG%")),
        },
    )

    # ========================================================
    # PLAYER VS PLAYER COMPARISON — TRUE SIDE-BY-SIDE, DOWNWARD
    # ========================================================
    st.markdown("---")
    st.subheader("Compare Two Players (Side-by-Side)")

    col1, col2 = st.columns(2)
    with col1:
        # Player A can be anyone (NBA or 2026)
        player_a = st.selectbox(
            "Select Player A", sorted(df["Player"].dropna().unique()), key="player_a"
        )
    with col2:
        # Player B - if Player A is 2026, only show NBA players; otherwise show all
        if player_a and player_a in current_2026_players:
            # 2026 player selected, only show NBA players for comparison
            player_b_options = sorted(
                [p for p in nba_players if p in df["Player"].values])
            player_b = st.selectbox(
                "Select Player B (NBA Players Only)", player_b_options, key="player_b"
            )
        else:
            # NBA player or no selection, show all players
            player_b = st.selectbox(
                "Select Player B", sorted(df["Player"].dropna().unique()), key="player_b"
            )

    if not player_a or not player_b:
        return

    pa = df.loc[df["Player"] == player_a].iloc[0]
    pb = df.loc[df["Player"] == player_b].iloc[0]

    # --- LAYOUT: LEFT PLAYER | DIVIDER | RIGHT PLAYER ---
    left, mid, right = st.columns([1, 0.025, 1])

    # ========================================================
    # LEFT PLAYER (A)
    # ========================================================
    with left:
        st.markdown(f"### {player_a}")
        st.markdown(
            f"**Role:** {pa.get('Role_final','—')}  |  **Year:** {pa.get('Year_final','—')}"
        )

        metrics = {
            "Non-dunk Rim%": pa.get("NonDunk_Rim%"),
            "Non-dunk Assisted%": pa.get("NonDunk_Assisted%"),
            "Total Rim%": pa.get("Total_Rim%"),
            "Total Assisted Rim%": pa.get("Total_Assisted_Rim%"),
            "Mid FG%": pa.get("Mid_FG%"),
            "Mid Assisted%": pa.get("Mid_Assisted%"),
            "TwoPt FG%": pa.get("TwoPt_FG%"),
            "TwoPt Assisted%": pa.get("TwoPt_Assisted%"),
            "Three FG%": pa.get("Three_FG%"),
            "Three Assisted%": pa.get("Three_Assisted%"),
            "Total Assisted%": pa.get("Total_Assisted%"),
        }
        dfm_a = pd.DataFrame(list(metrics.items()),
                             columns=["Metric", "Value"])
        dfm_a["Value"] = dfm_a["Value"].apply(
            lambda x: f"{x:.1%}" if pd.notna(x) else "—")
        st.table(dfm_a)

        # Pairs of efficiency | assisted charts
        def chart_pairs_a(pairs):
            for (eff_label, eff_col), (ast_label, ast_col) in pairs:
                st.markdown(
                    f"#### {eff_label.replace(' FG%', '')} vs {ast_label.replace('%', '')}")
                cols = st.columns(2)

                # Efficiency chart
                with cols[0]:
                    rmean = df[df["Role_final"] ==
                               pa["Role_final"]][eff_col].mean()
                    ymean = df[df["Year_final"] ==
                               pa["Year_final"]][eff_col].mean()
                    omean = df[eff_col].mean()
                    fig = grouped_player_role_year_overall_chart(
                        eff_label, pa.get(eff_col), rmean, ymean, omean
                    )
                    for patch in fig.axes[0].patches:
                        patch.set_color("#A16EFF")  # purple
                    st.pyplot(fig)

                # Assisted chart
                with cols[1]:
                    rmean = df[df["Role_final"] ==
                               pa["Role_final"]][ast_col].mean()
                    ymean = df[df["Year_final"] ==
                               pa["Year_final"]][ast_col].mean()
                    omean = df[ast_col].mean()
                    fig = grouped_player_role_year_overall_chart(
                        ast_label, pa.get(ast_col), rmean, ymean, omean
                    )
                    for patch in fig.axes[0].patches:
                        patch.set_color("#FF4DD2")  # hot pink
                    st.pyplot(fig)

                st.markdown("<hr style='border: 0.5px solid #333;'>",
                            unsafe_allow_html=True)

        chart_pairs_a([
            (("Non-dunk Rim%", "NonDunk_Rim%"),
             ("Non-dunk Assisted%", "NonDunk_Assisted%")),
            (("Total Rim%", "Total_Rim%"),
             ("Total Rim Assisted%", "Total_Assisted_Rim%")),
            (("Mid FG%", "Mid_FG%"), ("Mid Assisted%", "Mid_Assisted%")),
            (("TwoPt FG%", "TwoPt_FG%"), ("TwoPt Assisted%", "TwoPt_Assisted%")),
            (("Three FG%", "Three_FG%"), ("Three Assisted%", "Three_Assisted%")),
        ])

    # ========================================================
    # CENTER DIVIDER
    # ========================================================
    with mid:
        st.markdown(
            "<div style='border-left: 1px solid #555; height: 100%; margin: 0 auto;'></div>",
            unsafe_allow_html=True,
        )

    # ========================================================
    # RIGHT PLAYER (B)
    # ========================================================
    with right:
        st.markdown(f"### {player_b}")
        st.markdown(
            f"**Role:** {pb.get('Role_final','—')}  |  **Year:** {pb.get('Year_final','—')}"
        )

        metrics = {
            "Non-dunk Rim%": pb.get("NonDunk_Rim%"),
            "Non-dunk Assisted%": pb.get("NonDunk_Assisted%"),
            "Total Rim%": pb.get("Total_Rim%"),
            "Total Assisted Rim%": pb.get("Total_Assisted_Rim%"),
            "Mid FG%": pb.get("Mid_FG%"),
            "Mid Assisted%": pb.get("Mid_Assisted%"),
            "TwoPt FG%": pb.get("TwoPt_FG%"),
            "TwoPt Assisted%": pb.get("TwoPt_Assisted%"),
            "Three FG%": pb.get("Three_FG%"),
            "Three Assisted%": pb.get("Three_Assisted%"),
            "Total Assisted%": pb.get("Total_Assisted%"),
        }
        dfm_b = pd.DataFrame(list(metrics.items()),
                             columns=["Metric", "Value"])
        dfm_b["Value"] = dfm_b["Value"].apply(
            lambda x: f"{x:.1%}" if pd.notna(x) else "—")
        st.table(dfm_b)

        def chart_pairs_b(pairs):
            for (eff_label, eff_col), (ast_label, ast_col) in pairs:
                st.markdown(
                    f"#### {eff_label.replace(' FG%', '')} vs {ast_label.replace('%', '')}")
                cols = st.columns(2)

                # Efficiency chart
                with cols[0]:
                    rmean = df[df["Role_final"] ==
                               pb["Role_final"]][eff_col].mean()
                    ymean = df[df["Year_final"] ==
                               pb["Year_final"]][eff_col].mean()
                    omean = df[eff_col].mean()
                    fig = grouped_player_role_year_overall_chart(
                        eff_label, pb.get(eff_col), rmean, ymean, omean
                    )
                    for patch in fig.axes[0].patches:
                        patch.set_color("#007CFF")  # blue
                    st.pyplot(fig)

                # Assisted chart
                with cols[1]:
                    rmean = df[df["Role_final"] ==
                               pb["Role_final"]][ast_col].mean()
                    ymean = df[df["Year_final"] ==
                               pb["Year_final"]][ast_col].mean()
                    omean = df[ast_col].mean()
                    fig = grouped_player_role_year_overall_chart(
                        ast_label, pb.get(ast_col), rmean, ymean, omean
                    )
                    for patch in fig.axes[0].patches:
                        patch.set_color("#00FFE0")  # neon teal
                    st.pyplot(fig)

                st.markdown("<hr style='border: 0.5px solid #333;'>",
                            unsafe_allow_html=True)

        chart_pairs_b([
            (("Non-dunk Rim%", "NonDunk_Rim%"),
             ("Non-dunk Assisted%", "NonDunk_Assisted%")),
            (("Total Rim%", "Total_Rim%"),
             ("Total Rim Assisted%", "Total_Assisted_Rim%")),
            (("Mid FG%", "Mid_FG%"), ("Mid Assisted%", "Mid_Assisted%")),
            (("TwoPt FG%", "TwoPt_FG%"), ("TwoPt Assisted%", "TwoPt_Assisted%")),
            (("Three FG%", "Three_FG%"), ("Three Assisted%", "Three_Assisted%")),
        ])

# ============================================================
# utils.py — Metrics + Chart Utilities
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


# ============================================================
# COMPUTE METRICS
# ============================================================
def compute_metrics(df_assisted, df_career, df_bart):
    """Compute assisted/efficiency + shot frequency metrics and merge role/year context."""
    df = df_assisted.copy()

    cols = [
        "RimMade", "RimMiss", "RimAst",
        "DunkMade", "DunkMiss", "DunkAst",
        "MidMade", "MidMiss", "MidAst",
        "ThreeMade", "ThreeMiss", "ThreeAst",
    ]
    for c in cols:
        df[c] = pd.to_numeric(df.get(c, 0), errors="coerce").fillna(0)

    # --- Non-dunk rim ---
    df["ND_RimMade"] = (df["RimMade"] - df["DunkMade"]).clip(lower=0)
    df["ND_RimMiss"] = (df["RimMiss"] - df["DunkMiss"]).clip(lower=0)
    df["ND_RimAtt"] = df["ND_RimMade"] + df["ND_RimMiss"]
    df["NonDunk_Rim%"] = df["ND_RimMade"].div(
        df["ND_RimAtt"].replace({0: pd.NA}))
    df["NonDunk_Assisted%"] = (
        (df["RimAst"] - df["DunkAst"]).clip(lower=0)
        .div(df["ND_RimMade"].replace({0: pd.NA}))
    )

    # --- Total rim ---
    df["RimAtt"] = df["RimMade"] + df["RimMiss"]
    df["Total_Rim%"] = df["RimMade"].div(df["RimAtt"].replace({0: pd.NA}))
    df["Total_Assisted_Rim%"] = df["RimAst"].div(
        df["RimMade"].replace({0: pd.NA}))

    # --- Midrange ---
    df["Mid_Att"] = df["MidMade"] + df["MidMiss"]
    df["Mid_FG%"] = df["MidMade"].div(df["Mid_Att"].replace({0: pd.NA}))
    df["Mid_Assisted%"] = df["MidAst"].div(df["MidMade"].replace({0: pd.NA}))

    # --- 2pt combined ---
    df["TwoPt_Att"] = (
        df["RimMade"] + df["RimMiss"] +
        df["MidMade"] + df["MidMiss"]
    )
    df["TwoPt_FG%"] = (
        (df["RimMade"] + df["MidMade"])
        .div(df["TwoPt_Att"].replace({0: pd.NA}))
    )
    df["TwoPt_Assisted%"] = (
        (df["RimAst"] + df["MidAst"])
        .div((df["RimMade"] + df["MidMade"]).replace({0: pd.NA}))
    )

    # --- Three ---
    df["Three_Att"] = df["ThreeMade"] + df["ThreeMiss"]
    df["Three_FG%"] = df["ThreeMade"].div(df["Three_Att"].replace({0: pd.NA}))
    df["Three_Assisted%"] = df["ThreeAst"].div(
        df["ThreeMade"].replace({0: pd.NA}))

    # --- Total Assisted ---
    df["Total_Assisted%"] = (
        (df["RimAst"] + df["MidAst"] + df["ThreeAst"])
        .div((df["RimMade"] + df["MidMade"] + df["ThreeMade"]).replace({0: pd.NA}))
    )

    # ============================================================
    # NEW SECTION — Shot Frequency Metrics
    # ============================================================
    df["Total_Att"] = df["RimAtt"] + df["Mid_Att"] + df["Three_Att"]
    df["Rim_Freq"] = df["RimAtt"].div(df["Total_Att"].replace({0: pd.NA}))
    df["Mid_Freq"] = df["Mid_Att"].div(df["Total_Att"].replace({0: pd.NA}))
    df["Three_Freq"] = df["Three_Att"].div(df["Total_Att"].replace({0: pd.NA}))
    df["TwoPt_Freq"] = df["TwoPt_Att"].div(df["Total_Att"].replace({0: pd.NA}))

    # ============================================================
    # MERGE ROLE / YEAR CONTEXT
    # ============================================================
    df_career_slim = df_career[["player_lower",
                                "Role", "YR"]].drop_duplicates("player_lower")
    df_bart_slim = df_bart[["player_lower", "Role",
                            "YYR"]].drop_duplicates("player_lower")

    df = df.merge(df_career_slim, on="player_lower", how="left")
    df = df.merge(df_bart_slim, on="player_lower",
                  how="left", suffixes=("", "_bart"))
    df["Role_final"] = df["Role"].fillna(df["Role_bart"])
    df["Year_final"] = df["YR"].fillna(df["YYR"])

    # --- Aggregates ---
    df["Role_Avg"] = df.groupby("Role_final")[
        "Total_Assisted%"].transform("mean")
    df["Year_Avg"] = df.groupby("Year_final")[
        "Total_Assisted%"].transform("mean")
    df["Overall_Avg"] = df["Total_Assisted%"].mean()

    return df
# ============================================================
# GROUPED CHART — Player vs Role/Year/Overall
# ============================================================


def grouped_player_role_year_overall_chart(title: str, player_val, role_val, year_val, overall_val):
    """Render mini comparison bar chart with consistent dark styling."""
    fig, ax = plt.subplots(figsize=(3.8, 2.2))

    labels = ["Player", "Role", "Year", "Overall"]
    vals = [
        player_val if pd.notna(player_val) else 0,
        role_val if pd.notna(role_val) else 0,
        year_val if pd.notna(year_val) else 0,
        overall_val if pd.notna(overall_val) else 0,
    ]

    # purple-themed color palette (matches dark app)
    colors = ["#8A2BE2", "#6C63FF", "#9996FF", "#44D7B6"]

    ax.bar(labels, vals, color=colors, edgecolor="white", linewidth=0.6)
    ax.set_title(title, color="white", fontsize=9, pad=4)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.tick_params(colors="white", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#AAA")
    ax.set_facecolor("none")
    fig.patch.set_alpha(0)
    plt.tight_layout()
    return fig

# Drafted — Non-Dunk Rim Streamlit app

This small Streamlit app shows drafted players' rim stats excluding dunks (RimMade - DunkMade, RimMiss - DunkMiss) and assisted counts adjusted the same way (RimAst - DunkAst). It merges `drafted_assisted.csv` with `career_drafted.csv` to group/filter by `Role`.

How to run (PowerShell):

```powershell
pip install -r "c:\Users\dmott\Downloads\Non-Dunk Rim%\requirements.txt"
streamlit run "c:\Users\dmott\Downloads\Non-Dunk Rim%\streamlit_app.py"
```

Notes:
- The app creates `RimMadeAdj`, `RimMissAdj`, `RimAstAdj` and computes `RimPctAdj` = RimMadeAdj / (RimMadeAdj + RimMissAdj).
- Assisted percentage on rim attempts is shown as `RimAstPctAdj` = RimAstAdj / RimTotalAdj.
- If a player is missing a `Role` in `career_drafted.csv`, the Role cell will be blank.

If you want additional sorting columns or a download button for the filtered table, tell me which fields you'd like and I can add them.

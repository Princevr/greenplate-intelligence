"""GreenPlate design system: tokens, CSS, icons and reusable components."""
import altair as alt
import pandas as pd
import streamlit as st

EMERALD, FOREST, SAFFRON, MUTED = "#1FA971", "#0F3D2E", "#D99A1E", "#5F7268"

_I = {
    "trend": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "box": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "list": '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4M12 16h4M8 11h.01M8 16h.01"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "map": '<path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/><path d="M9 3v15M15 6v15"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "db": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/>',
    "grid": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
}


def icon(name, size=20):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{_I[name]}</svg>')


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap');
:root{--forest:#0F3D2E;--deep:#0A2A20;--emerald:#1FA971;--mint:#E4F5EC;--saffron:#D99A1E;--ink:#12241B;--muted:#5F7268;--line:#E1E9E3;--bg:#F4F7F5}
.stApp{font-family:'Figtree',system-ui,sans-serif;background:var(--bg);color:var(--ink)}
h1,h2,h3,h4{font-family:'Bricolage Grotesque',sans-serif!important;color:var(--forest);letter-spacing:-.02em}
#MainMenu,footer{visibility:hidden}header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1380px;padding:1.6rem 2.4rem 3rem}
:focus-visible{outline:2px solid var(--emerald)!important;outline-offset:2px}

/* Sidebar + navigation */
[data-testid="stSidebar"]{background:var(--deep);border-right:0}
[data-testid="stSidebar"] *{color:#DCEBE2}
[data-testid="stSidebar"] hr{border-color:#21493A}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *{color:#8FB09E}
[data-testid="stSidebarNavLink"]{border-radius:8px;padding:7px 10px;margin:1px 0}
[data-testid="stSidebarNavLink"]:hover{background:#15483A}
[data-testid="stSidebarNavLink"][aria-current="page"]{background:var(--emerald)}
[data-testid="stSidebarNavLink"][aria-current="page"] *{color:#04281B!important;font-weight:700}
[data-testid="stNavSectionHeader"] *{color:#7FA390!important;font-size:12px;font-weight:600}
.side-card{background:#0F3D2E;border:1px solid #21493A;border-radius:10px;padding:12px 14px;margin-top:10px}
.side-card b{display:block;font-size:13px;color:#fff}.side-card span{font-size:12px;color:#8FB09E}

/* Page header */
.ph{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin:0 0 22px;padding-bottom:18px;border-bottom:1px solid var(--line)}
.ph-l{display:flex;gap:14px;align-items:flex-start}
.ph-ic{width:44px;height:44px;border-radius:12px;background:var(--forest);color:#6EE0A9;display:flex;align-items:center;justify-content:center;flex:none}
.ph h1{font-size:28px;font-weight:800;margin:0 0 4px;line-height:1.15}
.ph p{margin:0;color:var(--muted);font-size:15px;max-width:700px}
.chip{display:inline-flex;align-items:center;gap:7px;background:#fff;border:1px solid var(--line);border-radius:999px;padding:6px 13px;font-size:12.5px;font-weight:600;color:var(--forest);white-space:nowrap}
.dot{width:7px;height:7px;border-radius:50%;background:var(--emerald)}

/* Components */
.kpi{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 18px;height:100%}
.kpi-l{font-size:13px;color:var(--muted);font-weight:500;margin-bottom:8px}
.kpi-v{font-family:'Bricolage Grotesque',sans-serif;font-size:28px;font-weight:700;color:var(--forest);line-height:1.1}
.kpi-s{font-size:12.5px;color:var(--muted);margin-top:6px}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border-color:var(--line)!important;border-radius:12px}
.sec-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:17px;color:var(--forest);margin:0 0 2px}
.sec-sub{font-size:13px;color:var(--muted);margin-bottom:10px}
.row{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:9px 0;border-bottom:1px solid #EDF2EE;font-size:14px}
.row:last-child{border-bottom:0}.row>span:last-child{color:var(--muted);font-size:13px;text-align:right}
.tag{display:inline-block;padding:2px 10px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.tag-ok{background:#DDF3E7;color:#17623F}.tag-warn{background:#FBEFD2;color:#80570A}.tag-no{background:#ECEFED;color:#5B6962}
.empty{border:1.5px dashed #C4D3C9;border-radius:12px;padding:18px 20px;background:#FAFCFB}
.empty b{color:var(--forest)}.empty ul{margin:8px 0 0;padding-left:18px;color:var(--muted);font-size:14px}
.insight{display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #EDF2EE;font-size:14px;line-height:1.45}.insight:last-child{border-bottom:0}
.insight svg{flex:none;color:var(--emerald);margin-top:2px}
.mod{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 16px 12px}
.mod-i{width:36px;height:36px;border-radius:10px;background:var(--mint);color:var(--forest);display:flex;align-items:center;justify-content:center;margin-bottom:10px}
.mod b{display:block;font-size:15px;color:var(--forest);margin-bottom:4px}.mod span{font-size:13px;color:var(--muted);line-height:1.5;display:block;margin-bottom:8px}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{border-radius:8px;font-weight:600}
.stButton>button[kind="primary"],[data-testid="stFormSubmitButton"]>button,.stDownloadButton>button{background:var(--emerald);border:0;color:#03281A}
[data-testid="stPageLink"] a{border:1px solid var(--line);border-radius:8px;padding:5px 10px;background:#fff;font-weight:600;font-size:13px}
[data-testid="stTabs"] [role="tab"]{font-weight:600}
[data-testid="stDataFrame"]{border:1px solid var(--line);border-radius:10px;overflow:hidden}
.foot{font-size:12.5px;color:var(--muted);padding-top:14px;border-top:1px solid var(--line);margin-top:30px}

/* Landing */
.lp-nav{display:flex;justify-content:space-between;align-items:center;padding:6px 0 26px}
.lp-brand{display:flex;align-items:center;gap:10px;font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:21px;color:var(--forest)}
.lp-mark{width:34px;height:34px;border-radius:10px;background:var(--forest);color:#6EE0A9;display:flex;align-items:center;justify-content:center}
.lp-hero{background:var(--deep);border-radius:22px;padding:54px 50px;color:#fff;position:relative;overflow:hidden}
.lp-hero:after{content:"";position:absolute;right:-120px;top:-140px;width:460px;height:460px;border-radius:50%;background:radial-gradient(circle,#1FA97155,transparent 68%)}
.lp-hero h1{color:#fff!important;font-size:46px;line-height:1.05;font-weight:800;margin:0 0 16px;max-width:680px}
.lp-hero p{color:#B3D0C0;font-size:17px;line-height:1.55;max-width:600px;margin:0}
.lp-h2{font-size:30px;font-weight:800;margin:46px 0 6px}.lp-sub{color:var(--muted);font-size:16px;max-width:660px;margin-bottom:20px}
.step{background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px;height:100%}
.step b{display:block;color:var(--forest);font-size:16px;margin-bottom:6px}.step span{font-size:14px;color:var(--muted);line-height:1.55}
.pill-row{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}.pill-row .chip{background:#12483A;border-color:#21614F;color:#CFEBDD}
@media(max-width:900px){.block-container{padding:1rem}.ph{flex-direction:column;align-items:flex-start}.lp-hero{padding:32px 24px}.lp-hero h1{font-size:32px}.lp-nav{flex-direction:column;gap:10px;align-items:flex-start}}
@media(prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""


def inject():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def hide_sidebar():
    st.markdown("<style>[data-testid='stSidebar'],[data-testid='stSidebarCollapsedControl']{display:none}</style>", unsafe_allow_html=True)


def page_header(title, subtitle, icon_name, source_label=None):
    chip = f"<div class='chip'><span class='dot'></span>{source_label}</div>" if source_label else ""
    st.markdown(f"<div class='ph'><div class='ph-l'><div class='ph-ic'>{icon(icon_name, 22)}</div><div><h1>{title}</h1><p>{subtitle}</p></div></div>{chip}</div>", unsafe_allow_html=True)


def kpi(col, label, value, sub=""):
    col.markdown(f"<div class='kpi'><div class='kpi-l'>{label}</div><div class='kpi-v'>{value}</div><div class='kpi-s'>{sub}</div></div>", unsafe_allow_html=True)


def section(title, sub=""):
    st.markdown(f"<div class='sec-title'>{title}</div><div class='sec-sub'>{sub}</div>", unsafe_allow_html=True)


def tag(label, tone="ok"):
    return f"<span class='tag tag-{tone}'>{label}</span>"


def needs_data(title, items):
    li = "".join(f"<li>{i}</li>" for i in items)
    st.markdown(f"<div class='empty'><b>{title}</b><ul>{li}</ul></div>", unsafe_allow_html=True)


def insights(lines):
    st.markdown("".join(f"<div class='insight'>{icon('check', 16)}<span>{t}</span></div>" for t in lines), unsafe_allow_html=True)


def show_df(data, **kw):
    try:
        st.dataframe(data, width="stretch", **kw)
    except Exception:  # older Streamlit versions
        st.dataframe(data, use_container_width=True, **kw)


def show_chart(chart):
    st.altair_chart(chart.properties(width="container"))


def _clean(ch):
    return ch.configure_view(strokeWidth=0).configure_axis(gridColor="#EBF1EC", labelColor=MUTED, domain=False, tickColor="#EBF1EC")


def trend_chart(s, color=EMERALD, height=280):
    d = s.rename("value").reset_index()
    d.columns = ["date", "value"]
    grad = alt.Gradient(gradient="linear", x1=1, x2=1, y1=1, y2=0, stops=[alt.GradientStop(color="white", offset=0), alt.GradientStop(color=color, offset=1)])
    base = alt.Chart(d).encode(x=alt.X("date:T", title=None), y=alt.Y("value:Q", title=None), tooltip=[alt.Tooltip("date:T"), alt.Tooltip("value:Q", format=",.1f")])
    return _clean((base.mark_area(opacity=.25, color=grad) + base.mark_line(color=color, strokeWidth=2)).properties(height=height))


def bar_chart(s, horizontal=True, color=EMERALD, height=None):
    d = s.rename("value").rename_axis("label").reset_index()
    d["label"] = d["label"].astype(str)
    if horizontal:
        enc = dict(x=alt.X("value:Q", title=None), y=alt.Y("label:N", sort="-x", title=None))
        h = height or max(160, 26 * len(d) + 20)
    else:
        enc = dict(x=alt.X("label:N", sort=None, title=None, axis=alt.Axis(labelAngle=0)), y=alt.Y("value:Q", title=None))
        h = height or 260
    return _clean(alt.Chart(d).mark_bar(color=color, cornerRadiusEnd=4).encode(tooltip=["label", alt.Tooltip("value:Q", format=",.1f")], **enc).properties(height=h))

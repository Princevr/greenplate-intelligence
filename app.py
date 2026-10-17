import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

st.set_page_config(page_title="GreenPlate Intelligence", page_icon="🌱", layout="wide")
st.markdown(r'''<style>
.stApp{background:#f5f8f5;color:#182a22}.block-container{padding-top:1.6rem;padding-bottom:3rem;max-width:1480px}
h1,h2,h3{color:#12392d;letter-spacing:-.025em}h1{font-weight:750!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#102f25,#174737);border-right:1px solid #214c3b}
[data-testid="stSidebar"] *{color:#f2f8f4}[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#b8cec1}
[data-testid="stSidebar"] hr{border-color:#315a48}[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:7px 9px;border-radius:8px;font-size:14px}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#245541}
.hero{background:linear-gradient(115deg,#10382b,#1b6044 58%,#31835a);padding:30px 32px;border-radius:18px;color:white;margin:10px 0 22px;box-shadow:0 10px 28px #14412d18;position:relative;overflow:hidden}
.hero h1{color:white!important;font-size:2rem!important;margin:0 0 8px!important}.hero p{font-size:15px;margin:0;color:#d9eee1;max-width:800px}
[data-testid="stMetric"]{background:white;border:1px solid #e2eae4;border-radius:14px;padding:17px 18px;box-shadow:0 3px 12px #18362508}
[data-testid="stMetricLabel"]{color:#65776b;font-size:13px}[data-testid="stMetricValue"]{color:#163f2e;font-weight:750}
[data-testid="stDataFrame"],[data-testid="stTable"]{border:1px solid #e2eae4;border-radius:12px;overflow:hidden}
.stButton>button,.stDownloadButton>button{border-radius:9px;border:1px solid #207653;font-weight:600}
[data-testid="stAlert"]{border-radius:11px}
@media(max-width:800px){.block-container{padding:1rem}.hero{padding:23px}.hero h1{font-size:1.65rem!important}}
</style>''', unsafe_allow_html=True)

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:#f5f8f5;color:#172b22}.block-container{padding-top:1.25rem;padding-bottom:3rem;max-width:1500px}
h1,h2,h3{font-family:'Manrope',sans-serif;letter-spacing:-.035em}h1{font-weight:800!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0e2d23,#143d2e 58%,#174735)}[data-testid="stSidebar"] [data-testid="stRadio"] label{padding:9px 11px;border-radius:10px;font-size:13px;font-weight:600}[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{background:#245541}
.hero{background:radial-gradient(circle at 88% 12%,#3d916b66 0,transparent 32%),linear-gradient(115deg,#10382b,#1b6044 58%,#31835a);padding:32px 34px;border-radius:22px;color:white;margin:10px 0 24px;box-shadow:0 14px 35px #14412d1b}.hero h1{font-size:2.05rem!important}.eyebrow{font-size:11px;letter-spacing:.14em;font-weight:800;text-transform:uppercase;color:#a6d6b8;margin-bottom:10px}
.topline{display:flex;justify-content:space-between;align-items:center;gap:16px;margin:0 0 14px}.wordmark{font-family:'Manrope',sans-serif;font-weight:800;color:#164d36;font-size:18px}.wordmark span{color:#55946b}.topmeta{font-size:12px;color:#6d7d73;background:#fff;border:1px solid #e3ebe5;border-radius:999px;padding:8px 12px}
.section-kicker{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:#6e8c78;margin:4px 0 8px}.feature-card,.insight-card{background:#fff;border:1px solid #e3ebe5;border-radius:16px;padding:18px;box-shadow:0 4px 16px #163e2c07}.feature-card{min-height:150px;margin-bottom:10px}.feature-icon{width:38px;height:38px;border-radius:12px;background:#e9f5ec;display:flex;align-items:center;justify-content:center;font-size:19px;margin-bottom:13px}.feature-title{font-weight:750;color:#1a3b2b;font-size:15px;margin-bottom:6px}.feature-desc{font-size:12px;line-height:1.55;color:#708077}
[data-testid="stMetric"]{background:white;border:1px solid #e3ebe5;border-radius:15px;padding:18px 19px;box-shadow:0 4px 16px #163e2c06;min-height:110px}[data-testid="stMetricValue"]{color:#163f2e;font-weight:800;font-family:'Manrope',sans-serif}[data-testid="stDataFrame"]{border:1px solid #e3ebe5;border-radius:13px;overflow:hidden}.stButton>button,.stDownloadButton>button{border-radius:10px;font-weight:700;min-height:42px}[data-testid="stAlert"]{border-radius:12px}
@media(max-width:800px){.block-container{padding:1rem}.hero{padding:23px}.hero h1{font-size:1.65rem!important}.feature-card{min-height:unset}}
</style>''', unsafe_allow_html=True)

SOURCES = {
 "Restaurant demand (Germany)": ("data_preprocessed (1)(1).csv", ";", "Daily restaurant product-category demand and engineered features."),
 "Grupo Bimbo sales (Mexico)": ("train_sample_30k.csv", ",", "30,000-row bakery sales/returns sample; not restaurant-specific."),
 "Open Food Facts products": ("open_food_facts_sample(1).csv", ",", "Product-level ingredients, packaging and nutrition fields; not sales data."),
}
PAGES = ["Dashboard", "1. Demand Forecasting", "2. Inventory Intelligence", "3. Supplier & Procurement Intelligence", "4. Food-Waste Intelligence", "5. Customer Intelligence", "6. Logistics & Delivery Optimisation", "7. ESG & Sustainability Reporting", "Dataset Explorer"]

def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def numeric(s):
    return pd.to_numeric(s, errors="coerce")

st.sidebar.markdown("# 🌿 GreenPlate")
st.sidebar.caption("INTELLIGENCE PLATFORM")
st.sidebar.markdown("Automating smarter, sustainable food operations")
st.sidebar.divider()
source = st.sidebar.selectbox("Active data source", list(SOURCES))
filename, default_sep, description = SOURCES[source]
st.sidebar.caption(description)
upload = st.sidebar.file_uploader("Optional: upload a replacement CSV", type=["csv"])
sep_choice = st.sidebar.selectbox("CSV separator", [",", ";", "tab"], index=[",", ";", "tab"].index(default_sep if default_sep != "\t" else "tab"))
sep = "\t" if sep_choice == "tab" else sep_choice
st.sidebar.markdown("**WORKSPACE**")
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("DEMO WORKSPACE")
st.sidebar.caption("Datasets remain separate. Choose the source that fits the module.")

try:
    df = pd.read_csv(upload if upload is not None else filename, sep=sep if upload is not None else default_sep, low_memory=False)
    df.columns = df.columns.astype(str).str.strip()
    if source == "Restaurant demand (Germany)":
        if "DEMAND_DATE" not in df: raise ValueError("Expected a DEMAND_DATE column.")
        df["DEMAND_DATE"] = pd.to_datetime(df["DEMAND_DATE"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["DEMAND_DATE"]).sort_values("DEMAND_DATE")
        targets = [c for c in ["TOTAL", "TOTAL_FISCHPROD", "TOTAL_FLEISCH", "CALAMARI", "FISCH", "GARNELEN", "HAEHNCHEN", "KOEFTE", "LAMM", "STEAK"] if c in df]
    elif source == "Grupo Bimbo sales (Mexico)":
        required = {"Semana", "Producto_ID", "Cliente_ID", "Agencia_ID", "Demanda_uni_equil"}
        if not required.issubset(df.columns): raise ValueError("This does not look like the expected Grupo Bimbo sample.")
        for c in required: df[c] = numeric(df[c])
        df = df.dropna(subset=["Semana", "Demanda_uni_equil"])
        targets = ["Demanda_uni_equil"]
    else:
        for c in ["fat_100g", "sugars_100g", "proteins_100g"]:
            if c in df: df[c] = numeric(df[c])
        targets = []
except FileNotFoundError:
    st.error(f"Cannot find {filename}. Upload the CSV in the sidebar or add it to the same GitHub repository folder as app.py.")
    st.stop()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.info("Check that the selected dataset matches the chosen source and CSV separator.")
    st.stop()

def choose_target(key="target"):
    if not targets:
        st.warning("No recognised demand target is available in this dataset.")
        return None
    default = "TOTAL" if "TOTAL" in targets else targets[0]
    return st.selectbox("Demand measure", targets, index=targets.index(default), key=key)

if page == "Dashboard":
    st.markdown("<div class='topline'><div class='wordmark'>🌿 GreenPlate <span>Intelligence</span></div><div class='topmeta'>● Demo workspace &nbsp; · &nbsp; Sustainable food operations</div></div>", unsafe_allow_html=True)
    st.markdown("""<div class="hero"><div class="eyebrow">OPERATIONS INTELLIGENCE PLATFORM</div><h1 style="color:white!important">Good decisions start with better visibility.</h1><p>Understand demand, improve operational planning and explore sustainability signals — all in one workspace designed for food businesses.</p></div>""", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>WORKSPACE OVERVIEW</div>", unsafe_allow_html=True)
    a,b,c,d=st.columns(4)
    a.metric("Records analysed",f"{len(df):,}",help="Rows in the selected dataset")
    b.metric("Data fields",f"{len(df.columns):,}")
    c.metric("Numeric measures",f"{len(df.select_dtypes(include=np.number).columns):,}")
    d.metric("Data completeness",f"{100*(1-df.isna().sum().sum()/max(1,df.size)):.1f}%",help="Share of non-missing cells")
    left,right=st.columns([1.4,1],gap="large")
    with left:
        st.markdown("<div class='section-kicker'>DATA SNAPSHOT</div><div class='insight-card'>",unsafe_allow_html=True)
        st.markdown(f"**{source}**")
        st.caption(description)
        if source == "Restaurant demand (Germany)" and "DEMAND_DATE" in df:
            valid=df.dropna(subset=["DEMAND_DATE"])
            if not valid.empty: st.markdown(f"**Coverage:** {valid['DEMAND_DATE'].min():%d %b %Y} – {valid['DEMAND_DATE'].max():%d %b %Y}")
            available=[c for c in targets if c in df.columns]
            if available:
                metric_col="TOTAL" if "TOTAL" in available else available[0]
                trend=df.groupby("DEMAND_DATE")[metric_col].apply(lambda x:numeric(x).sum(min_count=1)).dropna().sort_index()
                st.line_chart(trend.tail(90),use_container_width=True)
                st.caption(f"Daily trend · {metric_col} · latest 90 observations")
        elif source == "Grupo Bimbo sales (Mexico)" and "Demanda_uni_equil" in df:
            st.bar_chart(df.groupby("Semana")["Demanda_uni_equil"].sum().sort_index(),use_container_width=True)
            st.caption("Weekly adjusted demand from the Grupo Bimbo sample")
        else: st.info("This is a product catalogue, not a sales time series. Explore product and packaging attributes in ESG reporting.")
        st.markdown("</div>",unsafe_allow_html=True)
    with right:
        st.markdown("<div class='section-kicker'>PLATFORM STATUS</div><div class='insight-card'>",unsafe_allow_html=True)
        st.markdown("**Your intelligence modules**")
        st.caption("Each module uses only the selected dataset. Unsupported insights are clearly identified.")
        rows=[("Demand forecasting","Available for demand data" if source != "Open Food Facts products" else "Needs sales history"),("Inventory intelligence","Planning signals only"),("Supplier & procurement","Scenario comparison"),("Food-waste intelligence","Waste measurements needed"),("Customer intelligence","Customer history needed"),("Logistics optimisation","Route data needed"),("ESG reporting","Product attributes where available")]
        for label,status in rows:
            st.markdown(f"<div style='display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px solid #edf1ed'><span style='font-size:13px;font-weight:650;color:#284735'>{label}</span><span style='font-size:11px;color:#75857a;text-align:right'>{status}</span></div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='section-kicker' style='margin-top:26px'>EXPLORE THE PLATFORM</div>",unsafe_allow_html=True)
    cards=[("📈","Demand Forecasting","Explore demand trends and review an illustrative forecast."),("📦","Inventory Intelligence","Review demand signals for stock planning."),("🧾","Supplier & Procurement","Compare clearly labelled supplier scenarios."),("♻️","Food-Waste Intelligence","Separate measured waste from demand and return signals."),("👥","Customer Intelligence","Explore customer patterns when history supports them."),("🗺️","Logistics & Delivery","Inspect distribution signals and routing data needs."),("🌍","ESG & Sustainability","Explore product and packaging attributes.")]
    for i in range(0,len(cards),4):
        cols=st.columns(4,gap="medium")
        for col,item in zip(cols,cards[i:i+4]):
            with col: st.markdown(f"<div class='feature-card'><div class='feature-icon'>{item[0]}</div><div class='feature-title'>{item[1]}</div><div class='feature-desc'>{item[2]}</div></div>",unsafe_allow_html=True)
    st.caption("Prototype workspace · Outputs are exploratory and depend on data coverage, definitions and validation.")

elif page == "1. Demand Forecasting":
    hero("📈 Demand Forecasting", "Explore demand patterns and evaluate a simple model")
    if source == "Restaurant demand (Germany)":
        target = choose_target()
        if target:
            daily = df.groupby("DEMAND_DATE")[target].apply(lambda x: numeric(x).sum(min_count=1)).dropna().sort_index()
            st.line_chart(daily)
            st.caption("Confirm the source units and definitions before operational use.")
            f = daily.rename("y").to_frame(); f["dow"] = f.index.dayofweek; f["month"] = f.index.month; f["lag1"] = f.y.shift(1); f["lag7"] = f.y.shift(7); f["roll7"] = f.y.shift(1).rolling(7).mean(); f = f.dropna()
            features = ["dow", "month", "lag1", "lag7", "roll7"]
            if len(f) >= 30:
                split = int(len(f)*.8); train, test = f.iloc[:split], f.iloc[split:]
                model = RandomForestRegressor(n_estimators=150, random_state=42, min_samples_leaf=2, n_jobs=-1); model.fit(train[features], train.y); pred = model.predict(test[features])
                mae = mean_absolute_error(test.y, pred); base = mean_absolute_error(test.y, np.repeat(train.y.iloc[-1], len(test)))
                a,b,c = st.columns(3); a.metric("Test MAE", f"{mae:.2f}"); b.metric("Baseline MAE", f"{base:.2f}"); c.metric("Test rows", f"{len(test):,}")
                st.line_chart(pd.DataFrame({"Actual":test.y, "Predicted":pred}, index=test.index))
                nxt = f.index[-1] + pd.Timedelta(days=1); last = f.iloc[-1]
                x = pd.DataFrame([{"dow":nxt.dayofweek,"month":nxt.month,"lag1":last.y,"lag7":f.y.iloc[-7] if len(f)>=7 else last.y,"roll7":f.y.tail(7).mean()}])
                st.metric(f"Illustrative forecast for {nxt:%d %b %Y}", f"{model.predict(x[features])[0]:.2f}")
                st.caption("Chronological holdout test on this dataset only; performance may not generalise to another restaurant.")
            else: st.warning("At least 30 usable daily observations are recommended for this demonstration model.")
    elif source == "Grupo Bimbo sales (Mexico)":
        st.write("Weekly bakery sales sample; not restaurant daily sales.")
        weekly = df.groupby("Semana")["Demanda_uni_equil"].sum().sort_index(); st.line_chart(weekly)
        st.caption("Aggregated by the source's Semana field; consult original documentation for week-code meaning.")
        st.subheader("Top products by adjusted demand"); st.bar_chart(df.groupby("Producto_ID")["Demanda_uni_equil"].sum().nlargest(15).sort_values())
    else: st.warning("Open Food Facts is a product catalogue, not a sales time series. Choose another dataset for forecasting.")

elif page == "2. Inventory Intelligence":
    hero("📦 Inventory Intelligence", "Use demand patterns as planning signals—not automatic order quantities")
    if source == "Restaurant demand (Germany)" and targets:
        target = choose_target("inventory_target")
        if target:
            daily = df.groupby("DEMAND_DATE")[target].apply(lambda x:numeric(x).sum(min_count=1)).dropna().sort_index(); recent = daily.tail(min(28,len(daily)))
            a,b,c = st.columns(3); a.metric("Recent average",f"{recent.mean():.2f}"); b.metric("Recent peak",f"{recent.max():.2f}"); c.metric("Standard deviation",f"{recent.std():.2f}" if len(recent)>1 else "N/A")
            st.line_chart(daily); st.metric("Recent mean + 1 standard deviation", f"{recent.mean() + (recent.std() if len(recent)>1 else 0):.2f}")
    elif source == "Grupo Bimbo sales (Mexico)":
        summary = df.groupby("Producto_ID").agg(adjusted_demand=("Demanda_uni_equil","sum"), units_sold=("Venta_uni_hoy","sum"), returned_units=("Dev_uni_proxima","sum")).sort_values("adjusted_demand",ascending=False).head(20); st.dataframe(summary,use_container_width=True)
        st.caption("These are source demand/return fields, not stock-on-hand or verified food waste.")
    else: st.warning("Product catalogue data does not contain stock-on-hand or replenishment records.")
    st.subheader("Needed for operational recommendations"); st.markdown("- Current stock and units\n- Daily usage/sales by SKU or ingredient\n- Supplier lead time and minimum order quantity\n- Expiry dates and safety-stock policy")

elif page == "3. Supplier & Procurement Intelligence":
    hero("🚚 Supplier & Procurement Intelligence", "Compare hypothetical offers")
    st.warning("No supplied dataset contains verified supplier contracts, purchase prices or lead-time performance. All values below are user-entered scenario assumptions.")
    with st.form("supplier_form"):
        l,r = st.columns(2)
        with l:
            st.markdown("**Supplier A**"); pa=st.number_input("Price per unit (€), A",min_value=0.0,value=2.5,step=.1); la=st.number_input("Lead time (days), A",min_value=0,value=3); ra=st.slider("Reliability (%), A",0,100,95)
        with r:
            st.markdown("**Supplier B**"); pb=st.number_input("Price per unit (€), B",min_value=0.0,value=2.35,step=.1); lb=st.number_input("Lead time (days), B",min_value=0,value=5); rb=st.slider("Reliability (%), B",0,100,88)
        qty=st.number_input("Scenario quantity",min_value=1,value=100,step=10); go=st.form_submit_button("Compare scenario")
    if go: st.dataframe(pd.DataFrame([{"Hypothetical supplier":"A","Purchase cost (€)":pa*qty,"Lead time (days)":la,"Entered reliability (%)":ra},{"Hypothetical supplier":"B","Purchase cost (€)":pb*qty,"Lead time (days)":lb,"Entered reliability (%)":rb}]),use_container_width=True); st.caption("Excludes delivery charges, quality, contract terms and other costs.")

elif page == "4. Food-Waste Intelligence":
    hero("♻️ Food-Waste Intelligence", "Separate demand/returns signals from measured waste")
    if source == "Grupo Bimbo sales (Mexico)":
        st.warning("Returned units are not automatically proof of edible food being wasted.")
        a,b,c=st.columns(3); a.metric("Units sold (source field)",f"{numeric(df['Venta_uni_hoy']).sum():,.0f}"); b.metric("Units returned (source field)",f"{numeric(df['Dev_uni_proxima']).sum():,.0f}"); c.metric("Adjusted demand",f"{numeric(df['Demanda_uni_equil']).sum():,.0f}")
        x=df.groupby("Producto_ID").agg(sold=("Venta_uni_hoy","sum"),returned=("Dev_uni_proxima","sum"),adjusted_demand=("Demanda_uni_equil","sum")); st.dataframe(x.sort_values("returned",ascending=False).head(15),use_container_width=True)
    elif source == "Restaurant demand (Germany)" and targets:
        target=choose_target("waste_target")
        if target:
            daily=df.groupby("DEMAND_DATE")[target].apply(lambda x:numeric(x).sum(min_count=1)).dropna().sort_index(); st.line_chart(daily); st.metric("Days above 90th-percentile demand",int((daily>daily.quantile(.9)).sum())); st.write("Demand variation can guide production review but cannot quantify waste by itself.")
    else: st.warning("Open Food Facts does not include restaurant production, leftovers, expiry or disposal quantities.")
    st.subheader("Needed to measure waste"); st.markdown("- Quantity produced or purchased\n- Quantity sold/served\n- Unsold edible quantity and reason\n- Expired/discarded quantity and date\n- Ingredient weights and unit costs")

elif page == "5. Customer Intelligence":
    hero("👥 Customer Intelligence", "Explore customer-level patterns where supported")
    if source == "Grupo Bimbo sales (Mexico)":
        x=df.groupby("Cliente_ID").agg(adjusted_demand=("Demanda_uni_equil","sum"),records=("Producto_ID","count"),unique_products=("Producto_ID","nunique")).sort_values("adjusted_demand",ascending=False)
        a,b,c=st.columns(3); a.metric("Unique customer IDs",f"{df['Cliente_ID'].nunique():,}"); b.metric("Unique product IDs",f"{df['Producto_ID'].nunique():,}"); c.metric("Customer groups",f"{len(x):,}")
        st.dataframe(x.head(20),use_container_width=True); st.caption("IDs are source identifiers, not named people. Churn needs dated repeat-purchase history and a defined inactivity rule.")
    elif source == "Restaurant demand (Germany)": st.info("This is product-category/day demand rather than customer transaction history. Churn and customer lifetime value cannot be estimated from these fields alone.")
    else: st.info("Open Food Facts describes products rather than customer purchases.")
    st.subheader("Needed for customer analytics"); st.markdown("- Pseudonymous customer ID\n- Dated purchases or subscriptions\n- Order value and product mix\n- Cancellation/inactivity definition")

elif page == "6. Logistics & Delivery Optimisation":
    hero("🗺️ Logistics & Delivery Optimisation", "Check distribution signals and missing routing data")
    st.warning("None of the supplied datasets has the complete combination of delivery coordinates, time windows, vehicle capacity and stop-level records needed to optimise real routes.")
    if source == "Grupo Bimbo sales (Mexico)":
        a,b,c=st.columns(3); a.metric("Agencies",f"{df['Agencia_ID'].nunique():,}"); b.metric("Route IDs",f"{df['Ruta_SAK'].nunique():,}"); c.metric("Customer IDs",f"{df['Cliente_ID'].nunique():,}")
        st.subheader("Demand by agency"); st.bar_chart(df.groupby("Agencia_ID")["Demanda_uni_equil"].sum().nlargest(20))
        st.caption("Identifiers are not geographic coordinates or a complete vehicle-routing dataset.")
    elif source == "Restaurant demand (Germany)": st.info("Daily category demand may help estimate workload, but it does not identify delivery locations or travel times.")
    else: st.info("Product catalogue fields do not describe delivery operations.")
    st.subheader("Needed for route optimisation"); st.markdown("- Delivery addresses or coordinates\n- Orders and quantities per stop\n- Delivery time windows\n- Vehicle capacity and operating hours\n- Travel-time matrix and depot location")

elif page == "7. ESG & Sustainability Reporting":
    hero("🌍 ESG & Sustainability Reporting", "Inspect product-level packaging and nutrition fields")
    if source == "Open Food Facts products":
        a,b,c=st.columns(3); a.metric("Products in sample",f"{len(df):,}"); b.metric("Packaging listed",f"{df['packaging'].notna().sum():,}" if "packaging" in df else "Unavailable"); c.metric("Ingredient text listed",f"{df['ingredients_text'].notna().sum():,}" if "ingredients_text" in df else "Unavailable")
        if "packaging" in df:
            counts=df["packaging"].dropna().astype(str).str.strip(); counts=counts[counts.ne("")].value_counts().head(15)
            if len(counts): st.subheader("Common packaging descriptions"); st.bar_chart(counts)
        cols=[c for c in ["product_name","brands","categories","countries","packaging","ingredients_text","fat_100g","sugars_100g","proteins_100g"] if c in df]
        st.subheader("Product sample"); st.dataframe(df[cols].head(50),use_container_width=True)
        st.caption("This sample does not establish full lifecycle impact, company carbon footprint or ESG-standard compliance. Missing packaging data is not evidence of sustainable packaging.")
    else: st.warning("This dataset does not include company emissions, packaging lifecycle, energy use or verified sustainability indicators.")
    st.subheader("Needed for company ESG reporting"); st.markdown("- Electricity, heating and fuel use\n- Purchased goods and packaging weights/materials\n- Food waste by weight and disposal route\n- Transport distance and fuel data\n- Reporting boundaries, methods and source records")

elif page == "Dataset Explorer":
    hero("🔎 Dataset Explorer", "Inspect columns and data quality")
    a,b=st.columns(2); a.metric("Rows",f"{len(df):,}"); b.metric("Columns",f"{len(df.columns):,}")
    report=pd.DataFrame({"Column":df.columns,"Data type":[str(df[c].dtype) for c in df],"Missing values":[int(df[c].isna().sum()) for c in df],"Missing (%)":[round(float(df[c].isna().mean()*100),2) for c in df],"Unique values":[int(df[c].nunique(dropna=True)) for c in df]})
    st.dataframe(report,use_container_width=True,height=450); st.subheader("First 20 rows"); st.dataframe(df.head(20),use_container_width=True)
    st.download_button("Download column quality report",report.to_csv(index=False).encode("utf-8"),file_name="greenplate_data_quality_report.csv",mime="text/csv")

st.divider()
st.caption("Prototype disclaimer: outputs are exploratory and depend on the selected sample. Validate definitions, units, completeness and model performance before making business decisions.")

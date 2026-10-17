    return st.selectbox("Demand measure", targets, index=targets.index(default), key=key)

if page == "Dashboard":
    hero("🌱 GreenPlate Intelligence", "Decision intelligence for sustainable food operations")
    st.write("This prototype demonstrates selected analytics using separate sample datasets. It is not a production decision system.")
    a,b,c = st.columns(3); a.metric("Selected dataset", source); b.metric("Rows loaded", f"{len(df):,}"); c.metric("Columns loaded", f"{len(df.columns):,}")
    st.info("Restaurant demand supports historical category-demand analysis; Grupo Bimbo supports bakery demand and distribution proxies; Open Food Facts supports product-level exploration. Do not merge these unrelated datasets.")
    st.subheader("Seven core features")
    st.markdown("""1. **Demand Forecasting** — supported by restaurant demand and Grupo Bimbo samples.\n2. **Inventory Intelligence** — demand-based indicators only; stock-on-hand is required for real decisions.\n3. **Supplier & Procurement Intelligence** — supplier scenario only; verified prices and lead times are not supplied.\n4. **Food-Waste Intelligence** — actual waste requires measured discarded quantities; returns are not automatically waste.\n5. **Customer Intelligence** — Grupo Bimbo has customer IDs, but churn requires dated purchase histories and a defined churn rule.\n6. **Logistics & Delivery Optimisation** — actual routing requires coordinates, time windows, vehicle capacity and routes.\n7. **ESG & Sustainability Reporting** — product packaging fields are not a company carbon footprint.""")
    st.subheader("Data preview"); st.dataframe(df.head(10), use_container_width=True)

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

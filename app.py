    if "ordered" not in d or "unsold" not in d:
        st.warning("The selected dataset needs ordered and unsold columns for this analysis.")
    else:
        recent = d.tail(min(28, len(d)))
        c1, c2, c3 = st.columns(3)
        c1.metric("Recent average ordered index", f"{recent['ordered'].mean():.2f}")
        c2.metric("Recent average sales index", f"{recent['sales'].mean():.2f}")
        c3.metric("Recent average unsold index", f"{recent['unsold'].mean():.2f}")
        st.line_chart(recent.set_index("date")[["ordered", "sales", "unsold"]], use_container_width=True)
        st.caption("The source fields are scaled/anonymized indices. They cannot determine actual on-hand stock or stockout quantities.")
        if recent["ordered"].mean() > recent["sales"].mean() and recent["unsold"].mean() > d["unsold"].mean():
            st.warning("Signal for review: recent ordering is above recent sales and recent unsold index is above the full-period average. Review stock and ordering records before making changes.")
        else:
            st.info("No combined ordering/unsold signal was triggered by these simple rules. This is not proof that inventory is optimal.")

elif page == "3. Supplier & Procurement Intelligence":
    hero("🚚 Supplier & Procurement Intelligence", "A structured workflow for comparing suppliers and reviewing purchase decisions")
    st.info("The current dataset does not contain supplier IDs, supplier prices, lead times, minimum order quantities, or delivery reliability. The following is an illustrative input form, not an analysis of real supplier records.")
    with st.form("supplier_demo_form"):
        st.subheader("Enter illustrative supplier details")
        supplier = st.text_input("Supplier name", "Demo Supplier A")
        unit_price = st.number_input("Unit price (€)", min_value=0.0, value=2.50, step=0.10)
        lead_time = st.number_input("Lead time (days)", min_value=0, value=3, step=1)
        reliability = st.slider("On-time delivery rate (%)", min_value=0, max_value=100, value=95)
        quantity = st.number_input("Planned quantity (units)", min_value=0, value=100, step=10)
        submitted = st.form_submit_button("Review illustrative purchase")
    if submitted:
        st.subheader("Illustrative review")
        c1, c2, c3 = st.columns(3)
        c1.metric("Supplier", supplier or "Not provided")
        c2.metric("Estimated purchase cost", f"€{unit_price * quantity:,.2f}")
        c3.metric("Entered on-time rate", f"{reliability}%")
        st.write(f"Entered lead time: **{lead_time} day(s)**.")
        st.caption("These values were entered in the form and are not sourced from the Green AI Hub dataset. Compare multiple verified supplier records before making a purchasing decision.")

elif page == "4. Food-Waste Intelligence":
    hero("♻️ Food-Waste Intelligence", "Explore unsold-food patterns and identify periods for operational review")
    if "unsold" not in d or "ordered" not in d:
        st.warning("The selected dataset does not contain both ordered and unsold fields.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Average sales index", f"{d['sales'].mean():.2f}")
        c2.metric("Average ordered index", f"{d['ordered'].mean():.2f}")
        c3.metric("Average unsold index", f"{d['unsold'].mean():.2f}")
        chart = d.set_index("date")[["sales", "ordered", "unsold"]]
        st.line_chart(chart, use_container_width=True)
        recent = d.tail(min(28, len(d)))
        recent_unsold = recent["unsold"].mean()
        full_unsold = d["unsold"].mean()
        st.subheader("Review signal")
        if recent_unsold > full_unsold:
            st.warning("Recent unsold-food index is above the selected restaurant's full-period average. Review demand, ordering, calendar and weather before adjusting orders.")
        else:
            st.success("Recent unsold-food index is not above the full-period average. Continue monitoring trends.")
        st.caption("This is pattern analysis using anonymized/scaled indices; it does not calculate kilograms, meals, or monetary waste.")

elif page == "5. Customer Intelligence":
    hero("👥 Customer Intelligence", "Prepare customer analytics using an appropriate customer-level dataset")
    st.warning("Customer-level records are not present in the current dataset. Do not interpret store-level sales as individual customer behaviour.")
    st.markdown("**Suitable data to connect:** anonymized customer ID, transaction date, order value, products/categories, subscription status, and cancellations or repeat purchases.")
    st.subheader("Explore a sample customer dataset")
    sample = pd.DataFrame({
        "customer_id": ["C001", "C002", "C003", "C004"],
        "orders_last_90_days": [8, 2, 5, 1],
        "average_order_value_eur": [24.5, 18.0, 31.2, 14.5],
        "days_since_last_order": [7, 48, 15, 75],
    })
    st.caption("Illustrative example only — these rows are not real customers and are not from the connected source dataset.")
    st.dataframe(sample, use_container_width=True, hide_index=True)
    st.info("Once genuine anonymized customer data is available, this module can support repeat-purchase, customer-segmentation and churn-risk analysis. The sample table is not used to train a model.")

elif page == "6. Logistics & Delivery Optimisation":
    hero("🗺️ Logistics & Delivery Optimisation", "Review the data needed to analyse route and delivery efficiency")
    st.warning("The current dataset does not provide delivery stops, route distances, vehicle capacity, delivery windows, or GPS coordinates. It cannot calculate an actual optimized route.")
    st.subheader("Illustrative route planning inputs")
    with st.form("logistics_demo_form"):
        stops = st.number_input("Number of delivery stops", min_value=1, value=8, step=1)
        distance = st.number_input("Estimated total route distance (km)", min_value=0.0, value=35.0, step=1.0)
        fuel = st.number_input("Vehicle fuel consumption (L/100 km)", min_value=0.0, value=8.0, step=0.5)
        emission_factor = st.number_input("Emission factor (kg CO₂ per litre)", min_value=0.0, value=2.68, step=0.01)
        submitted = st.form_submit_button("Estimate entered route")
    if submitted:
        litres = distance * fuel / 100
        emissions = litres * emission_factor
        a, b, c = st.columns(3)
        a.metric("Entered stops", f"{stops}")
        b.metric("Estimated fuel use", f"{litres:.2f} L")
        c.metric("Illustrative emissions", f"{emissions:.2f} kg CO₂")
        st.caption("Calculation is based only on values entered above. It is not route optimization and does not use actual GPS or vehicle data.")
    st.markdown("**Data needed for real optimisation:** delivery addresses or coordinates, travel-time matrix, delivery windows, vehicle capacity, and order volumes.")

elif page == "7. ESG & Sustainability Reporting":
    hero("🌿 ESG & Sustainability Reporting", "Separate measured indicators from illustrative sustainability estimates")
    st.warning("The current dataset does not contain verified carbon factors, energy consumption, packaging materials, or waste mass. It cannot produce a verified carbon footprint or formal ESG report by itself.")
    if "unsold" in d:
        st.subheader("Available operational proxy")
        c1, c2 = st.columns(2)
        c1.metric("Average unsold-food index", f"{d['unsold'].mean():.2f}")
        c2.metric("Recent 28-day unsold index", f"{d.tail(min(28, len(d)))['unsold'].mean():.2f}")
        st.caption("Unsold-food index is an operational proxy only. It is not a measured quantity of waste and cannot be converted to CO₂ without additional verified data.")
    st.subheader("Data required for sustainability calculations")
    st.markdown("""
    - Waste quantity by weight and food category
    - Documented emissions factors and their sources
    - Energy and fuel consumption
    - Packaging type and material quantities
    - Reporting period, calculation method and data-quality notes
    """)
    st.info("Until those inputs are connected, label this page as a prototype reporting framework rather than verified ESG performance.")

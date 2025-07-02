import pandas as pd
import streamlit as st

st.set_page_config(page_title="Consolidated Holdings Report", layout="wide")
st.title("Consolidated Holdings Report")

uploaded_file = st.file_uploader("Upload Client Holdings Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.dropna(how='all', inplace=True)

    # Validate expected columns
    expected_cols = ['Asset Class', 'Asset Type', 'Ticker', 'Quantity', 'Amount', 'Currency']
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {missing_cols}")
        st.stop()

    # Separate invalid entries
    invalid_df = df[df['Currency'].isnull()]
    valid_df = df[df['Currency'].notnull()].copy()

    # Clean numeric values
    valid_df['Quantity'] = pd.to_numeric(valid_df['Quantity'], errors='coerce')
    valid_df['Amount'] = pd.to_numeric(valid_df['Amount'], errors='coerce')
    valid_df.dropna(subset=['Quantity', 'Amount'], inplace=True)


    st.sidebar.markdown("<h4><i style='color:#1a73e8;'>Filters</i></h4>", unsafe_allow_html=True)


    # 1. Multi-select Asset Class
    all_asset_classes = valid_df['Asset Class'].dropna().unique()
    selected_classes = st.sidebar.multiselect("Asset Class", sorted(all_asset_classes), default=list(all_asset_classes))

    # Filter Asset Types based on selected classes
    filtered_ac_df = valid_df[valid_df['Asset Class'].isin(selected_classes)]
    all_asset_types = filtered_ac_df['Asset Type'].dropna().unique()
    selected_types = st.sidebar.multiselect("Asset Type", sorted(all_asset_types), default=list(all_asset_types))

    # Filter Tickers based on selected types
    filtered_type_df = filtered_ac_df[filtered_ac_df['Asset Type'].isin(selected_types)]
    all_tickers = filtered_type_df['Ticker'].dropna().unique()
    selected_ticker = st.sidebar.selectbox("Ticker (Optional)", ['All'] + sorted(all_tickers.tolist()))

    # Apply all filters
    filtered_df = filtered_type_df.copy()
    if selected_ticker != 'All':
        filtered_df = filtered_df[filtered_df['Ticker'] == selected_ticker]

    # Sidebar summary
    st.sidebar.markdown("---")
    st.sidebar.markdown("<b><i style='color:#34a853;'>Current Selection:</i></b>", unsafe_allow_html=True)

    st.sidebar.markdown(f"- Asset Classes: `{', '.join(selected_classes)}`")
    st.sidebar.markdown(f"- Asset Types: `{', '.join(selected_types)}`")
    st.sidebar.markdown(f"- Ticker: `{selected_ticker}`")

    # Header
    st.markdown("<h3><i style='color:#188038;'>Grouped Holdings Report</i></h3>", unsafe_allow_html=True)

    for ac in filtered_df['Asset Class'].unique():
        ac_df = filtered_df[filtered_df['Asset Class'] == ac]
        ac_qty = ac_df['Quantity'].sum()
        ac_amt = ac_df['Amount'].sum()
        ac_entries = len(ac_df)

        st.markdown(f"""<div style='background-color:#f0f8ff;padding:10px;border-radius:6px'>
        <h4 style='margin-bottom:0'>
            <i style='color:#2a5d9f;font-style:normal;'>Asset Class:</i> <strong>{ac}</strong>
        </h4>
        <p style='margin:0'>Entries: <strong>{ac_entries}</strong> | Quantity: <strong>{ac_qty}</strong> | Amount: <strong>{ac_amt:,.2f}</strong></p>
        </div>""", unsafe_allow_html=True)

        for at in ac_df['Asset Type'].unique():
            at_df = ac_df[ac_df['Asset Type'] == at]
            at_qty = at_df['Quantity'].sum()
            at_amt = at_df['Amount'].sum()

            st.markdown(f"""<div style='margin-left:20px'>
            <h5 style='margin-bottom:0'>
                <i style='color:#6b4e9b;font-style:normal;'>Asset Type:</i> <strong>{at}</strong>
            </h5>
            <p style='margin:0'>Quantity: <strong>{at_qty}</strong> | Amount: <strong>{at_amt:,.2f}</strong></p>
            </div>""", unsafe_allow_html=True)

            for tk in at_df['Ticker'].unique():
                tk_df = at_df[at_df['Ticker'] == tk]
                tk_qty = tk_df['Quantity'].sum()
                tk_amt = tk_df['Amount'].sum()
                tk_entries = len(tk_df)

                st.markdown(f"""<div style='margin-left:40px'>
                <i style='color:#888;font-style:normal;'>Ticker:</i> <strong>{tk}</strong> —
                Entries: {tk_entries}, Quantity: {tk_qty}, Amount: {tk_amt:,.2f}
                </div>""", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

    # Display invalid rows
    if not invalid_df.empty:
        st.subheader("Entries with Missing Currency")
        st.dataframe(invalid_df, use_container_width=True)

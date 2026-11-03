
import streamlit as st
import pandas as pd

# ==========================================
# NEPAL SHARE TRANSACTION CALCULATOR
# ==========================================

st.set_page_config(
    page_title="NEPSE Share Calculator",
    page_icon="📈",
    layout="wide"
)

# ------------------------------------------
# TRANSACTION SETTINGS
# ------------------------------------------

SEBON_RATE = 0.00015
DP_CHARGE = 25

SHORT_TERM_CGT = 0.05
LONG_TERM_CGT = 0.0375


# ------------------------------------------
# BROKER COMMISSION
# ------------------------------------------

def broker_commission(amount):

    if amount <= 50000:
        rate = 0.0036

    elif amount <= 500000:
        rate = 0.0033

    elif amount <= 2000000:
        rate = 0.0031

    elif amount <= 10000000:
        rate = 0.0027

    else:
        rate = 0.0024

    return max(amount * rate, 10)


# ------------------------------------------
# PURCHASE CALCULATION
# ------------------------------------------

def calculate_purchase(quantity, price):

    transaction_amount = quantity * price

    commission = broker_commission(transaction_amount)

    sebon_fee = transaction_amount * SEBON_RATE

    total_expenses = commission + sebon_fee

    total_payable = transaction_amount + total_expenses

    average_cost = total_payable / quantity

    return {
        "Share Purchase Amount": transaction_amount,
        "Broker Commission": commission,
        "SEBON Fee": sebon_fee,
        "Total Expenses": total_expenses,
        "Total Payable": total_payable,
        "Effective Cost Per Share": average_cost
    }


# ------------------------------------------
# SALE CALCULATION
# ------------------------------------------

def calculate_sale(
    quantity,
    selling_price,
    purchase_price,
    holding_days,
    dp_charge=25
):

    # Purchase-side transaction costs
    purchase = calculate_purchase(
        quantity,
        purchase_price
    )

    acquisition_cost = purchase["Total Payable"]

    # Sale-side transaction amount
    transaction_amount = quantity * selling_price

    commission = broker_commission(transaction_amount)

    sebon_fee = transaction_amount * SEBON_RATE

    total_expenses = commission + sebon_fee + dp_charge

    # Capital gain after both purchase and sale costs
    capital_gain = (
        transaction_amount
        - total_expenses
        - acquisition_cost
    )

    # CGT for resident individual investors
    if capital_gain > 0:

        if holding_days <= 365:
            tax_rate = SHORT_TERM_CGT
        else:
            tax_rate = LONG_TERM_CGT

        cgt = capital_gain * tax_rate

    else:
        tax_rate = 0
        cgt = 0

    net_receivable = (
        transaction_amount
        - total_expenses
        - cgt
    )

    net_profit_loss = net_receivable - acquisition_cost

    return {
        "Sale Transaction Amount": transaction_amount,
        "Broker Commission": commission,
        "SEBON Fee": sebon_fee,
        "DP Charge": dp_charge,
        "Total Sale Expenses": total_expenses,
        "Purchase Cost Including Fees": acquisition_cost,
        "Capital Gain Before CGT": capital_gain,
        "CGT Rate": tax_rate * 100,
        "Capital Gains Tax": cgt,
        "Net Receivable": net_receivable,
        "Net Profit / Loss": net_profit_loss
    }


# ==========================================
# APPLICATION INTERFACE
# ==========================================

st.title("📈 NEPSE Share Transaction Calculator")

st.caption(
    "Calculate total share purchase costs and "
    "net sale proceeds in Nepal."
)

st.divider()

purchase_tab, sale_tab = st.tabs([
    "🟢 Share Purchase",
    "🔵 Share Sale"
])


# ==========================================
# PURCHASE TAB
# ==========================================

with purchase_tab:

    st.subheader("Share Purchase Calculator")

    col1, col2 = st.columns(2)

    with col1:

        buy_quantity = st.number_input(
            "Number of Shares",
            min_value=1,
            value=100,
            step=1
        )

    with col2:

        buy_price = st.number_input(
            "Purchase Price Per Share (Rs.)",
            min_value=0.01,
            value=500.0,
            step=1.0
        )

    if st.button(
        "Calculate Purchase",
        type="primary",
        use_container_width=True
    ):

        result = calculate_purchase(
            buy_quantity,
            buy_price
        )

        st.divider()

        st.subheader("Purchase Calculation Result")

        st.metric(
            "Total Amount Payable",
            f"Rs. {result['Total Payable']:,.2f}"
        )

        st.metric(
            "Effective Cost Per Share",
            f"Rs. {result['Effective Cost Per Share']:,.2f}"
        )

        purchase_details = pd.DataFrame({
            "Description": result.keys(),
            "Amount (Rs.)": [
                round(value, 2)
                for value in result.values()
            ]
        })

        st.dataframe(
            purchase_details,
            hide_index=True,
            use_container_width=True
        )


# ==========================================
# SALE TAB
# ==========================================

with sale_tab:

    st.subheader("Share Sale Calculator")

    col1, col2 = st.columns(2)

    with col1:

        sale_quantity = st.number_input(
            "Number of Shares",
            min_value=1,
            value=100,
            step=1,
            key="sale_quantity"
        )

        purchase_price = st.number_input(
            "Original Purchase Price Per Share (Rs.)",
            min_value=0.01,
            value=500.0,
            step=1.0
        )

    with col2:

        selling_price = st.number_input(
            "Selling Price Per Share (Rs.)",
            min_value=0.01,
            value=600.0,
            step=1.0
        )

        holding_days = st.number_input(
            "Holding Period (Days)",
            min_value=0,
            value=200,
            step=1
        )

    apply_dp = st.checkbox(
        "Include Rs. 25 DP charge",
        value=True
    )

    dp_amount = DP_CHARGE if apply_dp else 0

    if st.button(
        "Calculate Sale",
        type="primary",
        use_container_width=True
    ):

        result = calculate_sale(
            sale_quantity,
            selling_price,
            purchase_price,
            holding_days,
            dp_amount
        )

        st.divider()

        st.subheader("Sale Calculation Result")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Gross Sale Amount",
            f"Rs. {result['Sale Transaction Amount']:,.2f}"
        )

        col2.metric(
            "Net Receivable",
            f"Rs. {result['Net Receivable']:,.2f}"
        )

        col3.metric(
            "Net Profit / Loss",
            f"Rs. {result['Net Profit / Loss']:,.2f}",
            delta=f"{result['Net Profit / Loss']:,.2f}"
        )

        st.divider()

        st.subheader("Detailed Sale Breakdown")

        sale_details = pd.DataFrame({
            "Description": result.keys(),
            "Amount / Rate": [
                round(value, 2)
                for value in result.values()
            ]
        })

        st.dataframe(
            sale_details,
            hide_index=True,
            use_container_width=True
        )

        if result["Net Profit / Loss"] > 0:

            st.success(
                f"Your estimated net profit is "
                f"Rs. {result['Net Profit / Loss']:,.2f}"
            )

        elif result["Net Profit / Loss"] < 0:

            st.error(
                f"Your estimated net loss is "
                f"Rs. {abs(result['Net Profit / Loss']):,.2f}"
            )

        else:

            st.info("Your transaction is approximately at break-even.")


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "NEPSE Share Calculator | All amounts in NPR (Rs.)"
)

st.caption(
    "This calculator provides estimates. Actual charges, "
    "tax treatment and acquisition cost may differ according "
    "to applicable regulations and broker contract notes."
)

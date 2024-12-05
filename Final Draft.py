import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration for scrolling
st.set_page_config(layout="wide")

# Function Definitions
def calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years):
    monthly_rate = annual_interest_rate / 12 / 100
    num_payments = loan_term_years * 12
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    return monthly_payment

def generate_amortization_schedule(loan_amount, annual_interest_rate, loan_term_years):
    monthly_payment = calculate_monthly_payment(loan_amount, annual_interest_rate, loan_term_years)
    monthly_rate = annual_interest_rate / 12 / 100
    num_payments = loan_term_years * 12
    schedule = {
        "Payment Number": [],
        "Beginning Balance": [],
        "Monthly Payment": [],
        "Interest Paid": [],
        "Principal Paid": [],
        "Ending Balance": []
    }

    remaining_balance = loan_amount
    for payment_number in range(1, num_payments + 1):
        interest_paid = remaining_balance * monthly_rate
        principal_paid = monthly_payment - interest_paid
        ending_balance = remaining_balance - principal_paid

        schedule["Payment Number"].append(payment_number)
        schedule["Beginning Balance"].append(round(remaining_balance, 2))
        schedule["Monthly Payment"].append(round(monthly_payment, 2))
        schedule["Interest Paid"].append(round(interest_paid, 2))
        schedule["Principal Paid"].append(round(principal_paid, 2))
        schedule["Ending Balance"].append(round(ending_balance, 2))

        remaining_balance = ending_balance

    amortization_df = pd.DataFrame(schedule)
    total_payments = monthly_payment * num_payments
    total_interest = total_payments - loan_amount
    total_costs = {
        "Total Payments": round(total_payments, 2),
        "Total Interest Paid": round(total_interest, 2)
    }

    return amortization_df, total_costs

def generate_key_insights(amortization_data: pd.DataFrame, loan_amount: float):
    # Calculate total interest as a percentage of the loan amount
    total_interest_percentage = (amortization_data['Interest Paid'].sum() / loan_amount) * 100

    # Find the first payment where principal paid exceeds interest paid
    first_principal_exceeds_interest = amortization_data[
        amortization_data['Principal Paid'] > amortization_data['Interest Paid']
    ].iloc[0]['Payment Number']

    # Find the payment number where balance drops below 50% of the original loan amount
    balance_below_50 = amortization_data[amortization_data['Ending Balance'] < loan_amount * 0.5].iloc[0]['Payment Number']

    return total_interest_percentage, first_principal_exceeds_interest, balance_below_50

# Visualization Class
class LoanVisualizer:
    def plot_stacked_area_chart(self, amortization_data: pd.DataFrame) -> str:
        plt.figure(figsize=(12, 8))
        plt.stackplot(
            amortization_data['Payment Number'],
            amortization_data['Principal Paid'].cumsum(),
            amortization_data['Interest Paid'].cumsum(),
            labels=['Cumulative Principal Paid', 'Cumulative Interest Paid'],
            colors=['blue', 'orange'],
            alpha=0.7
        )
        plt.plot(
            amortization_data['Payment Number'],
            amortization_data['Ending Balance'],
            color='red',
            label='Remaining Balance',
            linewidth=2
        )
        plt.title("Amortization Schedule (Stacked Area)", fontsize=16)
        plt.xlabel("Payment Number", fontsize=14)
        plt.ylabel("Amount ($)", fontsize=14)
        plt.legend(fontsize=12)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        file_path = "stacked_area_chart.png"
        plt.savefig(file_path)
        plt.close()
        return file_path

# Streamlit Integration
st.title("Interest Rate Impact Analyzer")
st.write("Input your loan parameters below:")

loan_amount = st.number_input("Loan Amount ($)", min_value=0.0, step=1000.0)
interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, step=0.1, format="%.2f")
loan_term = st.number_input("Loan Term (years)", min_value=1, step=1)

if loan_amount > 0 and interest_rate > 0 and loan_term > 0:
    if st.button("Analyze"):
        # Calculations
        amortization_df, total_costs = generate_amortization_schedule(loan_amount, interest_rate, loan_term)
        # Visualizations
        visualizer = LoanVisualizer()
        stacked_area_chart = visualizer.plot_stacked_area_chart(amortization_df)

        # Display Results
        st.image(stacked_area_chart, caption="Amortization Schedule (Stacked Area)")
        st.write("Amortization Schedule")
        st.dataframe(amortization_df)

        # Display Total Borrowing Costs
        st.subheader("Total Borrowing Costs")
        st.metric("Total Payments", f"${total_costs['Total Payments']:,}")
        st.metric("Total Interest Paid", f"${total_costs['Total Interest Paid']:,}")

        # Generate and Display Key Insights
        st.subheader("Key Insights")
        total_interest_percentage, first_principal_exceeds_interest, balance_below_50 = generate_key_insights(amortization_df, loan_amount)

        # Key Insight 1
        st.write(f"💡 **Total Interest Paid as % of Loan Amount:** {total_interest_percentage:.2f}%")
        st.write(
            "- This tells you how much of the loan's total cost is made up of interest. A higher percentage indicates more interest paid over time."
        )

        # Key Insight 2
        st.write(f"💡 **Month When Principal Exceeds Interest Paid:** Month {int(first_principal_exceeds_interest)}")
        st.write(
            "- This marks the point where the borrower starts paying off more of the principal than the interest. It's an important milestone for paying off your debt faster."
        )

        # Key Insight 3
        st.write(f"💡 **Month When Balance Drops Below 50% of Loan Amount:** Month {int(balance_below_50)}")
        st.write(
            "- This shows when the remaining balance of the loan becomes less than half of the original loan amount. It's a key moment in the loan repayment process."
        )
else:
    st.error("All input values must be greater than zero.")



    
#streamlit run "Final Draft.py"

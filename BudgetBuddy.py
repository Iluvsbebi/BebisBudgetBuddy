import streamlit as st
import json
import os

DATA_FILE = 'budget_data.json'

def load_budget():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {'income': 0.0, 'expenses': {}}

def save_budget(budget_data):
    with open(DATA_FILE, 'w') as file:
        json.dump(budget_data, file, indent=4)

def main():
    st.title("Bebi Budget Buddy")
    
    # Load existing data
    budget_data = load_budget()
    
    # Initialize session state if not already set
    if 'income' not in st.session_state:
        st.session_state.income = budget_data.get('income', 0.0)
    if 'expenses' not in st.session_state:
        st.session_state.expenses = budget_data.get('expenses', {})

    st.header("Set Your Monthly Income")
    income_input = st.number_input("Monthly Income", value=st.session_state.income, step=100.0)
    st.session_state.income = income_input

    st.header("Expenses")
    with st.form("expense_form", clear_on_submit=True):
        expense_name = st.text_input("Expense Name")
        expense_amount = st.number_input("Expense Amount", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Add/Update Expense")
        if submitted:
            if expense_name:
                st.session_state.expenses[expense_name] = expense_amount
                st.success(f"Added/Updated expense: {expense_name} (${expense_amount:.2f})")
            else:
                st.error("Please enter an expense name.")

    st.subheader("Current Expenses")
    if st.session_state.expenses:
        for name, amount in st.session_state.expenses.items():
            st.write(f"{name}: ${amount:.2f}")
    else:
        st.write("No expenses added yet.")

    # Compute budget details
    total_expenses = sum(st.session_state.expenses.values())
    remaining = st.session_state.income - total_expenses

    st.header("Budget Summary")
    st.write(f"**Total Income:** ${st.session_state.income:.2f}")
    st.write(f"**Total Expenses:** ${total_expenses:.2f}")
    st.write(f"**Remaining Balance:** ${remaining:.2f}")

    if st.button("Save Budget Data"):
        # Save the current budget data
        data_to_save = {
            'income': st.session_state.income,
            'expenses': st.session_state.expenses
        }
        save_budget(data_to_save)
        st.success("Budget data saved successfully!")

if __name__ == '__main__':
    main()

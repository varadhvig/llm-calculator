import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Set Page Configuration
# -------------------------------

st.set_page_config(
    page_title="LLM Cost Calculator",
    page_icon="💰",
    layout="wide",  # Sets the layout to wide
    initial_sidebar_state="expanded",
    # Theme is set via config.toml or Streamlit Cloud settings
)

# -------------------------------
# Define Minimal LLM Pricing Data
# -------------------------------

def get_pricing_data():
    data = {
        "Provider": [
            "OpenAI", "Anthropic", "Meta (Llama 3)", "Google Gemini", "Bedrock"
        ],
        "Model": [
            "GPT-4 Turbo", "Claude 3 Opus", "Llama 3.1 405b", "Gemini 1.5 Flash", "Amazon Titan Text"
        ],
        "Context": [
            "128K/4K", "200K/4K", "128K/2K", "128K", "100K/4K"
        ],
        "Input/1k Tokens (USD)": [
            0.025, 0.0525, 0.0013, 0.0001, 0.1000  # Updated Bedrock pricing
        ],
        "Output/1k Tokens (USD)": [
            0.025, 0.0525, 0.0013, 0.0001, 0.1000  # Updated Bedrock pricing
        ],
        "Per Call (USD)": [
            0.025, 0.0525, 0.0013, 0.0001, 0.2000  # Assuming per call cost for Bedrock
        ],
        "Total (USD)": [
            2.50, 5.25, 0.13, 0.01, 20.00  # Updated total for Bedrock based on example
        ]
    }

    pricing_df = pd.DataFrame(data)
    return pricing_df

# -------------------------------
# Helper Functions
# -------------------------------

def convert_input_to_tokens(input_value, calculate_by):
    """
    Convert input value to tokens based on the 'Calculate By' option.

    Args:
        input_value (int): The user input value.
        calculate_by (str): The unit of the input ('Tokens', 'Words', 'Characters').

    Returns:
        int: The equivalent number of tokens.
    """
    if calculate_by == "Tokens":
        return input_value
    elif calculate_by == "Words":
        # Approximate: 1 word ≈ 1.3 tokens
        return int(input_value * 1.3)
    elif calculate_by == "Characters":
        # Approximate: 1 character ≈ 0.25 tokens
        return int(input_value * 0.25)
    else:
        return input_value  # Default to tokens if unknown option

def calculate_costs(input_tokens, output_tokens, api_calls, pricing_df):
    """
    Calculate the per call and total costs for each LLM model.

    Args:
        input_tokens (int): Number of input tokens.
        output_tokens (int): Number of output tokens.
        api_calls (int): Number of API calls.
        pricing_df (pd.DataFrame): DataFrame containing pricing data.

    Returns:
        pd.DataFrame: DataFrame with calculated costs.
    """
    df = pricing_df.copy()
    df["Per Call (USD)"] = (df["Input/1k Tokens (USD)"] * input_tokens / 1000) + \
                             (df["Output/1k Tokens (USD)"] * output_tokens / 1000)
    df["Total (USD)"] = df["Per Call (USD)"] * api_calls
    return df

def project_costs(pricing_df, months, growth_rate, initial_api_calls, input_tokens, output_tokens):
    """
    Project costs over a specified number of months with optional growth.

    Args:
        pricing_df (pd.DataFrame): DataFrame containing cost calculations.
        months (int): Number of months for projection.
        growth_rate (float): Monthly growth rate (e.g., 0.05 for 5%).
        initial_api_calls (int): Initial number of API calls.
        input_tokens (int): Number of input tokens.
        output_tokens (int): Number of output tokens.

    Returns:
        pd.DataFrame: Projection DataFrame with monthly and cumulative costs.
    """
    projection = []
    cumulative_cost = 0.0
    current_api_calls = initial_api_calls

    for month in range(1, months + 1):
        # Apply growth if any
        if growth_rate > 0 and month > 1:
            current_api_calls = int(current_api_calls * (1 + growth_rate))

        # Calculate cost for the current month
        cost_month = (pricing_df["Input/1k Tokens (USD)"] * input_tokens / 1000 + 
                      pricing_df["Output/1k Tokens (USD)"] * output_tokens / 1000) * current_api_calls

        # Sum the costs for all providers
        total_cost_month = cost_month.sum()

        # Update cumulative cost
        cumulative_cost += total_cost_month

        # Append to projection
        projection.append({
            "Month": month,
            "API Calls": current_api_calls,
            "Total Tokens": input_tokens + output_tokens,
            "Total Cost (USD)": total_cost_month,
            "Cumulative Cost (USD)": cumulative_cost
        })

    projection_df = pd.DataFrame(projection)
    return projection_df

# -------------------------------
# Streamlit App Layout
# -------------------------------

def main():
    # Set light theme using Streamlit configuration
    # Themes are typically set in config.toml or via Streamlit Cloud settings.
    # By default, Streamlit uses a light theme unless specified otherwise.

    st.title("LLM Cost Calculator - Enhanced Version 💰")
    
    # -------------------------------
    # Explanation of Tokens with Financial Example
    # -------------------------------
    
    st.markdown("""
    ### Understanding Tokens
    
    In the context of Large Language Models (LLMs), a **token** is a fundamental unit of text that the model processes. Tokens can be as short as one character or as long as one word. For example:
    
    - The word "**financial**" might be split into two tokens: "fin" and "ancial".
    - The sentence "**Data-driven insights**" could be tokenized into individual words: "Data", "-", "driven", "insights".
    
    **Financial Dataset Example:**
    
    Imagine you're analyzing a financial dataset containing annual reports of companies. Each report might consist of approximately 5,000 tokens. If your application processes 200 reports each month, that's 1,000,000 tokens. Understanding token usage is crucial for accurately estimating costs when utilizing LLMs for such tasks.
    
    This app helps you calculate the associated costs based on your usage.
    """)

    st.markdown("""
    This application calculates and projects the costs associated with various Large Language Models (LLMs) based on your input parameters. It now includes options for a wide layout, light theme, and specialized cost predictions for financial use cases.
    """)

    # User Inputs
    st.header("Input Parameters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        input_tokens = st.number_input("Input Tokens", min_value=0, value=1000, step=100)

    with col2:
        output_tokens = st.number_input("Output Tokens", min_value=0, value=500, step=50)

    with col3:
        api_calls = st.number_input("API Calls", min_value=0, value=100, step=10)

    with col4:
        calculate_by = st.selectbox(
            "Calculate By",
            ["Tokens", "Words", "Characters"]
        )

    # Use Case Selection
    st.header("Select Use Case")
    use_case = st.selectbox(
        "Choose your use case:",
        ["General", "Financial"]
    )

    # Adjust parameters based on use case
    if use_case == "Financial":
        st.subheader("Financial Use Case Parameters")
        financial_col1, financial_col2 = st.columns(2)

        with financial_col1:
            financial_growth_rate = st.slider(
                "Select Monthly Growth Rate (%)",
                min_value=0.0,
                max_value=50.0,
                value=10.0,
                step=1.0
            ) / 100.0  # Convert to decimal

        with financial_col2:
            projected_months = st.slider(
                "Select Number of Months for Projection",
                min_value=1,
                max_value=36,
                value=12,
                step=1
            )

    else:
        # Default projection parameters for general use case
        st.subheader("Projection Parameters")
        projection_col1, projection_col2 = st.columns(2)

        with projection_col1:
            growth_option = st.radio(
                "Apply Monthly Growth to API Calls?",
                ("No", "Yes")
            )

            if growth_option == "Yes":
                growth_rate = st.slider(
                    "Select Monthly Growth Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=5.0,
                    step=1.0
                ) / 100.0  # Convert to decimal
            else:
                growth_rate = 0.0  # No growth

        with projection_col2:
            months = st.slider(
                "Select Number of Months for Projection",
                min_value=1,
                max_value=24,
                value=12,
                step=1
            )

    # Convert Inputs if necessary
    if calculate_by != "Tokens":
        if calculate_by == "Words":
            # Convert words to tokens
            input_tokens_converted = convert_input_to_tokens(input_tokens, "Words")
            output_tokens_converted = convert_input_to_tokens(output_tokens, "Words")
            st.sidebar.info(f"Converted {input_tokens} Words to {input_tokens_converted} Tokens")
            st.sidebar.info(f"Converted {output_tokens} Words to {output_tokens_converted} Tokens")
            input_tokens = input_tokens_converted
            output_tokens = output_tokens_converted
        elif calculate_by == "Characters":
            # Convert characters to tokens
            input_tokens_converted = convert_input_to_tokens(input_tokens, "Characters")
            output_tokens_converted = convert_input_to_tokens(output_tokens, "Characters")
            st.sidebar.info(f"Converted {input_tokens} Characters to {input_tokens_converted} Tokens")
            st.sidebar.info(f"Converted {output_tokens} Characters to {output_tokens_converted} Tokens")
            input_tokens = input_tokens_converted
            output_tokens = output_tokens_converted

    # Fetch Pricing Data
    pricing_df = get_pricing_data()

    # Calculate Costs
    if st.button("Calculate"):
        if api_calls == 0:
            st.error("Number of API calls must be greater than 0.")
        else:
            cost_df = calculate_costs(input_tokens, output_tokens, api_calls, pricing_df)

            # Display Results
            st.header("Pricing Calculations")
            st.write("""
            The following pricing calculations are based on the input tokens, output tokens, and API calls you have entered above.
            """)
            st.dataframe(
                cost_df[["Provider", "Model", "Context", "Input/1k Tokens (USD)", 
                         "Output/1k Tokens (USD)", "Per Call (USD)", "Total (USD)"]]
                .style.format({
                    "Input/1k Tokens (USD)": "${:,.5f}",
                    "Output/1k Tokens (USD)": "${:,.5f}",
                    "Per Call (USD)": "${:,.4f}",
                    "Total (USD)": "${:,.2f}"
                })
            )

            # -------------------------------
            # Cost Over Time Visualization Enhancements
            # -------------------------------

            st.header("Cost Over Time")

            if use_case == "Financial":
                months = projected_months
                growth_rate = financial_growth_rate
            else:
                pass  # months and growth_rate are already set

            # Project Costs Over Time
            projection_df = project_costs(pricing_df, months, growth_rate, api_calls, input_tokens, output_tokens)

            # Display Projection Table
            st.subheader("Projection Table")
            st.dataframe(
                projection_df.style.format({
                    "API Calls": "{:,}",
                    "Total Tokens": "{:,}",
                    "Total Cost (USD)": "${:,.2f}",
                    "Cumulative Cost (USD)": "${:,.2f}"
                })
            )

            # Visualization: Monthly Cost and Cumulative Cost
            st.subheader("Projection Visualization")
            fig = px.line(
                projection_df, 
                x="Month", 
                y=["Total Cost (USD)", "Cumulative Cost (USD)"],
                labels={"value": "Cost ($)", "Month": "Month"},
                title="Monthly and Cumulative Cost Projection",
                markers=True
            )
            fig.update_layout(legend_title_text='Cost Type')
            st.plotly_chart(fig)

            # -------------------------------
            # Download Option
            # -------------------------------

            st.header("Download Cost Projection")
            csv = projection_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Projection as CSV",
                data=csv,
                file_name='llm_cost_projection.csv',
                mime='text/csv',
            )

            # -------------------------------
            # Optional: Display Raw Pricing Data
            # -------------------------------

            with st.expander("View Raw Pricing Data"):
                st.dataframe(cost_df)
            



            # Footer Section
st.markdown("""
    <style>
    footer {
        visibility: hidden;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #333333;
    }
    </style>
    <div class="footer">
        <p>Developed by Vignesh Varadharajan</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

import pandas as pd
import requests
import streamlit as st


def get_recent_observations(region_code):
    url = f"https://api.ebird.org/v2/data/obs/{region_code}/recent"
    headers = {"X-eBirdApiToken": st.secrets["ebird_api_key"]}
    response = requests.get(url, headers=headers)
    return response.json() if response.ok else None


if "observations" not in st.session_state:
    st.session_state["observations"] = None


def main():
    st.title("eBird Recent Observations App")
    st.write("Enter a region code to see recent bird observations in that area.")

    region_code = st.text_input("Region Code", "IN-MH-PU")

    if st.button("Fetch Observations"):
        observations = get_recent_observations(region_code)
        if observations is None:
            st.error("Failed to retrieve data or no recent observations available.")
        else:
            st.session_state.observations = observations

    if "observations" in st.session_state and st.session_state.observations:
        data = pd.DataFrame(st.session_state.observations)
        data.index = data.index + 1
        data = data[["comName", "obsDt", "locName"]]
        data.columns = ["Common Name", "Date Observed", "Location"]
        data["Date Observed"] = pd.to_datetime(data["Date Observed"]).dt.strftime(
            "%d %b %Y"
        )

        # Display the filter text box only after fetching the observations
        filter_query = st.text_input("Filter by bird name", "")

        if filter_query:
            # Filter data based on the user input
            filtered_data = data[
                data["Common Name"].str.contains(filter_query, case=False, na=False)
            ]
            if filtered_data.empty:
                st.write(f"No observations found for birds containing: {filter_query}")
            else:
                st.table(filtered_data)
        else:
            # Display the entire dataset if no filter is provided
            st.table(data)


if __name__ == "__main__":
    main()

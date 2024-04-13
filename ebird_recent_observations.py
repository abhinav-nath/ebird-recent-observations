import pandas as pd
import requests
import streamlit as st

API_KEY = st.secrets["ebird_api_key"]


def get_recent_observations(region_code):
    url = f"https://api.ebird.org/v2/data/obs/{region_code}/recent"
    headers = {"X-eBirdApiToken": API_KEY}
    response = requests.get(url, headers=headers)
    if response.ok:
        observations = response.json()
        if observations:
            return observations
        else:
            st.info(f"No recent observations found for region {region_code}.")
            return None
    else:
        st.error("Failed to retrieve data. Verify the region code and try again.")
        return None


def clear_observations():
    st.session_state.observations = None
    st.session_state.filter_query = ""


def set_region_code_and_fetch(code):
    st.session_state.region_code = code  # Set the region code in the session state
    st.session_state.filter_query = ""  # Reset the filter query
    st.session_state.observations = get_recent_observations(code)


if "observations" not in st.session_state:
    st.session_state["observations"] = None


def main():
    st.title("eBird Recent Observations App")

    if "region_code" not in st.session_state:
        st.session_state["region_code"] = "IN-MH-PU"

    with st.expander("View Region Codes"):
        region_codes = {
            "IN-MH-PU": "Pune Overall",
            "L3112807": "Saswad",
            "L2804745": "Sinhagad Valley",
            "L2717671": "Pabe Ghat",
            "L1866806": "Kavdi Pat",
            "L2639081": "ARAI Hills",
            "L1944566": "Pashan Lake",
            "L3326636": "Manas Lake",
            "L3287700": "Mulshi",
            "L4025539": "Kanifnath",
            "L3122641": "Baner Hill",
            "L3017706": "Mayureshwar WLS",
            "L2814614": "Bhigwan",
            "L3916644": "Waghapur",
            "L3678933": "Tamhini Forest",
            "IN-GA": "Goa",
        }

        columns_per_row = 4
        cols = st.columns(columns_per_row)

        for index, (code, location) in enumerate(region_codes.items()):
            with cols[index % columns_per_row]:
                st.button(
                    f"{location}", on_click=set_region_code_and_fetch, args=(code,)
                )

    region_code = st.text_input(
        "Enter a region code (in uppercase) to see recent bird observations in that area.",
        st.session_state.region_code,
    )

    col1, spacer, col2 = st.columns([3, 5.8, 1])
    with col1:
        if st.button("Fetch Observations"):
            set_region_code_and_fetch(region_code)

    if "observations" in st.session_state and st.session_state.observations:
        with col2:
            if st.button("Clear", key="clear_button"):
                clear_observations()
                return

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

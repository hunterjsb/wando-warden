import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd
import altair as alt
from boto3.dynamodb.conditions import Attr

from warden.terminal import load_terminals
from warden.detection import detect_trucks
from warden.config import get_photo_memory, get_db_memory


def main():
    st.title("Warden Camera Management")

    # Sidebar for configuration
    st.sidebar.header("Configuration")
    terminals_file = st.sidebar.text_input("Terminals YAML file", value="./terminals.yaml")
    storage_type = st.sidebar.selectbox("Storage Type", ["local", "s3"], index=1)
    db_type = st.sidebar.selectbox("Database Type", ["sqlite", "mysql", "postgres", "dynamodb"], index=3)
    detect_trucks_option = st.sidebar.checkbox("Detect Trucks", value=True)

    # Load terminals
    try:
        photo_mem = get_photo_memory(storage_type)
        db_mem = get_db_memory(db_type)
        terminals = load_terminals(terminals_file, photo_mem)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return

    # Main content
    for terminal in terminals:
        st.header(f"Terminal: {terminal.name}")
        for camera in terminal.cameras:
            st.subheader(f"Camera: {camera.name}")

            if st.button(f"Process {camera.full_name}"):
                try:
                    camera.get()
                    camera.save_last(with_timestamp=True)
                    st.success(f"Processed CAMERA: {camera.full_name}_{camera.last_timestamp}")

                    if detect_trucks_option:
                        truck_count, avg_confidence = detect_trucks(camera.last_image_name,
                                                                    os.environ.get('S3_BUCKET_NAME', 'wando-warden'))
                        st.info(f"Detected {truck_count} trucks with average confidence {avg_confidence:.2f}")
                        db_mem.save((truck_count, avg_confidence), f"{camera.full_name}|{camera.last_timestamp}")

                except Exception as e:
                    st.error(f"Error processing camera {camera.full_name}: {str(e)}")

    # Data Viewer and Visualization
    st.header("View Stored Data and Visualization")
    view_data = st.checkbox("View stored truck detection data")
    if view_data:
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
        end_date = st.date_input("End Date", datetime.now().date())

        results = query_db(db_mem, start_date, end_date)

        if results:
            # Display data table
            st.subheader("Data Table")
            st.table(results)

            # Create visualization
            st.subheader("Truck Count Visualization")
            df = pd.DataFrame(results)
            df['timestamp'] = df['timestamp'].apply(parse_flexible_timestamp)

            # Convert Decimal to float
            df['avg_confidence'] = df['avg_confidence'].apply(lambda x: float(x))

            chart = alt.Chart(df).mark_line().encode(
                x='timestamp:T',
                y='truck_count:Q',
                color='camera_name:N',
                tooltip=['camera_name', 'timestamp', 'truck_count', 'avg_confidence:Q']
            ).properties(
                width=700,
                height=400,
                title="Truck Count Over Time"
            ).interactive()

            st.altair_chart(chart)
        else:
            st.info("No data available for the selected date range.")


def parse_flexible_timestamp(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d_%H:%M:%S")
    except ValueError:
        return datetime.strptime(ts_str.replace("_approx", ""), "%Y-%m-%d_%H:%M:%S")


def query_db(db_mem, start_date, end_date):
    start_timestamp = start_date.strftime("%Y-%m-%d_00:00:00")
    end_timestamp = end_date.strftime("%Y-%m-%d_23:59:59")

    response = db_mem.table.scan(
        FilterExpression=Attr('timestamp').between(start_timestamp, end_timestamp)
    )

    items = response['Items']

    # Paginate through the results if there are more
    while 'LastEvaluatedKey' in response:
        response = db_mem.table.scan(
            FilterExpression=Attr('timestamp').between(start_timestamp, end_timestamp),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response['Items'])

    return items


if __name__ == "__main__":
    main()

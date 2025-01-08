import streamlit as st
from PIL import Image
import os
import time
import plotly.express as px
import pandas as pd
import random
import json

session_key = "real_time_data"


def read_input_source_data():
    # read json data from a file

    json_file_path = "/home/wut/playground/streamlit-viz-test/src/data.json"
    with open(json_file_path, "r") as f:
        data = json.load(f)
    # transform json data to dataframe
    data = pd.DataFrame(data)
    return data


if "source_data" not in st.session_state:
    st.session_state.source_data = read_input_source_data()

# Set Streamlit page configuration for wide layout
st.set_page_config(
    page_title="Real-Time Timelapse Viewer",
    layout="wide",  # Use wide layout for full-width display
)

if session_key not in st.session_state:
    st.session_state[session_key] = pd.DataFrame(columns=["Time", "Cell Type", "Value"])

if "image_and_time_info" not in st.session_state:
    st.session_state.image_and_time_info = []


# Function to simulate real-time data
def generate_real_time_data(existing_data, file_name, existing_image_and_time_info):

    new_data_test = st.session_state.source_data[
        st.session_state.source_data["image_name"] == file_name
    ]
    #  2024-05-29 11:48:20.963000
    new_time_stamp = (
        new_data_test["date"].values[0] + " " + new_data_test["time"].values[0]
    )
    # transform to timestamp
    new_time_stamp = pd.to_datetime(new_time_stamp)

    new_data_test_dict = {
        "Time": [new_time_stamp] * 4,  # Repeat the timestamp for each metric
        "Cell Type": ["RGB_011", "RGB_101", "RGB_100", "RGB_001"],
        "Value": [
            new_data_test["RGB_100"].values[0],
            new_data_test["RGB_101"].values[0],
            new_data_test["RGB_011"].values[0],
            new_data_test["RGB_001"].values[0],
        ],
    }
    new_df_test = pd.DataFrame(new_data_test_dict)
    updated_data = pd.concat(
        [existing_data, new_df_test]
    )  # Keep only the latest 150 rows
    existing_image_and_time_info.append((file_name, new_time_stamp))
    st.session_state[session_key] = updated_data
    st.session_state.image_and_time_info = existing_image_and_time_info
    return updated_data


# define function to get all the name of the folders in the path and check if there any items in the folder
def get_all_folders(path):
    folders = [
        name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))
    ]
    return folders


def clear_data():
    st.session_state[session_key] = pd.DataFrame(columns=["Time", "Cell Type", "Value"])
    st.session_state.image_and_time_info = []
    st.session_state.play_timelapse_active = False
    st.session_state.current_frame_idx = 0


def set_play_timelapse_button_inactive():
    st.session_state.play_timelapse_active = False
    st.session_state.current_frame_idx = 0


# Streamlit app
st.title("Cell Counting Timelapse Viewer with Interactive Line Chart")

# Folder selection
folder_path = "/data/biolab_arralyze_picture_data/"

# Layout: Side-by-Side Columns
col1, col2 = st.columns([1, 2])  # Adjust the width ratio as needed

# Initialize session state variables
if "real_time_data" not in st.session_state:
    st.session_state.real_time_data = pd.DataFrame(columns=["Time", "Cell Type", "Value"])
if "play_timelapse_active" not in st.session_state:
    st.session_state.play_timelapse_active = False
if "current_frame_idx" not in st.session_state:
    st.session_state.current_frame_idx = 0  # Start from the first frame

# Column 1: Image Viewer
with col1:
    if os.path.exists(folder_path):
        experiment_list = ["20240529 K562-NK cells purified_Killing Assay (9b33)", ""]
        # Add a dropdown to select the folder with the default value as the first folder
        experiment_selected = st.selectbox(
            "Select an Experiment", experiment_list, index=0
        )
        # Get all the folders in the path
        experiment_folder_path = os.path.join(
            folder_path, experiment_selected, "v3", "Run 1", "Images"
        )
        folders = get_all_folders(experiment_folder_path)
        with col2:
            # Add a dropdown to select the folder with the default value as the first folder
            folder_selected = st.selectbox("Select a Well", folders, index=0)
            if folder_selected not in st.session_state:
                st.session_state[folder_selected] = pd.DataFrame(columns=["Time", "Cell Type", "Value"])

        selected_folder_path = os.path.join(
            experiment_folder_path, folder_selected, "Merged"
        )
        # Load images
        images = []
        for file_name in sorted(os.listdir(selected_folder_path)):
            if file_name.endswith((".png", ".jpg", ".jpeg")):
                file_path = os.path.join(selected_folder_path, file_name)
                images.append((file_name, Image.open(file_path)))

        if images:
            # # Side-by-side buttons
            button_col1, button_col2, button_col3 = st.columns(3)
            with button_col1:
                play_timelapse = st.button("Play Timelapse")
            with button_col2:
                resume_timelapse = st.button("Resume Timelapse")
            with button_col3:
                stop_timelapse = st.button("Stop Timelapse")

            frame_idx = st.slider(
                "Select Frame",
                min_value=0,
                max_value=len(images) - 1,
                value=st.session_state.current_frame_idx,
                key="frame_slider",
            )

            # Update session state when slider changes
            if not st.session_state.play_timelapse_active:
                st.session_state.current_frame_idx = frame_idx
        else:
            st.warning("No images found in the specified folder.")
    else:
        st.error("The specified folder path does not exist. Please enter a valid path.")


# Column 2: Real-Time Line Chart
with col2:
    st.subheader("Cell Counting Result ")
    chart_placeholder = st.empty()  # Placeholder for the chart

    # Handle button interactions
    if play_timelapse:
        st.session_state.play_timelapse_active = True
        st.session_state.current_frame_idx = 0
        # with button_col1:
        #     st.write("Timelapse started. To stop, click 'Stop Timelapse'.")
    if stop_timelapse:
        st.session_state.play_timelapse_active = False
        # with button_col3:
        #     st.write("Timelapse stopped. To resume, click 'Resume Timelapse'.")
    if resume_timelapse:
        st.session_state.play_timelapse_active = True
        # with button_col2:
        #     st.write("Timelapse resumed. To stop, click 'Stop Timelapse'.")

    if st.session_state.play_timelapse_active:
        # Create placeholders for the image and chart
        image_placeholder = col1.empty()

        # Start timelapse and update graph
        for idx in range(st.session_state.current_frame_idx, len(images)):
            st.session_state.current_frame_idx = idx  # Save the current frame index

            # Check if playback is stopped
            if not st.session_state.play_timelapse_active:
                break

            # Update image in the placeholder
            file_name, img = images[idx]
            image_placeholder.image(
                img, caption=f"Frame: {file_name}", use_container_width=True
            )

            # Update real-time data
            st.session_state[folder_selected] = generate_real_time_data(
                st.session_state[folder_selected],
                file_name,
                st.session_state.image_and_time_info,
            )

            # Update chart with new data
            fig = px.line(
                st.session_state[folder_selected],
                x="Time",
                y="Value",
                color="Cell Type",
                title="Cell Counting Result Over Time",
            )

            # Update layout
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Values",
                legend_title="Cell Type",
                showlegend=True,
            )

            # Display the chart in the placeholder
            chart_placeholder.plotly_chart(fig, use_container_width=True)

            # Pause for real-time effect
            time.sleep(0.5)
        st.session_state.play_timelapse_active = False
    else:
        # Display the image based on the slider value
        image_placeholder = col1.empty()
        file_name, img = images[frame_idx]
        image_placeholder.image(
            img, caption=f"Frame: {file_name}", use_container_width=True
        )
        # filer time info with image name
        image_and_time_info_filtered = [
            item
            for item in st.session_state.image_and_time_info
            if item[0] == images[frame_idx][0]
        ]

        if image_and_time_info_filtered:
            time_stamp = image_and_time_info_filtered[-1][1]
        else:
            time_stamp = "00:00:00"

        filtered_data = st.session_state[folder_selected][
            st.session_state[folder_selected]["Time"] <= time_stamp
        ]

        # Display the filtered chart
        fig = px.line(
            filtered_data,
            x="Time",
            y="Value",
            color="Cell Type",
        )

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Values",
            legend_title="Cell Type",
            showlegend=True,
        )

        chart_placeholder.plotly_chart(fig, use_container_width=True)

    # Button to clear data
    st.button("Clear Data", on_click=clear_data)

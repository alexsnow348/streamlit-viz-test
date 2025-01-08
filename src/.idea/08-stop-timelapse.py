import streamlit as st
from PIL import Image
import os
import time
import plotly.express as px
import pandas as pd
import random
import json


session_key='real_time_data'

# Set Streamlit page configuration for wide layout
st.set_page_config(
    page_title="Real-Time Timelapse Viewer",
    layout="wide",  # Use wide layout for full-width display
)

if session_key not in st.session_state:
    st.session_state[session_key] = pd.DataFrame(columns=["Time", "Metric", "Value"])

def read_input_source_data():
    # read json data from a file
   
    json_file_path = "/home/wut/playground/streamlit-viz-test/src/data.json"
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    # transform json data to dataframe
    data = pd.DataFrame(data)
    return data

if "source_data" not in st.session_state:
    st.session_state.source_data = read_input_source_data()

# Function to simulate real-time data
def generate_real_time_data(existing_data, file_name):
    # Add a new timestamp and random values for metrics
    # new_time = pd.Timestamp.now().strftime("%H:%M:%S")
    # new_data = {
    #     "Time": [new_time] * 3,  # Repeat the timestamp for each metric
    #     "Metric": ["Metric 1", "Metric 2", "Metric 3"],
    #     "Value": [random.randint(10, 50), random.randint(5, 40), random.randint(2, 30)],
    # }
    # file the data with file name from the source data
    new_data = st.session_state.source_data[st.session_state.source_data["image_name"] == file_name]
    print(new_data.head())
    new_df = pd.DataFrame(new_data)
    updated_data = pd.concat([existing_data, new_df])  # Keep only the latest 150 rows
    st.session_state[session_key] = updated_data
    return updated_data

# define function to get all the name of the folders in the path and check if there any items in the folder
def get_all_folders(path):
    folders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    return folders

def clear_data():
   st.session_state[session_key]  = pd.DataFrame(columns=["Time", "Metric", "Value"])
 
def set_play_timelapse_button_inactive():
    st.session_state.play_timelapse_active = False
    st.session_state.current_frame_idx = 0

# Streamlit app
st.title("Real-Time Timelapse Viewer with Interactive Line Chart")

# Folder selection
folder_path = "/data/biolab_arralyze_picture_data/20240529 K562-NK cells purified_Killing Assay (9b33)/v3/Run 1/Images/"


# Layout: Side-by-Side Columns
col1, col2 = st.columns([1, 2])  # Adjust the width ratio as needed

# Initialize session state variables
if "real_time_data" not in st.session_state:
    st.session_state.real_time_data = pd.DataFrame(columns=["Time", "Metric", "Value"])
if "play_timelapse_active" not in st.session_state:
    st.session_state.play_timelapse_active = False
if "current_frame_idx" not in st.session_state:
    st.session_state.current_frame_idx = 0  # Start from the first frame


# Column 1: Image Viewer
with col1:
    if os.path.exists(folder_path):
        # get all the folders in the path
        folders = get_all_folders(folder_path)
        # add a dropdown to select the folder with the default value as the first folder
        folder_selected = st.selectbox("Select a Well", folders, index=0)
        folder_path = os.path.join(folder_path, folder_selected, "Merged")
        # Load images
        images = []
        for file_name in sorted(os.listdir(folder_path)):
            if file_name.endswith((".png", ".jpg", ".jpeg")):
                file_path = os.path.join(folder_path, file_name)
                images.append((file_name, Image.open(file_path)))

        if images:
            # Side-by-side buttons
            button_col1, _, _ = st.columns(3)
            with button_col1:
                play_timelapse = st.button("Play Timelapse")
                st.write(f"Selected well have {len(images)} frames.")
            
        
        else:
            st.warning("No images found in the specified folder.")
    else:
        st.error("The specified folder path does not exist. Please enter a valid path.")

# Column 2: Real-Time Line Chart
with col2:
    st.subheader("Real-Time Line Chart")
    chart_placeholder = st.empty()  # Placeholder for the chart
    if play_timelapse:
        st.session_state.play_timelapse_active = True
        st.session_state.current_frame_idx = 0
  
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
            image_placeholder.image(img, caption=f"Frame: {file_name}", use_container_width=True)
        
            # Update real-time data
            st.session_state.real_time_data = generate_real_time_data(st.session_state.real_time_data)

            # Update chart with new data
            fig = px.line(
                st.session_state.real_time_data,
                x="Time",
                y="Value",
                color="Metric",
                title="Real-Time Metrics"
            )

            # Update layout
            fig.update_layout(
                xaxis_title="Time",
                yaxis_title="Values",
                legend_title="Metrics",
                showlegend=True,
            )

            # Display the chart in the placeholder
            chart_placeholder.plotly_chart(fig, use_container_width=True)

            # Pause for real-time effect
            time.sleep(0.5)
        st.session_state.play_timelapse_active = True
    else:
        image_placeholder = col1.empty()
        file_name, img = images[st.session_state.current_frame_idx]
        image_placeholder.image(img, caption=f"Frame: {file_name}", use_container_width=True)
        # Display the last state of the chart
        fig = px.line(
            st.session_state.real_time_data,
            x="Time",
            y="Value",
            color="Metric",
            title="Real-Time Metrics"
        )

        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Values",
            legend_title="Metrics",
            showlegend=True,
        )

        chart_placeholder.plotly_chart(fig, use_container_width=True)

    st.button("Clear Data", on_click=clear_data)
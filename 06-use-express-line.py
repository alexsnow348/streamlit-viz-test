import streamlit as st
from PIL import Image
import os
import time
import plotly.express as px
import pandas as pd
import random  # For generating real-time data

# Set Streamlit page configuration for wide layout
st.set_page_config(
    page_title="Real-Time Timelapse Viewer",
    layout="wide",  # Use wide layout for full-width display
)

# Function to simulate real-time data

def generate_real_time_data(existing_data):
    # Add a new timestamp and random values for metrics
    new_time = pd.Timestamp.now().strftime("%H:%M:%S")
    new_data = {
        "Time": [new_time] * 3,  # Repeat the timestamp for each metric
        "Metric": ["Metric 1", "Metric 2", "Metric 3"],
        "Value": [random.randint(10, 50), random.randint(5, 40), random.randint(2, 30)],
    }
    new_df = pd.DataFrame(new_data)
    updated_data = pd.concat([existing_data, new_df]).tail(150)  # Keep only the latest 150 rows
    return updated_data

# Streamlit app
st.title("Real-Time Timelapse Viewer with Interactive Line Chart")

# Folder selection
folder_path = st.text_input("Enter the folder path containing timelapse images:", "/data/biolab_arralyze_picture_data/20240529 K562-NK cells purified_Killing Assay (9b33)/v3/Run 1/Images/A1_A15_ID-0/Merged")

# Layout: Side-by-Side Columns
col1, col2 = st.columns([1, 2])  # Adjust the width ratio as needed

# Column 1: Image Viewer
with col1:
    if os.path.exists(folder_path):
        # Load images
        images = []
        for file_name in sorted(os.listdir(folder_path)):
            if file_name.endswith((".png", ".jpg", ".jpeg")):
                file_path = os.path.join(folder_path, file_name)
                images.append((file_name, Image.open(file_path)))

        if images:
            # Image slider
            # frame_idx = st.slider("Select Frame", 0, len(images) - 1, 0)
            # file_name, img = images[frame_idx]

            # # Display the selected image
            # st.image(img, caption=f"Frame: {file_name}", use_container_width=True)

            # Play timelapse button
            play_timelapse = st.button("Play Timelapse")
        else:
            st.warning("No images found in the specified folder.")
    else:
        st.error("The specified folder path does not exist. Please enter a valid path.")

# Column 2: Real-Time Line Chart
with col2:
    st.subheader("Real-Time Line Chart")

    # Initialize data
    if "real_time_data" not in st.session_state:
        st.session_state.real_time_data = pd.DataFrame(columns=["Time", "Metric", "Value"])

    # Display the graph only during playback
    if "play_timelapse_active" not in st.session_state:
        st.session_state.play_timelapse_active = False

    if play_timelapse:
        st.session_state.real_time_data = pd.DataFrame(columns=["Time", "Metric", "Value"])
        st.session_state.play_timelapse_active = True

    if st.session_state.play_timelapse_active:
        # Create placeholders for the image and chart
        image_placeholder = col1.empty()
        chart_placeholder = col2.empty()

        # Start timelapse and update graph
        for idx, (file_name, img) in enumerate(images):
            # Update image in the same position
            image_placeholder.image(img, caption=f"Frame: {file_name}", use_container_width=True)

            # Update real-time data
            st.session_state.real_time_data = generate_real_time_data(st.session_state.real_time_data)

            # Create Plotly Express line chart
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

            # Display the chart
            chart_placeholder.plotly_chart(fig, use_container_width=True)

            # Pause for real-time effect
            time.sleep(0.5)

        # Reset the play_timelapse_active state after playback
        st.session_state.play_timelapse_active = False

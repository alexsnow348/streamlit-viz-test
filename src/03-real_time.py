import streamlit as st
from PIL import Image
import os
import time
import plotly.graph_objects as go
import pandas as pd
import random  # For generating real-time data

# Function to simulate real-time data
def generate_real_time_data(existing_data):
    # Add a new timestamp and random values for metrics
    new_time = pd.Timestamp.now().strftime("%H:%M:%S")
    new_data = {
        "Time": [new_time],
        "Metric 1": [random.randint(10, 50)],
        "Metric 2": [random.randint(5, 40)],
        "Metric 3": [random.randint(2, 30)],
    }
    new_df = pd.DataFrame(new_data)
    updated_data = pd.concat([existing_data, new_df]).tail(50)  # Keep only the latest 50 rows
    return updated_data

# Streamlit app
st.title("Real-Time Timelapse Viewer with Interactive Stacked Line Chart")

# Folder selection
folder_path = st.text_input("Enter the folder path containing timelapse images:", "/data/biolab_arralyze_picture_data/20240529 K562-NK cells purified_Killing Assay (9b33)/v3/Run 1/Images/A1_A15_ID-0/Merged")


if os.path.exists(folder_path):
    # Load images
    images = []
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith((".png", ".jpg", ".jpeg")):
            file_path = os.path.join(folder_path, file_name)
            images.append((file_name, Image.open(file_path)))

    if images:
        # Image slider
        frame_idx = st.slider("Select Frame", 0, len(images) - 1, 0)
        file_name, img = images[frame_idx]

        # Display the selected image
        st.image(img, caption=f"Frame: {file_name}", use_container_width=True)

        # Play timelapse
        if st.button("Play Timelapse"):
            placeholder = st.empty()  # Create a placeholder for the image
            for idx, (file_name, img) in enumerate(images):
                placeholder.image(img, caption=f"Frame: {file_name}", use_container_width=True)
                time.sleep(0.2)  # Adjust delay for timelapse speed
    else:
        st.warning("No images found in the specified folder.")
else:
    st.error("The specified folder path does not exist. Please enter a valid path.")

# Generate real-time data
st.subheader("Real-Time Stacked Line Chart")

# Initialize data
if "real_time_data" not in st.session_state:
    st.session_state.real_time_data = pd.DataFrame(columns=["Time", "Metric 1", "Metric 2", "Metric 3"])

# Dropdown for filtering data
dropdown_options = ["All Metrics", "Metric 1", "Metric 2", "Metric 3"]
selected_option = st.selectbox("Select Metric to Display", dropdown_options)

# Real-time chart update
placeholder_chart = st.empty()

while True:
    # Update data
    st.session_state.real_time_data = generate_real_time_data(st.session_state.real_time_data)

    # Filter data based on dropdown selection
    if selected_option == "All Metrics":
        metrics_to_display = ["Metric 1", "Metric 2", "Metric 3"]
    else:
        metrics_to_display = [selected_option]

    # Create Plotly stacked line chart
    fig = go.Figure()

    for metric in metrics_to_display:
        fig.add_trace(go.Scatter(
            x=st.session_state.real_time_data["Time"],
            y=st.session_state.real_time_data[metric],
            name=metric,
            stackgroup="one",  # Define stack group
            mode="lines"
        ))

    # Update layout
    fig.update_layout(
        title="Real-Time Metrics",
        xaxis_title="Time",
        yaxis_title="Values",
        showlegend=True
    )

    # Display the chart
    placeholder_chart.plotly_chart(fig, use_container_width=True)

    # Pause for real-time effect
    time.sleep(1)

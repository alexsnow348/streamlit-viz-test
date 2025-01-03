import streamlit as st
from PIL import Image
import os
import time
import plotly.graph_objects as go
import pandas as pd

# Function to load images from a folder
def load_images(folder_path):
    images = []
    for file_name in sorted(os.listdir(folder_path)):
        if file_name.endswith((".png", ".jpg", ".jpeg")):
            file_path = os.path.join(folder_path, file_name)
            images.append((file_name, Image.open(file_path)))
    return images

# Function to generate sample data for the stacked line chart
def generate_sample_data():
    data = {
        "Time": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"],
        "Metric 1": [10, 20, 30, 40],
        "Metric 2": [5, 15, 25, 35],
        "Metric 3": [2, 12, 22, 32],
    }
    return pd.DataFrame(data)

# Streamlit app
st.title("Timelapse Image Viewer with Stacked Line Chart")

# Folder selection
folder_path = st.text_input("Enter the folder path containing timelapse images:", "/data/biolab_arralyze_picture_data/20240529 K562-NK cells purified_Killing Assay (9b33)/v3/Run 1/Images/A1_A15_ID-0/Merged")


if os.path.exists(folder_path):
    # Load images
    images = load_images(folder_path)
    
    # Dropdown for filtering data
    dropdown_options = ["All Metrics", "Metric 1", "Metric 2", "Metric 3"]
    selected_option = st.selectbox("Select Metric to Display", dropdown_options)
    # Filter data based on dropdown selection
    if selected_option == "All Metrics":
        metrics_to_display = ["Metric 1", "Metric 2", "Metric 3"]
    else:
        metrics_to_display = [selected_option]
 
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

# Generate and display the stacked line chart
st.subheader("Stacked Line Chart")

# Dropdown for filtering data
dropdown_options = ["All Metrics", "Metric 1", "Metric 2", "Metric 3"]
selected_option = st.selectbox("Select Metric to Display", dropdown_options)

# Load data
df = generate_sample_data()

# Filter data based on dropdown selection
if selected_option == "All Metrics":
    metrics_to_display = ["Metric 1", "Metric 2", "Metric 3"]
else:
    metrics_to_display = [selected_option]

# Create Plotly stacked line chart
fig = go.Figure()

for metric in metrics_to_display:
    fig.add_trace(go.Scatter(
        x=df["Time"],
        y=df[metric],
        name=metric,
        stackgroup="one",  # Define stack group
        mode="lines"
    ))

# Update layout
fig.update_layout(
    title="Metrics Over Time",
    xaxis_title="Time",
    yaxis_title="Values",
    showlegend=True
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)

import streamlit as st
from PIL import Image
import os
import time
import plotly.express as px
import pandas as pd
import cv2

# local import
from data import (
    generate_real_time_data,
    get_all_folders,
    get_source_data_based_on_transaction_id,
    get_unique_details,
    get_experiment_list,
)
from action import clear_data, draw_detection

# load the .env file
from dotenv import load_dotenv

load_dotenv()

# Get the folder path from the environment variable
IMAGE_FOLDER_PATH = os.getenv("IMAGE_FOLDER_PATH")
IMAGE_MERGE_FOLDER = os.getenv("IMAGE_MERGE_FOLDER")


def setup_initial_session_state():
    # Set Streamlit page configuration for wide layout
    st.set_page_config(
        page_title="Machine Learning  Dashboard",
        layout="wide",  # Use wide layout for full-width display
    )
    # Streamlit app
    st.title("Cell Counting Image Viewer")

    session_key = "real_time_data"

    # Initialize session state variables
    if session_key not in st.session_state:
        st.session_state[session_key] = {}

    if "play_timelapse_active" not in st.session_state:
        st.session_state.play_timelapse_active = False
    if "current_frame_idx" not in st.session_state:
        st.session_state.current_frame_idx = 0  # Start from the first frame

    # Layout: Side-by-Side Columns
    col1, col2 = st.columns([1, 2])  # Adjust the width ratio as needed

    return session_key, col1, col2, st.session_state


def is_check_folder_path_existed(folder_path):
    if os.path.exists(folder_path):
        return True
    else:
        return False


def setup_buttons():
    # Side-by-side buttons
    button_col1, button_col2, button_col3 = st.columns(3)
    with button_col1:
        play_timelapse = st.button("Play Timelapse")
    with button_col2:
        resume_timelapse = st.button("Resume Timelapse")
    with button_col3:
        stop_timelapse = st.button("Stop Timelapse")
    return play_timelapse, resume_timelapse, stop_timelapse


def setup_select_boxes(col2, session_key):
    experiment_info = get_experiment_list()
    experiment_list = [experiment["experiment_name"] for experiment in experiment_info]
    experiment_selected = st.selectbox("Select an Experiment", experiment_list, index=0)
    # query the transaction_id from experiment_list when the experiment_selected is selected
    transaction_id = [
        experiment["transaction_id"]
        for experiment in experiment_info
        if experiment["experiment_name"] == experiment_selected
    ][0]
    unique_details = get_unique_details(transaction_id)
    if unique_details:
        unique_run_version = unique_details["run_version"]
        unique_run_name = unique_details["run_name"]
        unique_class_name = unique_details["result_class_name"]
        run_version_selected = st.selectbox(
            "Select a Run Version",
            unique_run_version,
            index=len(unique_run_version) - 1,
        )
        with col2:
            run_name_selected = st.selectbox(
                "Select a Run Name", unique_run_name, index=len(unique_run_name) - 1
            )
            # Get all the folders in the path
        experiment_folder_path = os.path.join(
            IMAGE_FOLDER_PATH,
            experiment_selected,
            run_version_selected,
            run_name_selected,
            "Images",
        )
        folders = get_all_folders(experiment_folder_path)
        # Add a dropdown to select the folder with the default value as the first folder
        with col2:
            folder_selected = st.selectbox("Select a Well", folders, index=0)
            selected_folder_path = os.path.join(
                experiment_folder_path, folder_selected, IMAGE_MERGE_FOLDER
            )
        if "source_data" not in st.session_state[session_key]:
            with st.spinner("Fetching data..."):
                st.session_state[session_key]["source_data"] = (
                    get_source_data_based_on_transaction_id(transaction_id)
                )

    else:
        st.warning("No unique details found for the selected experiment.")
        folder_selected = None
        selected_folder_path = None
    return folder_selected, selected_folder_path, unique_class_name, transaction_id


def get_images(selected_folder_path):
    images = []
    for file_name in sorted(os.listdir(selected_folder_path)):
        if file_name.endswith((".png", ".jpg", ".jpeg")):
            file_path = os.path.join(selected_folder_path, file_name)
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append((file_name, img))
    return images


def set_default_value_selected_folder(folder_selected, session_key):
    if folder_selected not in st.session_state[session_key]:
        st.session_state[session_key][folder_selected] = pd.DataFrame(
            columns=["Time", "Cell Type", "Value"]
        )
        st.session_state[session_key][f"image_and_time_info_{folder_selected}"] = []


def update_play_timelapse_active_status(
    play_timelapse, resume_timelapse, stop_timelapse
):
    # Handle button interactions
    if play_timelapse:
        st.session_state.play_timelapse_active = True
        st.session_state.current_frame_idx = 0
    if stop_timelapse:
        st.session_state.play_timelapse_active = False
    if resume_timelapse:
        st.session_state.play_timelapse_active = True


def draw_graph_play_timelapse_active(session_key, folder_selected, chart_placeholder):
    # Update chart with new data
    fig = px.line(
        st.session_state[session_key][folder_selected],
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
    return chart_placeholder


def draw_graph_play_timelapse_inactive(
    filtered_data,
    chart_placeholder
):
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


def draw_image(image_placeholder, bboxes, class_labels, img, file_name, idx):
    image = draw_detection(img, bboxes, class_labels)
    image_placeholder.image(
        img,
        caption=f"Frame: {file_name}, idx: {idx}",
        use_container_width=True,
    )
    return image_placeholder


def draw_image_without_bbox(image_placeholder, img, file_name, idx):
    image_placeholder.image(
        img,
        caption=f"Frame: {file_name}, idx: {idx}",
        use_container_width=True,
    )
    return image_placeholder


def setup_cell_counting_analytics_column_timelapse_active(
    col1, col2, images, session_key, folder_selected, unique_class_name
):
    with col2:
        # st.subheader("Cell Counting Result ")
        chart_placeholder = st.empty()  # Placeholder for the chart
        image_placeholder = col1.empty()
        if st.session_state.play_timelapse_active:
            image_placeholder = col1.empty()
            # Start timelapse and update graph
            for idx in range(st.session_state.current_frame_idx, len(images)):
                st.session_state.current_frame_idx = idx  # Save the current frame index

                # Check if playback is stopped
                if not st.session_state.play_timelapse_active:
                    break
                # Update image in the placeholder
                file_name, img = images[idx]
                # Update real-time data
                st.session_state, bboxes, class_labels = generate_real_time_data(
                    session_key,
                    folder_selected,
                    file_name,
                    unique_class_name,
                    st.session_state,
                )
                image_placeholder = draw_image(
                    image_placeholder, bboxes, class_labels, img, file_name, idx
                )
                chart_placeholder = draw_graph_play_timelapse_active(
                    session_key, folder_selected, chart_placeholder
                )
                # Pause for real-time effect
                time.sleep(0.5)
            st.session_state.play_timelapse_active = False
    return chart_placeholder, image_placeholder


def main():
    session_key, col1, col2, st.session_state = setup_initial_session_state()
    # Column 1: Image Viewer
    with col1:
        if is_check_folder_path_existed:
            # Add a dropdown to select the folder with the default value as the first folder
            folder_selected, selected_folder_path, unique_class_name, transaction_id = (
                setup_select_boxes(col2, session_key)
            )
            images = get_images(selected_folder_path)
            set_default_value_selected_folder(folder_selected, session_key)
            if images:
                play_timelapse, resume_timelapse, stop_timelapse = setup_buttons()
            else:
                st.warning("No images found in the specified folder.")
        else:
            st.error(
                "The specified folder path does not exist. Please enter a valid path."
            )
        update_play_timelapse_active_status(
            play_timelapse, resume_timelapse, stop_timelapse
        )
        # Column 2: Real-Time Line Chart
        chart_placeholder, image_placeholder = (
            setup_cell_counting_analytics_column_timelapse_active(
                col1,
                col2,
                images,
                session_key,
                folder_selected,
                unique_class_name,
            )
        )
    if not st.session_state.play_timelapse_active:
        with col2:
            # Display the image based on the slider value
            frame_idx = st.slider(
                "Select Frame",
                min_value=0,
                max_value=len(images) - 1,
                value=st.session_state.current_frame_idx,
                key="frame_slider",
            )
        file_name, img = images[frame_idx]
        image_placeholder = draw_image_without_bbox(
            image_placeholder, img, file_name, frame_idx
        )
        # filer time info with image name
        image_and_time_info_filtered = [
            item
            for item in st.session_state[session_key][
                f"image_and_time_info_{folder_selected}"
            ]
            if item[0] == images[frame_idx][0]
        ]
        if image_and_time_info_filtered:
            file_name, time_stamp, bbox_results, class_labels = (
                image_and_time_info_filtered[0]
            )
            draw_image(image_placeholder, bbox_results, class_labels, img, file_name, frame_idx)
        else:
            time_stamp = pd.Timestamp.now()
        filtered_data = st.session_state[session_key][folder_selected][
                st.session_state[session_key][folder_selected]["Time"] <= time_stamp
            ]
        draw_graph_play_timelapse_inactive(
                filtered_data,
                chart_placeholder,

            )

    with col2:
        # Button to clear data
        st.button(
            "Clear Data",
            on_click=clear_data,
            args=(session_key, folder_selected, st.session_state),
        )


if __name__ == "__main__":
    main()

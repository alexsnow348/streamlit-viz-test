import pandas as pd
import os
import json


def get_unique_cell_type():
    unique_cell_type = ["RGB_100", "RGB_101", "RGB_011", "RGB_001"]
    return unique_cell_type

# Function to simulate real-time data
def generate_real_time_data(session_key, folder_selected, file_name, session_state):
    existing_data = session_state[session_key][folder_selected]
    existing_image_and_time_info = session_state[session_key][
        f"image_and_time_info_{folder_selected}"
    ]
    new_data_test = session_state[session_key]["source_data"][
        session_state[session_key]["source_data"]["image_name"] == file_name
    ]
    #  2024-05-29 11:48:20.963000
    new_time_stamp = (
        new_data_test["date"].values[0] + " " + new_data_test["time"].values[0]
    )
    # transform to timestamp
    new_time_stamp = pd.to_datetime(new_time_stamp)
    unique_cell_type = get_unique_cell_type()
    cell_value_list = []
    for cell_type in unique_cell_type:
        cell_value_list.append(new_data_test[cell_type].values[0])
    new_data_test_dict = {
        "Time": [new_time_stamp] * len(unique_cell_type),  # Repeat the timestamp for each metric
        "Cell Type": unique_cell_type,
        "Value": cell_value_list,
    }
    new_df_test = pd.DataFrame(new_data_test_dict)
    updated_data = pd.concat([existing_data, new_df_test])
    existing_image_and_time_info.append((file_name, new_time_stamp))
    session_state[session_key][folder_selected] = updated_data
    session_state[session_key][
        f"image_and_time_info_{folder_selected}"
    ] = existing_image_and_time_info
    return session_state


# get unique values from run_version column from the source data
def get_unique_run_version(session_state, session_key):
    unique_run_version = session_state[session_key]["source_data"][
        "run_version"
    ].unique()
    return unique_run_version


# get unique run_name from the source data
def get_unique_run_name(session_state, session_key):
    unique_run_name = session_state[session_key]["source_data"]["run_name"].unique()
    return unique_run_name



# define function to get all the name of the folders in the path and check if there any items in the folder
def get_all_folders(path):
    folders = [
        name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))
    ]
    return folders


def read_input_source_data():
    # read json data from a file

    json_file_path = "/home/wut/playground/streamlit-viz-test/data/data.json"
    with open(json_file_path, "r") as f:
        data = json.load(f)
    # transform json data to dataframe
    data = pd.DataFrame(data)
    return data


def get_experimenet_list():
    return [
        "20240529 K562-NK cells purified_Killing Assay (9b33)",
    ]

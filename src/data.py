import pandas as pd
import os
import json
import requests as rq
import logging

# logger
logger = logging.getLogger(__name__)

# load the .env file
from dotenv import load_dotenv

load_dotenv()

# Get the folder path from the environment variable
IMAGE_FOLDER_PATH = os.getenv("IMAGE_FOLDER_PATH")
CELL_COUNTING_DATASOURCE_ENDPOINT = os.getenv("CELL_COUNTING_DATASOURCE_ENDPOINT")
SOURCE_DATA_FOLDER = os.getenv("SOURCE_DATA_FOLDER")

def filter_data_based_on_folder_name(source_data, file_name):
    filtered_data = {}
    
    for item in source_data:
        # print(item)
        if item["image_name"] == file_name:
            filtered_data = item
            break
    return filtered_data

# Function to simulate real-time data
def generate_real_time_data(
    session_key, folder_selected, file_name, unique_class_name, session_state
):
    existing_data = session_state[session_key][folder_selected]
    existing_image_and_time_info = session_state[session_key][
        f"image_and_time_info_{folder_selected}"
    ]
    new_data_test = filter_data_based_on_folder_name(
        session_state[session_key]["source_data"], file_name
    )
   
    #  2024-05-29 11:48:20.963000
    new_time_stamp = new_data_test["image_datetime"]
    # transform to timestamp
    new_time_stamp = pd.to_datetime(new_time_stamp)

    cell_value_list = []
    for class_name in unique_class_name:
        cell_value = new_data_test[class_name]
        cell_value_list.append(cell_value)
    new_data_test_dict = {
            "Time": [new_time_stamp]
            * len(unique_class_name),  # Repeat the timestamp for each metric
            "Cell Type": unique_class_name,
            "Value": cell_value_list,
        }
    new_df_test = pd.DataFrame(new_data_test_dict)
    updated_data = pd.concat([existing_data, new_df_test])
    bbox_results = new_data_test["bbox_results"]
    class_labels = new_data_test["class_name_results"]
    existing_image_and_time_info.append((file_name, new_time_stamp, bbox_results, class_labels))
    session_state[session_key][folder_selected] = updated_data
    session_state[session_key][
            f"image_and_time_info_{folder_selected}"
        ] = existing_image_and_time_info
    return session_state, bbox_results, class_labels


# get unique values from run_version column from the source data
def get_unique_details(transaction_id):
    unique_details = {}
    unique_details_url = (
        f"{CELL_COUNTING_DATASOURCE_ENDPOINT}/unique_details/{transaction_id}"
    )
    response = rq.get(unique_details_url)
    if response.status_code != 200:
        logger.error(
            f"Error in getting the unique details from the datasource: {unique_details}"
        )
    else:
        response_json = response.json()
        unique_details = response_json["unique_details"]
    return unique_details


# define function to get all the name of the folders in the path and check if there any items in the folder
def get_all_folders(path):
    folders = [
        name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))
    ]
    return folders



def get_source_data_based_on_transaction_id(transaction_id):
    json_file_path = f"{SOURCE_DATA_FOLDER}/{transaction_id}.json"
    if not check_existing_data(json_file_path):
        # read json data from a file
        cell_counting_summary_url = (
            f"{CELL_COUNTING_DATASOURCE_ENDPOINT}/summary/{transaction_id}"
        )
        response = rq.get(cell_counting_summary_url)
        if response.status_code != 200:
            logger.error(
                f"Error in getting the source data from the datasource: {response.json()}"
            )
        else:
            data = response.json()["results"]
            # write to json file
            with open(json_file_path, "w") as f:
                json.dump(data, f)
    else:
        with open(json_file_path, "r") as f:
            data = json.load(f)
    return data


def check_existing_data(json_file_path):
    if not os.path.exists(SOURCE_DATA_FOLDER):
        os.makedirs(SOURCE_DATA_FOLDER)
    if not os.path.exists(json_file_path):
        return False
    else:
        return True


def get_experiment_list():
    experiment_list = []
    try:
        experiment_url = f"{CELL_COUNTING_DATASOURCE_ENDPOINT}/experiments"
        response = rq.get(experiment_url)
        response_json = response.json()
        if response.status_code != 200:
            logger.error(
                f"Error in getting the experiment list from the datasource: {response_json}"
            )
        else:
            experiment_list = response_json["experiments_list"]

    except Exception as e:
        logger.error(f"Error in getting the experiment list from the datasource: {e}")
    logger.info(f"Experiment list: {experiment_list}")
    return experiment_list

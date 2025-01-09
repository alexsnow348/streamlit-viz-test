import pandas as pd


def clear_data(session_key, folder_selected, session_state):
    session_state[session_key][folder_selected] = pd.DataFrame(
        columns=["Time", "Cell Type", "Value"]
    )
    session_state[session_key][f"image_and_time_info_{folder_selected}"] = []
    session_state.play_timelapse_active = False
    session_state.current_frame_idx = 0
    return session_state

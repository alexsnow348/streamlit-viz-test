# Streamlit Visualization Test

This repository contains a project to test and demonstrate various visualization techniques using Streamlit.

## Folder Structure

```
streamlit-viz-test/
├── README.md
├── src/
├── requirements.txt
└── data/
    └── sample_data.csv
```

## Files

- `README.md`: This file. Provides an overview of the project.
- `src`: The main Streamlit application src.
- `requirements.txt`: A list of Python packages required to run the Streamlit app.


## Getting Started

To get started with this project, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/alexsnow348/streamlit-viz-test.git
    cd streamlit-viz-test
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:
    ```sh
    streamlit run src/app.py
    ```
## Docker

1. Build the docker image.
    ```
    docker build -t <ml-fronte>:<tag> .
    ```
2. Run the docker image.
    ```
    docker run -d --name my_container -p <host_port>:<container_port> -v <host_dir>:<container_dir> <image_name>
    ```
    Sample:
    ```
    docker run -d --rm --name mlfronend -p 8501:8501 -v /data/biolab_arralyze_picture_data:/data/biolab_arralyze_picture_data ml-frontend:v0.0.1
    ```

## Usage

Once the app is running, you can interact with various visualizations by navigating through the Streamlit interface.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
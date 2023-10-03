# DeepAD-Reinforcement Learning for Traffic Simulation

## Modules
- Macroscopic route recommendation
- Microscopic lane changing

This repository contains the implementation of a deep-learning model for anomaly detection.

## micro_load.py: Loading datasets and their respective labels.

   - Purpose: This script appears to be responsible for loading data. It contains functions such as `load_data` and `load_label`, which likely handle the loading of dataset and labels respectively.
   - Key Functions:
     - `load_data`: Loads the dataset.
     - `load_label`: Loads the labels for the dataset.
   - Imports: The script imports libraries such as `numpy`, `os`, and `pandas`.

## `micro_multi_load.py`: An extension of `micro_load.py` tailored for handling multi-modal data.
   - Purpose: This script seems to be an extension or variation of the `micro_load.py` script, but tailored for handling multiple datasets or multi-modal data. It contains functions like `multi_load_data` and `multi_load_label`.
   - Key Functions: 
     - `multi_load_data`: Loads multiple datasets or multi-modal data.
     - `multi_load_label`: Loads labels for the multi-modal data.
   - Imports: Similar to `micro_load.py`, this script imports `numpy`, `os`, and `pandas`.

## `micro_train.py`: Contains the training and testing logic for the model.
   - Purpose: As the name suggests, this script is likely responsible for training a model. It contains functions such as `train`, `test`, and `main`, indicating the primary steps involved in the training and testing process.
   - Key Functions:
     - `train`: Handles the training process of a model.
     - `test`: Tests the trained model.
     - `main`: The main function that orchestrates the training and testing processes.
   - Imports: This script imports several libraries, including `torch`, `numpy`, `os`, `time`, and `micro_load`, indicating its reliance on PyTorch for deep learning and `micro_load.py` for data loading.

These scripts form the foundation of a deep learning project, with functionalities for data loading and model training. 

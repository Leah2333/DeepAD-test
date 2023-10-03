# DeepAD-Reinforcement Learning for Traffic Simulation

## Modules
- Macroscopic route recommendation
- Microscopic lane changing

This repository contains the implementation of a deep-learning model for anomaly detection.

## Python Scripts:
- `micro_load.py`: Responsible for loading datasets and their respective labels.
- `micro_multi_load.py`: An extension of `micro_load.py` tailored for handling multi-modal data.
- `micro_train.py`: Contains the training and testing logic for the model.

## Directories:
- `data`: Contains the datasets required for the model.
- `model`: Houses the model architectures and related utilities.
- `output`: Contains the output results from the model.
- `utils`: Utility scripts and functions to assist in various tasks.

# Data Directory

This directory contains the datasets required for training and testing the deep learning model.

## Files:
- Datasets in `.npy` format: These are NumPy arrays storing the data samples.
- Label files in `.npy` format: Corresponding labels for the datasets.

Ensure that the data is correctly placed in this directory before running the training script.

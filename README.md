# DeepAD-Reinforcement Learning for Traffic Simulation

## Modules
- Macroscopic route recommendation
- Microscopic lane changing

This repository contains the implementation of a deep-learning model for anomaly detection.

### micro_load.py: 

**Loading datasets and their respective labels.**

     - `load_data`: Loads the dataset.
     - `load_label`: Loads the labels for the dataset.

### `micro_multi_load.py`: 

**An extension of `micro_load.py` tailored for handling multi-modal data.**

     - `multi_load_data`: Loads multiple datasets or multi-modal data.
     - `multi_load_label`: Loads labels for the multi-modal data.

### `micro_train.py`: 

**Contains the training and testing protocol for the model.**

     - `train`: Handles the training process of a model.
     
     - `test`: Tests the trained model.
     
     - `main`: The main function that orchestrates the training and testing processes.

These scripts form the foundation of a deep learning project, with functionalities for data loading and model training. 

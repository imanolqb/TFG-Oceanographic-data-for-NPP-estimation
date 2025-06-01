<a href="https://www.eii.ulpgc.es" target="_blank"><img src="https://www.ulpgc.es/sites/default/files/ArchivosULPGC/identidad-corporativa/NuevoLogo/eii_hc_0.png" alt="EII-ULPGC" align="right" width="516" height="150" /></a>

# BACHELOR'S DEGREE FINAL PROJECT

> - Digital Twin Based on Neural Networks Using Picota
> - Developed by Imanol Quintero Bermúdez, under the supervision of Yeray Santana Falcón, PhD, and José Évora Gómez, PhD
> - [Imanol Personal Page](https://imanolqb.github.io)

## Project Overview

This project aims to develop a digital twin of the ocean using neural networks, leveraging the Picota tool for data processing and model deployment. The main objective is to create a robust and scalable system capable of simulating and predicting oceanographic variables by integrating heterogeneous datasets and advanced machine learning techniques.

The project covers the entire workflow: from data acquisition and preprocessing, through neural network training and evaluation, to the visualization and analysis of results. The digital twin is designed to support research and decision-making in marine science, providing accurate and interpretable predictions of key variables.

## Dataset and Data Processing

The datasets used in this project include multi-source oceanographic data in NetCDF and CSV/TSV formats. Data preprocessing steps include:

- **Conversion**: scripts to convert NetCDF files to CSV/TSV for easier manipulation.
- **Filtering**: removal of non-ocean tiles and irrelevant columns.
- **Coverage Analysis**: tools to analyze and visualize data completeness across variables and records.
- **Interpolation**: filling missing values using nearest neighbor and RBF interpolation methods.

All data processing scripts are located in the utils directory, with modular code for easy adaptation to new datasets.

## Neural Network Model

The neural network architecture is designed for regression and prediction of ocean variables. Key features include:

- Flexible input handling for multi-dimensional data.
- Customizable layers and hyperparameters.
- Integration with Picota for streamlined training and deployment.
- Evaluation using standard metrics and cross-validation.

The model is trained on historical data and validated using recent observations to ensure generalization and robustness.

## Project Structure

```text
project/
├── src/
│   └── utils/
│       ├── converters/
│       ├── interpolation/
│       ├── netcdf_utils/
│       ├── downloaders/
│       └── visualization/
├── data/
│   ├── measurements.tsv
│   └── measurements.csv
├── results/
└── README.md
```

## Technologies Used

- Python (pandas, numpy, xarray, matplotlib, seaborn, scikit-learn)
- Picota (for workflow orchestration and model management)
- NetCDF, CSV/TSV data formats

## Results and Visualizations

The project includes scripts for generating visualizations of data coverage, variable anomalies, and model predictions. Example outputs:

- Coverage Analysis: Bar plots and density distributions of data completeness.
- Anomaly Detection: Maps and time series of variable anomalies between periods.
- Prediction Performance: Plots of predicted vs. observed values, error distributions, and more.

All results are saved in the results/ directory for further analysis.

## Acknowledgements

- Supervised by Yeray Santana Falcón, PhD, and José Évora Gómez, PhD
- Developed at the [School of Computer Engineering, ULPGC](https://www.eii.ulpgc.es)
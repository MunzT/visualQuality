|                                                                                                  ![App](application.png?raw=true)                                                                                                  | 
|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:| 
| *User interface of our interactive system to explore the projection quality of multidimensional time series generated with the dimensionality reduction method t-SNE. The image shows the uncertainty-highlighting visualization.* |


# Visual Analysis System to Explore the Visual Quality of Multidimensional Time Series Projections

Our approach generates visualizations for multidimensional time series projections.
The projections can be generated with different dimensionality reduction methods. The visualizations show the temporal data along with methods to explore the visual quality of the projections and visualizations.

This is the source code behind the approach described in the following publication:
> T. Munz-Körner, and D. Weiskopf. Exploring visual quality of multidimensional time series projections. Visual Informatics. 2024.
https://doi.org/10.1016/j.visinf.2024.04.004.


Our system provides three different types of visualizations:
* The **projection visualization** shows the samples of the projection as dots along with their connections for the temporal development.
* The interactive **uncertainty-highlighting visualization** highlights problematic regions of the projection and visualization.
* The **halo visualization** fades such problems in the visualization.

First, the data has to be preprocessed and projected to 2D (e.g., with PCA, MDS, t-SNE, or UMAP). Afterward, it can be visualized and explored in our interactive visualization system.

## Data Preparation and Visualization

We developed our approach with Python 3.7.4 under Ubuntu 22.04/Windows 10. The user interface was tested with Firefox (version 115.0.1).

The file [datasets.txt](datasets.txt) must contain the path(s) to the directories containing raw data (CSV file(s), images, ...) and setting files in order to be available for the preprocessing steps and visualization.

Multiple scripts are provided (*.sh* files for Linux (in [run_linux](run_linux)) and *.bat* files for Windows (in [run_windows](run_windows))) to quickly run the system.

First, we recommend creating the virtual environment and installing all requirements with *0_create_venv.\[sh|bat]*:

Next, data can be reduced to 50 dimensions with PCA and be standardized with *1_preprocessData.\[sh|bat]*. 
*1_preprocessData* takes the file *origDatasets.csv* as a lookup table for data sets. The paths of the newly created files are written to *2_preprocessedData.csv*.

Next, the preprocessed data is projected to 2D for the specified settings with *2_createDataForVis.\[sh|bat]* (multiple settings can be defined, e.g., for different dimensionality reduction methods). 
All created projections are saved in *3_visData* and *3_preview* contains preview images for all projections.

Finally, the interactive tool can be started with *3_runExplorer.\[sh|bat]*. It takes *3_visData.csv* as an input file for an overview of available data sets. 

Next, start the user interface with http://127.0.0.1:2000/ in a browser (we recommend Firefox) to explore the data.

If you just want to test our visual analysis system, run *0_create_venv.\[sh|bat]* and afterward *3_runExplorer.\[sh|bat]*.
Start the user interface with http://127.0.0.1:2000/ in a browser and explore our example data.

## File Descriptions

### Input Files to Preprocess Data

We allow multiple types of data to be preprocessed by our system:

* **CSV** (csv) <br>
A common CSV file. Each row specifies one time step consisting of multiple properties (each column is one dimension).

* **Multiple CSV files** (csv_multipleFiles) <br>
Each file specifies one time step. Each line of a file represents one dimension.

* **Series of Images** (images) <br>
Each image specifies one time step. Each pixel (red, green, and blue separately) represents one dimension.

* **BGRAPH** (bgraph) <br>
This is a specific file type that contains a series of graphs.

In a file *origDatasets.csv* that is used by [preprocessData.py](preprocessData.py), each line specifies one dataset. 
Each dataset contains the following values:
- An id (any string) for the data set.
- The file path to the file/directory (a directory for csv_multipleFiles and images; a file path for the other data types).
- The data set type (csv, csv_multipleFiles, images, or bgraph).

### Settings for preprocessing

The file *preprocessData.toml* contains settings for preprocessing: settings for PCA and if standardization should be used.
If multiple values are given for a parameter, preprocessing is performed multiple times.

Example:
```bash
preprocessing = ["no", "standardization"]

[PCA] 
random_state = [42]
metric =["euclidean"]
n_components = [50]
```

### Settings to Create Data for Visualization

The file *visData.toml* contains information about the projection methods and their settings.
If multiple values are given for a parameter, data for visualization is created multiple times for each set of settings.

Example:
```bash
[general]
dimRedMethod = ["PCA", "MDS", "tSNE", "UMAP"]

[PCA]
random_state = [42]

[MDS]
random_state = [42, 32489013]
dissimilarity = ["euclidean"]
metric = [true]

[tSNE]
random_state = [42]
metric = ["euclidean"]
perplexity = [10, 30, 50]

[UMAP]
random_state = [42]
```

## Datasets

We provide the datasets used in our corresponding publication (preprocessed data and some original source files) in the [datasets](datasets) directory.
If you want to create your own data, you can have a look at these examples.

### Artificial Data
We provide the scripts for generating the artificial data, the raw data, and the data used for visualization. Examples include different spirals, clusters, crossing lines, and a logarithmic change.

### Kármán Simulation
We provide preprocessed data for visualization of the Kármán simulation.

### Covid-19
For the Covid-19 data, raw data is used from https://github.com/CSSEGISandData/COVID-19; downloaded 07/03/2023.
We adapted columns/rows such that each row of the file represents one time instance.
Therefore, we provide the modified raw and preprocessed data for visualization.

### Hurricane Dorian Timelapse
The video of Hurricane Dorian was downloaded from https://www.youtube.com/watch?v=e3g7NpCkZMM. We saved a frame every second.
From resized images, we generated the data for visualization. The images are provided and  preprocessed data for visualization. 

## Dependencies

Our system uses the packages listed in the requirements files [requirements.txt](requirements.txt).
For the visual analysis system, [D3.js](https://d3js.org/) is used for the visualizations.

## License

Our project is licensed under the [MIT License](LICENSE.md).

## Citation

Please cite our paper *Exploring Visual Quality of Multidimensional Time Series Projections* when referencing our work.

T. Munz-Körner, and D. Weiskopf. Exploring visual quality of multidimensional time series projections. Visual Informatics. 2024.
https://doi.org/10.1016/j.visinf.2024.04.004.

```
@article{visInf2023quality,
  author  = {Munz-Körner, Tanja and Weiskopf, Daniel},
  title   = {Exploring Visual Quality of Multidimensional Time Series Projections},
  journal = {Visual Informatics},
  year    = {2024},
  doi     = {10.1016/j.visinf.2024.04.004}
}
```

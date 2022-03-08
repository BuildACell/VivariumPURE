# VivariumPURE
Using Vivarium to build a modular model of PURE

Tom -> created a yml file where you can create the conda env from. Users can use the following command in command line to replicate the conda env:
```
conda env create -f environment.yml
```


Steps to replicate this env manually:

In command line
```
conda create -n vyvarium python==3.8
conda activate vyvarium
pip install biocrnpyler
pip install pytest
pip install vivarium_bioscrape
```



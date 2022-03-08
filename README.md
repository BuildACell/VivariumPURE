# VivariumPURE
Using Vivarium to build a modular model of PURE

# dependencies

Here we created a yml file where you can create the conda env from. Users can use the following command in command line to replicate the conda env:
```
conda env create -f environment_1.yml
```

And then, you can start the conda environment with
```
conda activate vyvarium
```

In this environment, you should be able to then run everything smoothly.

If you want to replicate this env manually (you really dont have to), you can do the following in command line:
```
conda create -n vyvarium python==3.8
conda activate vyvarium
pip install biocrnpyler
pip install pytest
pip install vivarium_bioscrape
conda install jupyter 
```



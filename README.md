# DFT-Turbomole
The DFT-Turbomole WaNo implements a wide range of methods available within the Turbomole code, based on Gaussian basis sets this code has been applied for the development of many fast and low-scaling algorithms in the recent decades, turning it into one of the most widely used electronic structure programs. This WaNo affords experienced and inexperienced users to perform DFT and TDDFT calculations without requiring a deep understanding of Turbomole functionalities and specifications. The structure file in xyz format is the single mandatory file as the input of the WaNo. All the remaining input files are automatically generated or loaded from an external source.

<img src="Turbomole.png" alt="drawing" width="700"/>

Figure 1 displays the Turbomole flags, where we can name the calculation and define the following field of parameters: `Molecular structure`, `Basis set`, `initial guess`, `DFT options` and `Type of calculation`.

## 1. Python Setup
To get this WaNo up running on your available computational resources, make sure to have the below libraries installed on Python 3.6 or newer.

```
1. Atomic Simulation Environment (ASE).
2. Python Materials Genomics (Pymatgen).
3. subprocess, glob, os, sys, yaml. 
```


## Description

This is a sample WaNo.


## Parameters

**Input File:**
* just a sample input file

### General Settings

**Print** (default: "Text")
* Determines wether the Number or the String will be printed

**Text:** (default: "Text")
* The String that will be printed

**Number:** (default: 10 )
* The Number that will be printed  
 

## Output
**output.txt** 
* the file including the output

**output.txt**

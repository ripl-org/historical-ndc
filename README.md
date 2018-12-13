# Assembling a Historical National Drug Code Directory from the Internet Archive

This repositority provides a data-processing pipeline for downloading and collating historical archives of the [National Drug Code (NDC) Directory](https://www.fda.gov/Drugs/InformationOnDrugs/ucm142438.htm) from the [Internet Archive](https://archive.org/). The NDC Directory is only available as a current snapshot that is missing data on previously registered drugs. Also, the drug classification provided by the Directory has changed over time. Because of these inconsistencies and missing data, research with historical pharmacy claims data will have an increasing number of claims going back in time that cannot be matched on NDC code to drug data in the current Directory. The goal of this framework is to build an open-source, comprehensive list of historical NDC codes linked to their last known drug data and classification. As an example, we use the historical list of active ingredients genereated by the pipeline to create a classification of opioid drugs and recovery drugs used in medication-assisted treatment for opioid use disorder.

The pipeline was developed to support research projects at
[Research Improving People's Lives](https://ripl.org).

## Installation

Requires:
* Python 3.6+
* pandas
* requests
* scons 

**Note**: we have patched scons to support Python 3.6+, available in a fork
[https://github.com/mhowison/scons/releases](https://github.com/mhowison/scons/releases)
as release "3.0.1-hotfix1".

We recommend installing the required packages using **Anaconda Python**. First
[download](https://www.anaconda.com/download/) and install an Anaconda or Miniconda
distribution. Then run the command:

    conda create -n historical-ndc -c ripl-org python=3.7 pandas requests scons

This will create a new environment **historical-ndc** with the patched version of scons
available from our Anaconda channel. Load the environment with:

    source activate historical-ndc

## Run

The run order and dependencies of the scripts are specified in the SConstruct
file.  The entire pipeline can be run by executing the `scons` command from the
root directory of the repo.

## Output

The pipeline will generate three output files in the `output/` subdirectory:
* `ndc-drugs.csv` is the collated list of all drugs with unique NDCs across all historical snapshots of the Directory;
* `ndc-ingredients.csv` contains entries for the individual activate ingredients in each drug;
* `ndc-opiods.csv` contains a classification for "opioid" and "recovery" drugs, as explained above.

## Organization

* `SConstruct` is the main scons file for running the pipeline.
* `lib/process_*.py` contain logic for parsing three different formats used by the Directory: old (1998-2005), mid (2006-2010), and new (2011-current).
* `lib/opioids.py` contains logic for classifying drugs as "opioid" or "recovery" based on active ingredients.
* `InternetArchive` contains scripts for downloading all available Internet Archive snapshots of the NDC Directory between the years 2000-2018. These were last run on April 11, 2018 and the resulting snapshots have been bundled and are available for download from figshare (doi:[10.6084/m9.figshare.6128225.v1](https://doi.org/10.6084/m9.figshare.6128225.v1)). These scripts can be rerun again in the future to extend the range of the directory past 2018.
* `scratch` will contain downloaded data and intermediate output from the pipeline while it is running.
* `output` will contain the final output of the pipeline when it completes. For reference, we have included the latest output of our run of the pipeline in the repo.

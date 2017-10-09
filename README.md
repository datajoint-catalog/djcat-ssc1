# djcat-ssc1

This pipeline is based on the study described in:

[A Cellular Resolution Map of Barrel Cortex Activity during Tactile Behavior. Simon P. Peron, Jeremy Freeman, Vijay Iyer, Caiying Guo, Karel Svoboda. Neuron. 2015 May 6;86(3):783-99. doi: 10.1016/j.neuron.2015.03.027
](https://www.ncbi.nlm.nih.gov/pubmed/25913859)

with data available from http://crcns.org/NWB/data-sets/ssc/ssc-1

## Online viewing

All Jupyter notebooks in this catalog can be better viewed online through the
Jupyter.org viewer at http://nbviewer.jupyter.org/github/datajoint-catalog

## Obtain credentials

If you need a database account to try these examples, you can get a free
tutorial account by subscribing through https://datajoint.io.

Before you start working with the pipeline, please obtain the following
credentials:

* host address
* user name 
* password

# Setup

The instructions for downloading the DataJoint library are available here:

http://docs.datajoint.io/setup/Install-and-connect.html

Additionally, the common 'djcat-lab' module for general experiment data needs to
be cloned from:

    https://github.com/datajoint-catalog/djcat-lab.git

since it is referenced from this project.  Be sure to setup your PYTHONPATH
variable accordingly so that djcat-lab is included in sys.path. For example,
your djcat-lab source code is stored in the same folder as this experiment, you
can add it from within python as follows:

    >>> import sys
    >>> import os
    >>> sys.path.insert(0, os.path.join('..','djcat-lab'))


# Support
Please submit issues and questions through the [Issues tab
above](https://github.com/datajoint-catalog/RET-1/issues)

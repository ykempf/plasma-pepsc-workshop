Space Plasma Simulations with Vlasiator on LUMI Supercomputer
=============================================================


Plasma is one of four fundamental states of matter, characterized by the presence of 
a significant portion of charged particles in any combination of ions or electrons. 
Plasma is a powerful phase of matter as it is key to many applications and technologies, 
from astrophysics to space physics, from clean energy production based on fusion to 
compact and cheap particle accelerators. However, it is still a mysterious phase of matter 
as its dynamics is inherently nonlinear, multidimensional and multiscale.


The theoretical description of plasma using analytic modeling tools is somewhat limited and 
great progress in plasma physics has been achieved using computer simulations. 
Indeed, advances in massively parallel simulations using high performance computing (HPC) 
resources have have further boosted our understanding of plasma science at an unprecedented 
resolutions and levels of physical fidelity. These simulations have been producing a new 
wealth of knowledge and enabling key applications for science, industry, and society.


**Plasma-PEPSC** (Plasma Exascale-Performance Simulation Centre) is a European Centre of Excellence leading 
plasma science into the era of exascale computing to drive scientific breakthroughs in plasma science’s most 
significant challenges (fusion energy, accelerator devices and space physics) through cutting-edge hardware and 
software advancements.
The overarching goal of Plasma-PEPSC is to take this technological development to the next level, enabling unprecedented 
simulations on current pre-exascale and future exascale platforms across Europe. Four flagship plasma codes with a 
large user base – BIT, GENE, PIConGPU, and Vlasiator – serve as the focal points of the centre of excellence. 
By maximising their parallel performance and efficiency, we aim to achieve breakthroughs in controlling plasma-material 
interfaces, optimising magnetically confined fusion plasmas, designing next-generation plasma accelerators and predicting 
space plasma dynamics within the Earth’s magnetosphere.


`**Vlasiator** <https://www.helsinki.fi/en/researchgroups/vlasiator>`_ (`GitHub <https://github.com/fmihpc/vlasiator>`_) is 
the state-of-the-art hybrid-Vlasov simulation for ion-scale physics in a global 
magnetospheric setting. It is the only 6D hybrid-Vlasov code capable of simulating 
the Earth's magnetosphere. In Vlasiator, ions are represented as velocity distribution functions, 
while electrons are a massless charge-neutralizing fluid, enabling a self-consistent global plasma simulation 
that can describe multi-temperature plasmas to resolve non-MHD processes that currently 
cannot be self-consistently described by the existing global space weather simulations. 
The novelty is that by modelling ions as velocity distribution functions the outcome will be 
numerically noiseless. Due to the multi-dimensional approach at ion scales, Vlasiator's 
computational challenges are immense. Advanced HPC techniques will be adopted using tens of 
thousands of cores to perform massively parallel computations.


.. prereq::

  - PhD students, postdocs, industry engineers
  - Basic familiarity with general physics and plasma physics
  - Some previous practical experience running some CFD code
  - Basic familiarity with Unix shell and HPC environment
  - Some materials towards advanced users


.. csv-table::
   :widths: auto
   :delim: ;

   20 min ; :doc:`filename`

.. toctree::
   :maxdepth: 1
   :caption: Prerequisites

   introduction
   prepare_workspace

.. toctree::
   :maxdepth: 1
   :caption: The lessons

   installing-vlasiator
   benchmarks_and_running
   vlasiator_outputs
   visit
   analysator
   analysator_exercises
..
   vlasiator_projects
   example_run

.. toctree::
   :maxdepth: 1
   :caption: Reference

   quick-reference
   vlasiator-cfg-reference
   analysator_supported
   new_project


.. _learner-personas:

Who is the course for?
----------------------

This hybrid workshop will bring together code developers, researchers, and research software 
engineers working on plasma science, and create an amazing opportunity for sharing innovative 
ideas and best practice for potential users to use the Vlasiator package and using its 
capabilities and assorted tools for data analysis.



About the course
----------------

This workshop includes:

- running simulations at scale
- benchmarking for deploying Vlasiator on supercomputing environments
- designing a simulation setup, with notes on applicability and resources required
- Accessing the .vlsv data via Analysator
- Accessing the .vlsv data via the VisIt plugin

After attending this workshop, you will:

- Understand core features of the Vlasiator package 
- Be efficient using the Vlasiator package to perform plasma simulations
- Be productive in data analysis and visualization of simulation results
- Be able to create your own project


See also
--------

- ENCCS: https://enccs.se/
- Plasma-PEPSC CoE: https://plasma-pepsc.eu/
- Follow ENCCS on `LinkedIn <https://www.linkedin.com/company/enccs>`__, or `Twitter <https://twitter.com/EuroCC_Sweden>`__



Credits
-------

The lesson file structure and browsing layout is inspired by and derived from
`work <https://github.com/coderefinery/sphinx-lesson>`__ by `CodeRefinery
<https://coderefinery.org/>`__ licensed under the `MIT license
<http://opensource.org/licenses/mit-license.html>`__. We have copied and adapted
most of their license text.

Instructional Material
^^^^^^^^^^^^^^^^^^^^^^

This instructional material is made available under the
`Creative Commons Attribution license (CC-BY-4.0) <https://creativecommons.org/licenses/by/4.0/>`__.
The following is a human-readable summary of (and not a substitute for) the
`full legal text of the CC-BY-4.0 license
<https://creativecommons.org/licenses/by/4.0/legalcode>`__.
You are free to:

- **share** - copy and redistribute the material in any medium or format
- **adapt** - remix, transform, and build upon the material for any purpose,
  even commercially.

The licensor cannot revoke these freedoms as long as you follow these license terms:

- **Attribution** - You must give appropriate credit (mentioning that your work
  is derived from work that is Copyright (c) ENCCS and individual contributors and, where practical, linking
  to `<https://enccs.github.io/sphinx-lesson-template>`_), provide a `link to the license
  <https://creativecommons.org/licenses/by/4.0/>`__, and indicate if changes were
  made. You may do so in any reasonable manner, but not in any way that suggests
  the licensor endorses you or your use.
- **No additional restrictions** - You may not apply legal terms or
  technological measures that legally restrict others from doing anything the
  license permits.

With the understanding that:

- You do not have to comply with the license for elements of the material in
  the public domain or where your use is permitted by an applicable exception
  or limitation.
- No warranties are given. The license may not give you all of the permissions
  necessary for your intended use. For example, other rights such as
  publicity, privacy, or moral rights may limit how you use the material.


Software
^^^^^^^^

Except where otherwise noted, the example programs and other software provided
with this repository are made available under the `OSI <http://opensource.org/>`__-approved
`MIT license <https://opensource.org/licenses/mit-license.html>`__.

Introduction to Vlasiator
=========================

Why we teach this lesson
------------------------

Here we introduce what is Vlasiator.




Intended learning outcomes
--------------------------

* Know what Vlasiator is and does
* Understand what you can do with Vlasiator
* What resources do I need to run Vlasiator for some given task?
* Rules of the Road for using Vlasiator

Timing
------

Tuesday morning, 1h

Preparing exercises
-------------------

Here you can find `Vlasiator introductory lectures <https://datacloud.helsinki.fi/index.php/s/wEZdF3szjBfapSs>`_.

Reference papers for Vlasiator simulation:

* `Alfthan et al., 2014 <https://doi.org/10.1016/j.jastp.2014.08.012>`_, Vlasiator: First global hybrid-Vlasov simulations of Earth's foreshock and magnetosheath. *JASTP*.
* `Palmroth et al., 2018 <https://doi.org/10.1007/s41115-018-0003-2>`_, Vlasov methods in space physics and astrophysics. *LRCA*.
* `Ganse et al., 2023 <https://doi.org/10.1063/5.0134387>`_,  Enabling technology for global 3D + 3V hybrid-Vlasov simulations of near-Earth space. *Phys. Plasmas*.

Highlight results:

* `Turc et al., 2022 <https://doi.org/10.1038/s41567-022-01837-z>`_, Transmission of foreshock waves through Earth’s bow shock. *Nat. Phys*.
* `Palmroth et al. 2023 <https://doi.org/10.1038/s41561-023-01206-2>`_, Magnetotail plasma eruptions driven by magnetic reconnection and kinetic instabilities. *Nat. Geosci*.

Find more at `the group website <https://www.helsinki.fi/en/researchgroups/vlasiator/publications-and-presentations>`_.


Vlasiator
---------

`**Vlasiator** <https://www.helsinki.fi/en/researchgroups/vlasiator>`_ (`GitHub <https://github.com/fmihpc/vlasiator>`_) is the state-of-the-art hybrid-Vlasov simulation for ion-scale physics in a global magnetospheric setting. It is the only 6D hybrid-Vlasov code capable of simulating the Earth's magnetosphere. In Vlasiator, ions are represented as velocity distribution functions, while electrons are massless charge-neutralizing fluid, enabling a self-consistent global plasma simulation that can describe multi-temperature plasmas to resolve non-MHD processes that currently cannot be self-consistently described by the existing global space weather simulations. The novelty is that by modelling ions as velocity distribution functions the outcome will be numerically noiseless. Due to the multi-dimensional approach at ion scales, Vlasiator's computational challenges are immense.

.. figure:: img/BCH_LRCA.webp
    :width: 500
    :alt: Example of a Vlasiator 5D run (LRCA)
    
    A Vlasiator view of the Earth's magnetosphere (5D, Palmroth+2018)


Vlasiator simulates the dynamics of plasma using a hybrid-Vlasov model, where protons are described by their distribution function f(r,v,t) in ordinary (r) and velocity (v) space, and electrons are a charge-neutralising fluid. This approach neglects electron kinetic effects but retains ion kinetics. The time-evolution of f(r,v,t) is given by Vlasov's equation,

.. image:: img/vlasov-eq.webp
    :width: 600
    :alt: Vlasov's equation

which is coupled self-consistently to Maxwell's equations giving the evolution of the electric and magnetic fields E and B. Maxwell's equations neglect the displacement current.

.. image:: img/faraday.png
    :width: 200
    :alt: Faraday's law

and

.. image:: img/ampere.png
    :width: 250
    :alt: Ampere's law



The equations are closed by a generalised Ohm's law including the Hall term (and the electron pressure term, not shown below).

.. image:: img/ohm.webp
    :width: 300
    :alt: Vlasov's equation





State-of-the-art
----------------

Vlasiator is parallelized at multiple scales via MPI, threading support and vectorization, and we are continuously improving the performance and the feature set. GPU porting is in progress: solvers have been ported, but they need to be optimized for GPUs to be useful in production.

The data structures in Vlasiator have been optimized to propagate the 6D solution efficiently with explicit solvers. The velocity distribution functions are associated with a spatial, hierarchically-adapted Cartesian grid (the Vlasov grid, SpatialGrid or the AMR grid), with each such spatial cell containing a VDF for each ion species in the simulation. The VDF themselves are stored on a Cartesian velocity-space grid as a sparse data structure - otherwise the production simulations could not fit any available computers. This implies slight loss of mass at the fringes (under a set sparsity threshold, the VDF is not stored), but the VDF can optionally be re-scaled to conserve mass. Suitably chosen sparsity thresholds enable global runs with negligible adverse effects. Some 98% of the phase-space volume is discarded.

.. figure:: img/sparse-YPK2016.webp
    :width: 500
    :alt: Example of sparse velocity grid.

    Example of sparse velocity grid, Yann Pfau-Kempf, 2016.

.. figure:: img/aBlockyVDF.png
    :width: 500
    :alt: Example of sparse velocity grid.

    Example of sparse velocity grid. The 4x4x4 structure stems from the block data structure.

The numerical algorithm for the propagation of the Vlasov equation is based on operator splitting: spatial translation and velocity-space acceleration are leapfrogged. Spatial translation remaps the VDF as 1D shears. The acceleration re-mapping of the VDF is handled by the semi-Lagrangian SLICE-3D method by Zerroukat and Allen (2012), by decomposing v-space rotation and translation to a series of shear operations. These mappings are conservative by themselves.

.. figure:: img/Strang-Splitting.png
    :width: 400

    Schematic of Strang-splitting the Vlasov propagation, left (yellow) the translation part, right (green) the acceleration part.

Spatial AMR has lately enabled truly 6D simulations of the Earth's magnetosphere (see Ganse+2023). The initial 6D production runs have used statically-refined grid, with a dynamic AMR currently being tested in production.

Spatial AMR, however, is *not* extended to the field solver (*heterologous* grids): Field solver has simple load balancing, while the Vlasov solver does not. The solution is to have *two* grids, with the field solver grid at the highest resolution of the Vlasov grid, throughout the entire domain. There are some details in cross-coupling e.g. plasma moments across these grids. With four levels of refinement, the field solver is contributing about 10% of runtime as it is - Vlasov solver is still the bottleneck.

.. figure:: img/FsGrid_LB.png
    :width: 400

    Example of fieldsolver load balancing

.. figure:: img/SpatialGrid_LB_RCB.png
    :width: 400

    Example of SpatialGrid load balancing, legacy RCB

Improved load balancing algorithms matter. In the above Recursive Coordinate Bisection (RCB) example, one can see small-scale structure in the domain boundaries, which is not optimal for MPI communication buffers. Forcing rectilinear domains for RCB helps, but so do using other methods, like Recursive Inertial Bisection (RIB, below), that can balance MPI communications over the three principal directions.

.. figure:: img/SpatialGrid_LB_RIB.png
    :width: 400
    :alt: Example of load balancing of SpatialGrid, MPI ranks

    Example of load balancing of SpatialGrid, showing the decomposition to MPI ranks, currently used in production.

.. figure:: img/SpatialGrid_LB_blocks.png
    :width: 400
    :alt: Example of load balancing of SpatialGrid

    Example of load balancing of SpatialGrid, showing the velocity-space block-counts.

Recently, we have also included a proper ionospheric inner boundary condition, with an ionosphere solver along the lines of MHD solvers. Further developments are ongoing, incl. better ionization and conductivity profiles. Outer boundary conditions now include the possibility of time-varying solar wind parameters.

Lately, we have included an electron module, eVlasiator (`Battarbee+2021 <https://doi.org/10.5194/angeo-39-85-2021>`_, `Alho+2022 <https://doi.org/10.1029/2022GL098329>`_), that takes an existing Vlasiator solution and runs electron VDFs against that background.

Deploying Vlasiator to various environments has lately (with Plasma-PEPSC!) been made much easier, including compilation on ARM. We'll look at the build process later!

Practical aspects of running Vlasiator
--------------------------------------

What sorts on constraints does Vlasiator have?

Six-dimensional simulations are expensive! Further, there are some constraints from physics on resolution - if you want to be accurate, you will need to resolve some scales.

#. Timestep: Ion cyclotron frequency.
   
   Especially restrictive with global magnetospheric simulations with high magnetic field values close to the poles, with an r^-3 dependence.

   We constrain the timestep to provide a maximum of 22 degrees of cyclotron rotation per step. Further, the Vlasov solver timestep is *so far* a global timestep. This is a bottleneck for the inner boundary.

#. Velocity-space resolution: numerical heating

   Low velocity-space resolution is constrained by thermal velocity: dv ~< v_th/3. For exampe, solar wind Maxwellians exhibit numerical heating for dv >~ v_th/3.

#. Velocity-space sparsity threshold

   Around 10^-15 m^6 s^-3 has been found a decent compromise for the sparsity threshold, retaining the parts of VDFs that are relevant for the dynamics of the system. If you wish to model high-energy tails, the threshold should be pushed down... at the cost of significantly increased memory footprint.

#. Velocity-space extents

   +- 4000...8000 km/s are decent extents for terrestrial magnetospheric simulations with the current sparsity thresholds. Usually VDFs 'hit the walls' only when there is anomalous acceleration, or otherwise very fast and/or hot flows. This results in 200..400 velocity cells per dimension in our usual runs. Sparsity really saves on the memory footprint!

#. Spatial resolution

   Preferably, ion kinetic scale should be resolved (~200 km in Earth's magnetosphere). In 6D global production runs, we have not yet reached this (max resolution 1000 km). 5D runs can go to sufficient resolution - plenty of foreshock studies!
   
   Anomalous effects can be seen in the magnetosheath, for example. 1000 km resolution does not resolve all relevant EMIC waves, leading to anomalous loss-cone distributions. See e.g. `Dubart+2023 <https://doi.org/10.1063/5.0176376>`_ for ongoing work towards a subgrid diffusion model to mimic the effects of these waves.

#. Spatial extents

   Outflow boundaries are simple copy-condition boundaries. For example, the bow shock hitting the outer walls should be avoided, leading to approx. +- 60 RE simulation extents for the Earth.

What can I do?
--------------

Let's see what *has* been done.

* ULF wave field studies, see `Turc et al., 2022 <https://doi.org/10.1038/s41567-022-01837-z>`_, Transmission of foreshock waves through Earth’s bow shock. *Nat. Phys*.

  5D/2D runs - can resolve ion kinetic scales. Topics include generation of counterstreaming foreshock populations, resulting ULF wave fields, and their effects!

  Similar runs are now being run at O(10M) CPUh on Mahti (CSC/Finland). Smaller 2D runs have been nowaways performed also on our local cluster of 10 nodes of 2x AMD Epyc 7302/32 cores per node.

* Relatedly: Jets and SLAMS, see the works by Joonas Suni, e.g., `Suni et al., <https://doi.org/10.1029/2021GL095655>`_

* Reconnection in a global context `Palmroth et al. 2023 <https://doi.org/10.1038/s41561-023-01206-2>`_, Magnetotail plasma eruptions driven by magnetic reconnection and kinetic instabilities. *Nat. Geosci*.

  These are huge runs at several tens of MCPU-hours.

  Ion kinetics make the reconnection phenomena very dynamic, presenting need for more tools for finding them. See `Alho et al., 2023 (revised) <https://doi.org/10.5194/egusphere-2023-2300>`_

* Directly utilize the VDF data of the global simulations, e.g. in precipitation of particles from magnetospheric processes, both from 2D (`Grandin et al. 2019 <https://doi.org/10.5194/angeo-37-791-2019>`_) and 3D simulations (`Grandin et al. 2023 <https://doi.org/10.1051/swsc/2023017>`)

* Local ion-kinetic simulations, e.g. Kelvin-Helmholz instabilities (Tarvus et al, in prep.), EMIC wave studies (`Dubart et al. 2023 <https://doi.org/10.1063/5.0176376>`_, with *many* small simulations), shock tube simulations (YPK)... More discussion on Vlasiator projects later.

See the `Vlasiator website/publications <https://www.helsinki.fi/en/researchgroups/vlasiator/publications-and-presentations>`_ for more examples!

We note that since these runs are expensive, we often mine multiple papers out of a single run.


Rules of the Road
=================

As noted at the `Vlasiator website <https://www.helsinki.fi/en/researchgroups/vlasiator/rules-of-the-road>`_.

*Vlasiator is a significant investment, and its development has taken many years (since 2008).*

Vlasiator is funded by the European Research Council and the Research Council of Finland.

Vlasiator requires considerable amount of human resources. The code is being developed by external funding. Runs are carried out with supercomputer resources that the PI team applies for from competitive sources (such as PRACE and CSC Grand Challenge). Each run needs to be babysat.

While Vlasiator is licensed under GPL-2, these rules of the road have a similar philosophy as are generally in use for instruments. Vlasiator is the only one of its kind in the world, having no similar benchmark. Hence we need to make sure that all Vlasiator results have been verified by by the PI-team.

The user is strongly advised to utilise Vlasiator as described below.

PI and the PI-team
------------------

The PI-team makes all decisions pertaining to the Vlasiator master version. All data requests and other support questions should be addressed to the PI. The PI-team decides about the time and place in which the peer-reviewed data becomes public.

Vlasiator enthusiasts
---------------------

The PI-team welcomes collaborations! Do reach out to us and make a data request, which we handle on the best effort basis. Any publications or presentations need to follow the publication rules below, and the further distribution of the accessed data is not allowed without the consent of the PI-team. The movies made public through the Vlasiator web pages can be freely used in scientific work, presentations and publications, bearing in mind the publications rules of the road below.

Publications and presentations
------------------------------

All publications or presentations showing Vlasiator data need to be inspected by someone from the Vlasiator PI-team. The PI and the relevant PI-team members shall be added as co-authors in the publication. The Vlasiator PI-team may publish the Vlasiator data shown in the publication through the Vlasiator web page.

Acknowledgement for publications and presentations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Vlasiator is developed by the European Research Council Starting grant 200141-QuESpace, and Consolidator grant GA682068-PRESTISSIMO received by the Vlasiator PI. Vlasiator has also received funding from the Academy of Finland. See www.helsinki.fi/vlasiator

Presentations
^^^^^^^^^^^^^

All presentations showing Vlasiator data shall include a Vlasiator slide given by the PI-team. The presentation shall also include the Vlasiator logo. The slide and acknowledgement are available from the PI time upon request.

Publications
^^^^^^^^^^^^

All publications showing Vlasiator data shall cite these two Vlasiator architectural papers:

Enabling technology for global 3D+3V hybrid-Vlasov simulations of near Earth space, U. Ganse, T. Koskela, M. Battarbee, Y. Pfau-Kempf, K. Papadakis, M. Alho, M. Bussov, G. Cozzani, M. Dubart, H. George, E. Gordeev, M. Grandin, K. Horaites, J. Suni,
V. Tarvus, F. Tesema Kebede, L. Turc, H Zhou, and M. Palmroth. Physics of Plasmas 30, 042902 (2023)
`<https://doi.org/10.1063/5.0134387>`_

Palmroth, M., Ganse, U., Pfau-Kempf, Y., Battarbee, M., Turc, L., Brito, T., Grandin, M., Hoilijoki, S., Sandroos, A., and von Alfthan, S., "Vlasov methods in space physics and astrophysics", Living Rev Comput Astrophys., 4:1, `<doi:10.1007/s41115-018-0003-2>`_, 2018.


Additional informative technological publications:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Parametrization of coefficients for sub-grid modeling of pitch-angle diffusion in global magnetospheric hybrid-Vlasov simulations, M. Dubart, M. Battarbee, U. Ganse, A. Osmane, F. Spanier, J. Suni, G. Cozzani, K. Horaites, K. Papadakis, Y. Pfau-Kempf, V. Tarvus, and M. Palmroth, Physics of Plasmas 30, 123903 (2023)
https://doi.org/10.1063/5.0176376

Spatial filtering in a 6D hybrid-Vlasov scheme for alleviating AMR artifacts: a case study with Vlasiator, versions 5.0, 5.1, 5.2.1, K. Papadakis, Y. Pfau-Kempf, U. Ganse, M. Battarbee, M. Alho, M. Grandin, M. Dubart, L. Turc, H. Zhou, K. Horaites, I. Zaitsev, G. Cozzani, M. Bussov, E. Gordeev, F. Tesema, H. George, J. Suni, V. Tarvus, and M. Palmroth. Geosci. Model Dev., 15, 7903–7912 (2022)
https://doi.org/10.5194/gmd-15-7903-2022

Vlasov simulation of electrons in the context of hybrid global models: an eVlasiator approach, M. Battarbee, T. Brito, M. Alho, Y. Pfau-Kempf, M. Grandin, U. ganse, K. Papadakis, A. Johlander, L. Turc, M. Dubart, and M. Palmroth. Ann. Geophys. 39, 85–103 (2021)
https://doi.org/10.5194/angeo-39-85-2021

Vlasiator: First global hybrid-Vlasov simulations of Earth's foreshock and magnetosheath, S. von Alfthan, D. Pokhotelov, Y. Kempf, S. Hoilijoki, I. Honkonen, A. Sandroos, M. Palmroth. Journal of Atmospheric and Solar-Terrestrial Physics, Volume 120, December 2014, Pages 24-35, https://doi.org/10.1016/j.jastp.2014.08.012



Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------


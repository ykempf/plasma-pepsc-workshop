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
=========

`**Vlasiator** <https://www.helsinki.fi/en/researchgroups/vlasiator>`_ (`GitHub <https://github.com/fmihpc/vlasiator>`_) is the state-of-the-art hybrid-Vlasov simulation for ion-scale physics in a global magnetospheric setting. It is the only 6D hybrid-Vlasov code capable of simulating the Earth's magnetosphere. In Vlasiator, ions are represented as velocity distribution functions, while electrons are massless charge-neutralizing fluid, enabling a self-consistent global plasma simulation that can describe multi-temperature plasmas to resolve non-MHD processes that currently cannot be self-consistently described by the existing global space weather simulations. The novelty is that by modelling ions as velocity distribution functions the outcome will be numerically noiseless. Due to the multi-dimensional approach at ion scales, Vlasiator's computational challenges are immense.

.. figure:: img/BCH_LRCA.webp
    :width: 500
    :alt: Example of a Vlasiator 5D run (LRCA)
    
    A Vlasiator view of the Earth's magnetosphere (5D, Palmroth+2018)



Vlasiator simulates the dynamics of plasma using a hybrid-Vlasov model, where protons are described by their distribution function f(r,v,t) in ordinary (r) and velocity (v) space, and electrons are a charge-neutralising fluid. This approach neglects electron kinetic effects but retains ion kinetics. The time-evolution of f(r,v,t) is given by Vlasov's equation,

.. image:: img/vlasov-eq.webp
    :width: 400
    :alt: Vlasov's equation

which is coupled self-consistently to Maxwell's equations giving the evolution of the electric and magnetic fields E and B. Maxwell's equations neglect the displacement current.

.. image:: img/faraday.png
    :width: 200
    :alt: Faraday's law

,

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

    Example of sparse velocity grid, YPK 2016.

The numerical algorithm for the propagation of the Vlasov equation is based on operator splitting: spatial translation and velocity-space acceleration are leapfrogged. Spatial translation remaps the VDF as 1D shears. The acceleration re-mapping of the VDF is handled by the semi-Lagrangian SLICE-3D method by Zerroukat and Allen (2012), by decomposing v-space rotation and translation to a series of shear operations. These mappings are conservative by themselves.

Spatial AMR has lately enabled truly 6D simulations of the Earth's magnetosphere (see Ganse+2023). The initial 6D production runs have used statically-refined grid, with a dynamic AMR currently being tested in production.

Spatial AMR, however, is *not* extended to the field solver (*heterologous* grids): Field solver has simple load balancing, while the Vlasov solver does not. The solution is to have *two* grids, with the field solver grid at the highest resolution of the Vlasov grid, throughout the entire domain. There are some details in cross-coupling e.g. plasma moments across these grids. With four levels of refinement, the field solver is contributing about 10% of runtime as it is - Vlasov solver is still the bottleneck.

Recently, we have also included a proper ionospheric inner boundary condition, with an ionosphere solver along the lines of MHD solvers. Further developments are ongoing, incl. better ionization and conductivity profiles. Outer boundary conditions now include the possibility of time-varying solar wind parameters.

Deploying Vlasiator to various environments has lately (with Plasma-PEPSC!) been made much easier, including compilation on ARM. We'll look at the build process later!

Practical aspects of running Vlasiator
--------------------------------------

What sorts on constraints does Vlasiator have?

Six-dimensional simulations are expensive! Further, there are some constraints from physics on resolution - if you want to be accurate, you will need to resolve some scales.

#. Timestep: Ion cyclotron frequency.
   
   Especially restrictive with global magnetospheric simulations with high magnetic field values close to the poles, with an r^-3 dependence.

   We constrain the timestep to provide a maximum of 22 degrees of cyclotron rotation per step.

#. Velocity-space resolution: numerical heating

   Low velocity-space resolution is constrained by thermal velocity: dv ~< v_th/3. For exampe, solar wind Maxwellians exhibit numerical heating for dv >~ v_th/3.

#. Velocity-space sparsity threshold

   Around 10^-15 m^6 s^-3 has been found a decent compromise for the sparsity threshold, retaining the parts of VDFs that are relevant for the dynamics of the system. If you wish to model high-energy tails, the threshold

#. Velocity-space extents

   +- 4000...8000 km/s are decent extents for terrestrial magnetospheric simulations with the current sparsity thresholds. Usually VDFs 'hit the walls' only when there is anomalous acceleration, or otherwise very fast and/or hot flows. This results in 200..400 velocity cells per dimension in our usual runs. Sparsity really saves on the memory footprint!

#. Spatial resolution

   Preferably, ion kinetic scale should be resolved (~200 km in Earth's magnetosphere). In 6D global production runs, we have not yet reached this (max resolution 1000 km). See e.g. `Dubart+2023 <https://doi.org/10.1063/5.0176376>`_ for ongoing work on the topic.

#. Spatial extents

   Outflow boundaries are simple copy-condition boundaries. For example, the bow shock hitting the outer walls should be avoided, leading to approx. +- 60 RE simulation extents for the Earth.




Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------

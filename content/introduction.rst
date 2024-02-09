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



The equations are closed by a generalised Ohm's law including the Hall term (and the electron pressure term).

.. image:: img/ohm.webp
    :width: 300
    :alt: Vlasov's equation





State-of-the-art
----------------

Vlasiator is parallelized at multiple scales via MPI, threading support and vectorization, and we are continuously improving the performance and the feature set. GPU porting is in progress: solvers have been ported, but they need to be optimized for GPUs to be useful in production.





Other practical aspects
-----------------------



Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------

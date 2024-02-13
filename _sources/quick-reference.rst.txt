Quick Reference
===============

Reference cards sorted by topic.


Adaptive Mesh Refinement cfg
----------------------------

All parameters under ``[AMR]``

* ``max_spatial_level``: Maximum AMR level for both static and adaptive refinement
* ``refine_radius``: Maximum distance from origin to refine cells, default unlimited. On static refinement this should be less than gridbuilder.x_min to avoid tail box refinement on the back wall.
* ``adapt_refinement``: Set true to use adaptive refinement
* ``use_alpha1``: Use the maximum of dimensionless gradients as a refinement index, default true (is used if adapt_refinement is set)
* ``use_alpha2``: Use J/B_perp (measuring current sheets) as a refinement index, default true (is used if adapt_refinement is set)
* ``alpha1_refine_threshold``, ``alpha_2_refine_threshold``: Minimum values of alpha to refine a cell, default 0.5
* ``alpha1_coarsen_threshold``, ``alpha_2_coarsen_threshold``: Maximum values of alpha to coarsen a cell, default half of refine threshold
* ``refine_cadence``: Adapt refinement in the grid every N load balances, default 5 (so every 5th load balance)
* ``refine_after``: Minimum time to start refinement, allows you to initialize the grid on minimal refinement. Default 0, i.e. no minimum time
* ``alpha1_dX_weight``: Multiplier for each constituent variable in the calculation of alpha1, default 1.

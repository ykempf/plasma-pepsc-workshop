VisIt and VLSV bootcamp
=======================

Why we teach this lesson
------------------------

`VisIt <https://visit-dav.github.io/visit-website/index.html>`_ is a scalable 3D-visualization software, suitable for supercomputing environments. It also has a home-brewed plugin to read and plot .vlsv files, which is why we prefer using it over similar alternatives such as ParaView. In this lesson, we look at configuring a VisIt client-server on LUMI, using VisIt and the .vlsv plugin for data exploration in 3D. VisIt and VLSV plugin are pre-installed on the LUMI workspace.


Intended learning outcomes
--------------------------

* Using a client-server with VisIt.
* Basic exploration of .vlsv files
  
  * SpatialGrid
  * FsGrid
  * Finding stored VDFs
* Plotting fieldlines and streamlines
* Plotting contours
* vlsvextract and plotting a VDF
  
Maybe:

* Compiling and installing the .vlsv plugin


Timing
------

Wednesday morning

Preparations for the exercises
------------------------------

If you haven't yet done so, please:

#. Install `VisIt 3.3 <https://visit-dav.github.io/visit-website/releases-as-tables/#series-33>`_ locally.
#. Download `host_lumi_pepsc.xml <https://github.com/ENCCS/plasma-pepsc-workshop/raw/main/content/visit/host_lumi_pepsc.xml>`_ and place it into your local ``$HOME/.visit/hosts``
#. Open VisIt, go to Options - Host profiles.. and change the Account to your username under the lumi-pepsc host.
#. From options, click ``Save settings`` so the username is saved to your config.

Feel free to get to know the `VisIt manuals<https://visit-sphinx-github-user-manual.readthedocs.io/en/develop/getting_started/index.html>`_ as well!


The hands-on
------------

#. Launch your local VisIt

VisIt produces a plentiful amount of windows.
   
The main one (``gui``) is the tall one with plotting tools, from database list on the top, a time slider, and a plotting pipeline window, currently empty.

The other one you encounter by default is the ``viewer`` window. This will render your plots and let you navigate them - see the toolbar on the top for navigation, zooming, saving viewpoints, etc. You can have multiple windows as well, and there are handy layout buttons available.

Launching to client-server
^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Click "Open"
#. Choose *Host* ``lumi-pepsc``, as given by the host configuration

   * This opens a VisIt metadata server on the frontend.

#. Navigate *Path* to ``/pfs/lustrep2/scratch/project_465000693/example_runs/Mercury5D/bulk``
#. With file grouping at on/smart, open the bulk files as a database
#. A *Compute engine launch* prompt appears. Launch one on ``small``, adjust cpu counts if needed.

   * Might take a bit to queue... 
   * A larger number of cores helps esp. with loading data from the .vlsv files!


While we wait a bit...
^^^^^^^^^^^^^^^^^^^^^^

VisIt works by handling 3D data in pipelines, with two noteworthy concepts. Firstly, we can consider the mesh: the spatial structure that tells us where we have data, and how these data points are connected. In other words, this contains the geometry and topology of the dataset. We can extract new meshes from the existing ones via geometric operations, such as slicing. These operations can also be chained, and at the end we choose what data we actually want show on the mesh at the end of the pipeline. We'll see plenty of examples soon!


First plots
^^^^^^^^^^^

Mostly, we'll be using pseudocolor plots. Let's get a feel for the 2D dataset!

#. Set the time slider to the end
#. Add a Pseudocolor plot -> ``proton/vg_rho`` to get the proton number density
#. Notice we have now the full domain plotted - including the 3rd dimension, which is included even in the 2D/5D runs.

.. figure:: visit/2d_0_rho.png
   :width: 600



#. Select the plot and use the Operator button, navigate to Slicing -> Slice

   * Double-click on the new operator in the pipeline menu.
   * De-select "Project to 2D"
   * Set Normal axis as Z, with intercept at 0
   * Click Apply in the dialog
   * Click Draw in the main window!

.. figure:: visit/2d_1_slice.png
   :width: 600

Double-clicking on the operators or or the plots opens attribure windows for those objects. Feel free to e.g. adjust the Pseudocolor colormaps or variable ranges from Pseudocolor attributes!


.. Let's dive a bit deeper.

.. #. Change the pseudocolor variable to ``fg_b_magnitude`` by right-clicking on the plot (or from the Variable button)
.. #. Double-click the Pseudocolor plot to access Pseudocolor plot settings, change to Log scale and click Apply
.. #. Right-click on the plot and click Clone
.. #. New plot! Let's change the variable to ``vg_b_vol_magnitude``

.. Now, these look slightly different - note that ``fg_b`` lives on the fieldsolver grid. This is the primary, actually face-centered quantity. ``vg_b_vol``, instead, is a volumetric average over the spatial cell. Looking at ``fg_b`` is actually wrong like this, since the different components of the B vector live on different faces of the fsgrid cell! Useful when you want to e.g. diagnose the run or in restarts, but otherwise cell-centered volumetric variables are the way to go!

Let's identify the system boundaries next.

Vlasiator boundaries
^^^^^^^^^^^^^^^^^^^^^^^^^

#. Set the pseudocolor variable to ``vg_boundarytype``.

.. figure:: visit/2d_2_boundary.png
   :width: 600

Let's compare that to the `sysboundarytype enum <https://github.com/fmihpc/vlasiator/blob/676f26a5e74c4c2b40e6d5e3294c413da0157ac3/common.h#L450>`_:

.. code-block:: c++

  namespace sysboundarytype {
    enum {
        DO_NOT_COMPUTE,   /*!< E.g. cells within the ionospheric outer radius should not be computed at all. */
        NOT_SYSBOUNDARY,  /*!< Cells within the simulation domain are not boundary cells. */
        IONOSPHERE,       /*!< Ionospheric current model. */
        OUTFLOW,          /*!< No fixed conditions on the fields and distribution function. */
        MAXWELLIAN,       /*!< Set Maxwellian boundary condition, i.e. set fields and distribution function. */
        COPYSPHERE,       /*!< A sphere with copy-condition for perturbed B as the simple inner boundary */
        OUTER_BOUNDARY_PADDING, /*!< These cells only occur on FSGrid, where boundaries are not at the highest refinement level */
        N_SYSBOUNDARY_CONDITIONS
    };
  }

We find here the ``COPYSPHERE`` (5) boundary and ``DO_NOT_COMPUTE`` (1) cells covering the planet, approximately, as the inner boundary. Then, we can focus on the actual simulation domain:

#. Add an operator to the plot: Selection -> threshold
#. Open the threshold window, remove the "default" variable
#. Add ``vg_boundarytype`` as a threshold variable, set min and max to 1 (``NOT_SYSBOUNDARY``)
#. Click apply

.. figure:: visit/2d_3_threshold.png
   :width: 600

Now you can change the variable to e.g. ``proton/vg_rho``, without system boundaries confounding the plot.

.. Contours
.. ^^^^^^^^
.. .. okay, the shock is pretty parallel so maybe nots let do this for now.
.. Let's add a bowshock proxy. Right-click on the  Add a pseudocolor plot of some variable, (maybe slice it on Z=0), and add a Slicing-> Isocontour operator. In the Isocontour operator, select levels by value, and let's choose a suitable density value. Apply and draw.

Vector plots
^^^^^^^^^^^^

Let's look at the vector plot type. Add one of ``vg_b_vol``, and click Draw. This probably looks very empty:

.. figure:: visit/2d_4_vector.png
    :width: 600

Let's go to Vector plot attributes, Geometry tab, and unselect Scale by magnitude, Apply:

.. figure:: visit/2d_5_vector.png
    :width: 600

Picking
^^^^^^^

Let's see how to find an interesting cell and its CellID with VisIt.

Let's use the plot of ``proton/vg_rho`` as a reference value slice in the background. Add another pseudocolor plot of ``vg_f_saved``, and add a Threshold operator to diplay only cells with vg_f_saved = 1. Draw, and we should have cells with VDFs stored visible on top of the background slice.

.. figure:: visit/2d_6_fsaved.png
    :width: 600

Zoom in to the foreshock, select the Zonal pick operator, and click on a cell that looks like it could have interesting dynamics:

.. figure:: img/visit_pick.png
    :width: 200

    Pick operators in the VisIt viewer. Z for zonal, N for nodal. S for spreadsheet.

The following Pick window should open, showing the picked coordinates and the plotted variable.

.. figure:: img/visit-pick-window-default.png
    :width: 400

That is not yet very useful. Adding ``CellID`` to the query variables helps! We should get a large-ish number, like 332776.

Going 3D 
--------

Let's add a dimension to our plotting, and inspect one of these VDFs. The file ``/scratch/project_465000693/example_runs/Mercury5D/velgrid.332776.0000122.vlsv`` contains an extracted VDF (with ``vlsvextract``) from the foreshock area, open it, and add a new window!

.. figure:: visit/new_window.png
   :width: 300


Let's start by plotting the full proton v-space mesh: Pseudocolor->proton

.. figure:: visit/vdf_0_pseudocolor.png
   :width: 600

This is now the outer edge of the VDF. We need to do something else if we want to have a look inside. Let's add a Threeslice operator and Draw again.

.. figure:: visit/vdf_1_threeslice.png
   :width: 600

Quite a bit of structure there! But we still have the blocky v-space halo with values below the threshold. Let's add an aptly-named thresholding operator:

.. figure:: visit/vdf_2_threshold.png
   :width: 600

Slices are good, but what if we want to have a more thorough view of the 3D structure of the VDF? Let's remove the Threeslice operator from the plot, and draw. Now that we still have the threshold operator, we should see the outer edge of the VDF at the threshold value.

.. figure:: visit/vdf_3_just_threshold.png
   :width: 600

Try adjusting the threshold value e.g. to ``1e-13``!


A proper 3D run
^^^^^^^^^^^^^^^

Next, let's see what one of our old low-resolution 3D tests looked like. Open the database at ``/scratch/project_465000693/example_data/EGE``.

Let's start by getting a quick overview with a pseudocolor plot of ``proton/vg_rho`` once more, and add a threeslice operator.

.. figure:: visit/3d_0_threeslice.png
   :width: 600


Streamline plots
^^^^^^^^^^^^^^^^

Let's add some fieldlines! These are produced in VisIt through an IntegralCurve system, which can be a bit hard to get into. Add a new pseudocolor plot with the *variable*: operators->IntegralCurve->vg_b_vol:

.. figure:: visit/3d_1_integralcurves.png
   :width: 600

Double-clicking on the integralcurve operator let's you adjust the seeding of the lines. Let's do something like the following - a spherical region with some radius of ~5e7 meters:

.. figure:: visit/3d_2_integralcurves.png
   :width: 600



.. Queries
.. ^^^^^^^

.. Let's do some quick statistics on the ULF foreshock/some other box. Select the background plot of ``proton/vg_rho``, clone it by right-clicking on it and selecting clone. Add a box operator to the cloned plot: Selection->Box. Set Box extents to cover some part of the foreshock, apply. Plot is now constrained to the given box.

.. Now, with this plot active, open Controls->Query. Navigate to Variable statistics and press query. Printout will now show statistics of the variable in the box.




Other practical aspects
-----------------------

VisIt may crash from time to time. Save your session often!

There are plenty of levers and clever tricks to pull in VisIt, this is really just scratching the surface in a short time.



Typical pitfalls
----------------

Forgetting to click ``Apply`` or ``Draw`` buttons.

Not noticing the small button with arrows to display 

Not saving your session often.


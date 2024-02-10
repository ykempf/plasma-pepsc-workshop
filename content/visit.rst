VisIt and VLSV bootcamp
=======================

Why we teach this lesson
------------------------

Configuring VisIt client-server on LUMI, using VisIt and the .vlsv plugin for data exploration in 3D. VisIt and VLSV plugin are pre-installed on the LUMI workspace.


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

Preparing exercises
-------------------

If you haven't yet done so, please:

#. Install VisIt 3.3 locally
#. Download host_lumi_pepsc.xml and place it into your local ``$HOME/.visit/hosts``
#. Open VisIt, go to Options - Host profiles.. and change the Account to your username under the lumi-pepsc host.
#. From options, click ``Save settings`` so the username is saved to your config.


The hands-on
------------

Launching to client-server
^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Launch your local VisIt
#. Click "Open"
#. Choose *Host* ``lumi-pepsc``, as given by the host configuration

   * This opens a VisIt metadata server on the frontend.

#. Navigate *Path* to ``/pfs/lustrep2/scratch/project_465000693/example_runs/Mercury5D/bulk``
#. With file grouping at on/smart, open the bulk files as a database
#. A *Compute engine launch* prompt appears. Launch one, adjust cpu counts if needed.

   * Might take a bit to queue... 
   * A larger number of cores helps esp. with loading data from the .vlsv files!

First plots
^^^^^^^^^^^

Mostly, we'll be using pseudocolor plots. Let's get a feel for the 2D dataset!

#. Add a Pseudocolor plot -> ``proton/vg_rho`` to get the proton number density
#. Notice we have now the full domain plotted - including the 3rd dimension, which is included even in the 2D/5D runs.
#. Select the plot and use the Operator button, navigate to Slicing -> Slice

   * Double-click on the new operator in the pipeline menu.
   * De-select "Project to 2D"
   * Set Normal axis as Z, with intercept at 0
   * Click Apply in the dialog
   * Click Draw in the main window!

#. Adjust the time slider, see the simulation developing!

Let's dive a bit deeper.

#. Change the pseudocolor variable to ``fg_b_magnitude`` by right-clicking on the plot (or from the Variable button)
#. Double-click the Pseudocolor plot to access Pseudocolor plot settings, change to Log scale and click Apply
#. Right-click on the plot and click Clone
#. New plot! Let's change the variable tp ``vg_b_vol_magnitude``

Now, these look slightly different - note that ``fg_b`` lives on the fieldsolver grid. This is the primary, actually face-centered quantity. ``vg_b_vol``, instead, is a volumetric average over the spatial cell. Looking at ``fg_b`` is actually wrong like this, since the different components of the B vector live on different faces of the fsgrid cell! Useful when you want to e.g. diagnose the run or in restarts, but otherwise cell-centered volumetric variables are the way to go!

Let's identify the system boundaries next.

Selection by thresholding
^^^^^^^^^^^^^^^^^^^^^^^^^

#. Set one pseudocolor to ``vg_boundarytype``.

Let's compare that to the `sysboundarytype enum <https://github.com/fmihpc/vlasiator/blob/676f26a5e74c4c2b40e6d5e3294c413da0157ac3/common.h#L450>`_`:

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

We find here the ``COPYSPHERE`` boundary and ``DO_NOT_COMPUTE`` cells covering the planet, approximately, as the inner boundary. Then, we can focus on the actual simulation domain:

#. Add an operator to the plot: Selection -> threshold
#. Open the threshold window, remove the "default" variable
#. Add ``vg_boundarytype`` as a threshold variable, set min and max to 1 (``NOT_SYSBOUNDARY``)
#. Click apply

Now you can change the variable to e.g. ``proton/vg_rho``, without system boundaries confounding the plot.

Contours
^^^^^^^^

Let's add a bowshock proxy. Add a pseudocolor plot of some variable, (maybe slice it on Z=0), and add a Slicing-> Isocontour operator. In the Isocontour operator, select levels by value, and let's choose a suitable density value. Apply and draw.

Queries
^^^^^^^

Let's do some quick statistics on the ULF foreshock. Select the background plot of ``proton/vg_rho``, and add an operator Selection->Box. Set Box extents to cover some part of the foreshock, apply. Plot is now constrained to the given box.

Now, with this plot active, open Controls->Query. Navigate to Variable statistics and press query. Printout will now show statistics of the variable in the box.


Vector plots
^^^^^^^^^^^^

Let's look at the vector plot type. Add one of ``vg_b_vol``, and click Draw. This probably looks very empty.. let's go to Vector plot attributes, Geometry tab, and unselect Scale by magnitude, Apply. 



Other practical aspects
-----------------------



Interesting questions you might get
-----------------------------------



Typical pitfalls
----------------

Coordinate Scalar Field
=======================

Functionality
-------------

This node generates a Scalar Field, the value of which at each point equals to
one of coordinates of that point. For example, this node can generate a scalar
field generated by function `S(x,y,z) = x`.

Cartesian, cylindrical and spherical coordinates are supported.

Inputs
------

This node has no inputs.

Parameters
----------

This node has the following parameter:

* **Coordinate**. The coordinate to use. The available values are:

  * **X**. Cartesian X coordinate. This option is the default one.
  * **Y**. Cartesian Y coordinate.
  * **Z**. Cartesian Z coordinate, or cylindrical Z coordinate - they are identical.
  * **Rho - Cylindrical**. Cylindrical Rho coordinate.
  * **Phi**. Cylindrical or spherical Phi coordinate - they are identical.
  * **Rho - Spherical**. Spherical Rho coordinate.
  * **Theta - Spherical**. Spherical Theta coordinate.

Outputs
-------

This node has the following output:

* **Field**. The generated scalar field.

Example of usage
----------------

This node is useful in combination with "scalar field math", "vector field math", "compose vector field" and similar nodes. For example:

.. image:: https://user-images.githubusercontent.com/284644/80824284-8e5f1380-8bf7-11ea-86e1-c7f590deb247.png


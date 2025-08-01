# VLSI CAD Assignments

Welcome to the repository for the VLSI Computer-Aided Design (CAD) assignments developed as part of the **VLSI CAD course** at **NITK Surathkal**. This repository contains Python-based solutions for **geometric layout analysis** and **Steiner tree construction** using modular, efficient, and visually rich implementations.


##  Assignment 1 – Layout Geometry Analysis

This assignment focuses on **rectangle-based layout parsing**, **spatial analysis**, and **geometric relationships**. The input is a list of rectangles defined by their coordinates. Each subproblem explores a different spatial relation:

###  Problems Solved

1. **Visualize Rectangles** – Read rectangle data and plot all shapes using `matplotlib`.
2. **Point-In-Polygon** – Determine if a user-input point lies inside one or more rectangles.
3. **Non-Overlapping Rectangles** – Identify and plot rectangles that do not overlap with any other.
4. **Partially Overlapping Rectangles** – Detect and visualize pairs of rectangles that intersect.
5. **Containment Detection** – Identify rectangles that fully contain other rectangles.
6. **Abutting Rectangles** – List and visualize rectangles that abut externally on any side.


---

##  Assignment 2 – Steiner Tree Construction & Clock Skew Optimization

This assignment involves **Steiner tree generation** using Manhattan distances for layout-aware interconnect planning. The data is a list of node coordinates.

###  Problems Solved

1. **Steiner Tree with Delay Estimation**
   - Construct a trunk to minimize wire length.
   - Compute delay using **Elmore's delay model**.
   - Plot tree, nodes, Steiner points, segment lengths, and delays.

2. **Clock Generator Placement Optimization**
   - Find a point (not necessarily on the tree) to minimize **clock skew**.
   - Recalculate tree delay from new generator location.
   - Plot the optimized structure.





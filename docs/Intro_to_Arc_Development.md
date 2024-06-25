# Introduction to Arc One Development Cycle

### How our code works
We give Cura the ArcOne.py script located in the plugins folder. Cura then runs this file and gives us variables that we store in src/arcgcode/cura/settings.py. After Cura slices an object it then runs src/arcgcode/v1/postprocessor.py. In postprocessory.py is the logic used to determine what processes need to be run on the gcode file that Cura provides. 

### The Processors
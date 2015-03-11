.. _tutorial:

Example Usage
=============

Show the processes on a Web Processing Service::

   $ export WPS_SERVICE="http://rsg.pml.ac.uk/wps/generic.cgi"
   $ birdy -h
   usage: birdy [-h] <command> [<args>]

   optional arguments:
     -h, --help            show this help message and exit

   command:
     List of available commands (wps processes)

     {temperatureConverter,oilspil,fetchMODISTimeStamp,fetchMODIS,fetchMRCS,r.colors,reprojectCoords,intersectBBOX,reprojectImage,mergeImages,compareImages,buoyGraphic,gml2svg,geotiff2png,dummyprocess,gdalinfo,ncdump,reducer,taverna,WCS_Process,NetCDF2JSON,json2plot}
                        Run "birdy <command> -h" to get additional help.   


Show help for a dummyprocess::

   $ birdy dummyprocess -h
   usage: birdy dummyprocess [-h] --input2 [INPUT2] --input1 [INPUT1]
                             [--output {output2,output1}]

   optional arguments:
     -h, --help            show this help message and exit
     --input2 [INPUT2]     Input2 number
     --input1 [INPUT1]     Input1 number
     --output {output2,output1}
                        Output: output2=Output2 subtract 1 result (default:
                        output)output1=Output1 add 1 result (default: output)


Execute dummyprocess::

   $ birdy dummyprocess --input1 1 --input2 3 --output output1
   Execution status: ProcessAccepted
   Execution status: ProcessSucceeded
   Output URL=http://earthserver.pml.ac.uk/wps/wpsoutputs/output1-cf94c9ea-7982-11e4-8e10-d4ae52675c92



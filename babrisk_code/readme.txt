This note explains the steps to re-construct the dataset used in: Stomper A., Radwanski J.; Babylonian Risk Aversion; from the Excel file available online via Prof. Van der Spek's website (http://www.iisg.nl/hpw/babylon.php).

The main Python script is: constructing_the_dataset.py. It depends upon the modules: pandas, numpy, openpyxl, xlrd, and jdcal. These need to be installed before running the script.

Make sure that the working directory of your editor is set to the location of the main script.

Prior to running the main script, you should:
- Download babylonia.xls from http://www.iisg.nl/hpw/babylon.php and save in OriginalData folder.
- Open babylonia.xls with Excel and save as babylonia.xlsx, in the same folder.
- Run run_first.py, which computes and writes data quality indicator variables into babylonia.xlsx.

In order to generate the Excel file: final_dataset.xlsx, on which we perform the analysis in the paper, one needs to re-run the main script (constructing_the_dataset.py) several times, commenting/uncommenting certain blocks. Each time, a single dataset is created, based on a product of two rules: (1) the way observations are mapped to parts of month, (2) which observations are retained based on data quality considerations. The choice of the rules is defined in lines 149-153, where exactly one line should be uncommented at a time. On a final run, all output can be merged and saved. More concretely, the steps to re-create our dataset are:

1. Comment out the block 248-266.
2. Uncomment lines 150 and 238-239, comment all other lines 150-153. Run the script. This should create files: dataset__PT1_ALL.pkl and fixed.pkl in the working directory. Comment out 238-239.
3. Uncomment line 151, comment all other lines 150-153. Run the script to produce file: dataset__PT1_NIT.pkl in the working directory.
4. Uncomment line 152, comment all other lines 150-153. Run the script to produce file: dataset__PT0_ALL.pkl in the working directory.
5. Uncomment line 153, comment all other lines 150-153. Run the script to produce file: dataset__PT0_NIT.pkl in the working directory.
6. Keeping any of lines 150-153 uncommented, uncomment the block 248-266. Run the script to produce the merged final dataset. 

More comments are given in the main script file.
   
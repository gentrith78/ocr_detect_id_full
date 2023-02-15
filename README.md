# ocr_detect_id_full

Requirements:
- Create GUI that allows user to selecect input and output folder and to start the program
- In the input folder, script should search for images inside subfolders
- Script should detect new files that will be inputed and run the program when it detects new files, then it should save each file name into a db in order to be able to identify the new files from the old or processed ones.
- Script should save each file inito output folder with another folder created with the extraced id as name.
- Whenever there is a new file processed/extracted ocr, the script should search into the local database if the content of this file already exists into database and if it exist then it will mark as already processed and will not save it also it will remmove from input folder.

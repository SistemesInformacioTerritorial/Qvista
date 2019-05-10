import filecmp 


# def print_diff_files(dcmp):
#     # for name in dcmp.diff_files:
#     for name in dcmp.same_files:
#         print ("diff_file %s found in %s and %s" % (name, dcmp.left, dcmp.right))
    
#     for sub_dcmp in dcmp.subdirs.values():
#         print_diff_files(sub_dcmp)

# dcmp = filecmp.dircmp('D:/qVista/Codi/Dades/dir_ele1/', 'D:/qVista/Codi/Dades/dir_eleD:/qVista/Codi/Dades/dir_ele/') 
# print_diff_files(dcmp) 

# filecmp.cmp("D:/qVista/Codi/Dades/dir_ele1/001808.csv","D:/qVista/Codi/Dades/dir_ele/001808.csv")
# filecmp.cmpfiles("D:/qVista/Codi/Dades/dir_ele1/","D:/qVista/Codi/Dades/dir_ele/",  'common_files')
# aa=filecmp.dircmp("D:/qVista/Codi/Dades/dir_ele1/","D:/qVista/Codi/Dades/dir_ele/").diff_files
aa= filecmp.dircmp("U:/QUOTA/Comu_imi/-JNB/dir_ele1","U:/QUOTA/Comu_imi/-JNB/dir_ele").diff_files
print(aa)

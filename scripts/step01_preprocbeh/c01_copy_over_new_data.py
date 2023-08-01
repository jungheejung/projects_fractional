# %%
import glob, os, re, shutil
from pathlib import Path

# TODO:
# identify data existing in d02_preprocessed
# cross check and copy over only that doesn't exist in d02_preprocessed

# %%
current_dir = os.getcwd()
analysis_repo_dir = Path(current_dir).parents[1]
print("top dir: ".format(analysis_repo_dir))
data_repo_dir = "/Users/h/Documents/projects_local/d_beh" # USER, INSERT PATH

"""
search for folder named d_beh
copy /Users/h/Documents/projects_local/d_beh/sub-0001/task-social
into /Users/h/Documents/projects_local/social_influence_analysis/data/dartmouth/d01_rawbeh
"""

# %%
src = glob.glob(os.path.join(data_repo_dir, 'sub-*', 'task-fractional', '*'))
print(src)

# %%
for ind, src_fname in enumerate(src):
    num = re.findall('\d+', src[ind])
    print("sub: {0}".format(num[0]))
    print("src_fname", src_fname)
    print(os.path.basename(src_fname))

  
    # print(src[0])
    # print(os.path.basename(src_fname))
    dst1_fpath = os.path.join( analysis_repo_dir, 'data', 'beh', 'beh01_raw', 'sub-'+num[0])
    dst2_fpath = os.path.join( analysis_repo_dir, 'data', 'beh', 'beh02_preproc', 'sub-'+num[0])
    Path(dst1_fpath).mkdir( parents=True, exist_ok=True )
    Path(dst2_fpath).mkdir( parents=True, exist_ok=True )
    
    print("ds1 path",dst1_fpath)
    print(os.path.basename(src_fname))
    if Path(os.path.join(dst1_fpath, os.path.basename(src_fname))).is_file():
        print("file exists")
    else:
        shutil.copyfile(src_fname, os.path.join(dst1_fpath, os.path.basename(src_fname)))

    if Path(os.path.join(dst2_fpath, os.path.basename(src_fname))).is_file():
        print("file exists")
    else:
        shutil.copyfile(src_fname, os.path.join(dst2_fpath, os.path.basename(src_fname)))
        print("copying file over")



# %%

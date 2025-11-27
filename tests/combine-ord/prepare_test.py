import pandas as pd
from pathlib import Path
import numpy as np

# %% Load the exposure file
# fname='SourceLocOEDPiWind.csv'
fname='SourceLocOEDPiWind10.csv'
loc_path = Path(f"/home/vinulw/code/OasisPiWind/tests/combine-ord/full/{fname}")
output_path = loc_path.parent.parent / 'split'

loc_df = pd.read_csv(loc_path)

# %% sample

n_split = 2
n_total = len(loc_df)

idx_arr = np.arange(n_total)

rng = np.random.default_rng(seed=1234)
rng.shuffle(idx_arr)
split_idx_arr = [idx_arr[:n_total//2], idx_arr[n_total//2:]]

# %% output
for i, _idx_arr in enumerate(split_idx_arr):
    _idx_arr = np.sort(_idx_arr)

    _output_path = output_path / f'{i+1}/{fname}'
    _output_path.parent.mkdir(parents=True, exist_ok=True)
    loc_df.iloc[_idx_arr].to_csv(_output_path, index=False)

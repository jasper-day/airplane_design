# Airplane Design Repo

This repository contains code to help design airplanes.

The code lives in the airplane_design folder. So far, these are the important files:

- airfoil.py: parse and interpret airfoil `.dat` files from [the UIUC Airfoil Coordinates Database](https://m-selig.ae.illinois.edu/ads/coord_database.html#M)
- data.py: contains ORM ([object-relational mappings](https://docs.sqlalchemy.org)) to interact with the sqlite database at design.db

# Setup

```sh
# create python virtual environment in folder `venv`
python -m venv venv
# activate the venv according to the instructions for your shell, e.g:
venv/bin/activate # most linux and mac
source venv/bin/activate.fish # fish shell
./venv/Scripts/activate # Windows powershell/cmd
# install requirements
pip install -r requirements.txt
```

# Example usage

```sh
# Launch a session from the shell:
ipython -i airplane_design/data.py
```

Then, in ipython, you can interact with the airfoil data:

```py
import matplotlib.pyplot as plt
import airfoil

# sort the airfoils by thickness
airfoils = session.scalars(select(Airfoil).order_by(Airfoil.thickness)).all()

# load the first 20 coordinates (note that data comes serialized)
coordinates = [json.loads(a.coordinates) for a in airfoils]
titles = [f"{int(100 * a.thickness)}%: {a.title}" for a in airfoils]

# plot
%matplotlib
fig,axs = plt.subplots(5,4)
airfoil.make_subplots(axs, coordinates[:20], titles[:20], 5, 4)
```

#!/usr/bin/env python

import os
import pandas as pd
from functools import reduce
from multiprocessing import Pool

# Get all topics
topic_fractions = pd.read_csv("mp_topic_fraction.csv")
topics = topic_fractions.columns[6:]

def bake_collision(topic):
    """Run nodejs script to calculate position of all MP points for a particular topic"""
    print("Computing nodes for topic: " + topic)
    return  pd.read_csv(os.popen('node compute_collision.js "{0}"'.format(topic)))

# Make a pool with 8 processes
pool = Pool(8)

# Map pool to topics to generate one dataframe per topic
dfs = pool.map(bake_collision, topics)

# Merge all dataframes in list into one, using mp id as key
df = reduce(lambda left, right: pd.merge(left, right, on="id"), dfs)

# Join MP data with baked positions and write to csv
topic_fractions[["id", "full_name", "party", "gender", "state", "district"]]\
    .join(df.set_index("id"), on="id")\
    .to_csv("baked_positions.csv", index=False, float_format='%.3f')

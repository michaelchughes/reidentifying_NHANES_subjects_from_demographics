'''

Synopsis
--------
Simulate how often we would expect a demographic-only method to be correct,
given counts of number of possible levels of each named categorical variable
such as 'age' or 'edu' or 'income', by drawing a population with uniform distribution
over each categorical variable.

Usage
-----
## What accuracy if we only used age and had 2 levels and 100 subjects?
$ simulate_acc_of_categorical_reid.py --n_subjects 100 --use_fields age --n_possible_age 2

## What accuracy if we only used age and had 100 levels and 100 subjects?
$ simulate_acc_of_categorical_reid.py --n_subjects 100 --use_fields age --n_possible_age 50

$ simulate_acc_of_categorical_reid.py --n_subjects 10000 --use_fields ALL

'''

import argparse
import numpy as np
import pandas as pd

## Num possible levels of each categorical variable.
# These are roughly consistent with NHANES dataset

FIELD_NAMES_AND_COUNTS={
    'age':60,
    'gender':2,
    'income':16,
    'edu':7,
    'race':5,
    'country_of_origin':4,
    }

def build_random_subject(
        seed=0,
        subj_uid=0,
        field_names_and_counts=FIELD_NAMES_AND_COUNTS,
        ):
    prng = np.random.RandomState(seed)
    subj_dict = dict(subj_uid=subj_uid)
    for key, n_possib in field_names_and_counts.items():
        subj_dict[key] = prng.choice(n_possib)
    return subj_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--n_subjects', type=int, default=10000)
    parser.add_argument('--seed_offset', type=int, default=0)
    parser.add_argument('--n_possible_age', type=int, default=FIELD_NAMES_AND_COUNTS['age'])
    parser.add_argument('--n_possible_income', type=int, default=FIELD_NAMES_AND_COUNTS['income'])
    parser.add_argument('--n_possible_race', type=int, default=FIELD_NAMES_AND_COUNTS['race'])
    parser.add_argument('--n_possible_edu', type=int, default=FIELD_NAMES_AND_COUNTS['edu'])
    parser.add_argument('--use_fields', type=str, default='ALL')
    args = parser.parse_args()
    use_fields = args.use_fields.split(',')
    if args.use_fields == 'ALL':
        use_fields = FIELD_NAMES_AND_COUNTS.keys()
    field_names_and_counts = dict()
    for field in use_fields:
        field_names_and_counts[field] = FIELD_NAMES_AND_COUNTS[field]
    for key, val in args.__dict__.items():
        if key.startswith('n_possible'):
            field = key[len('n_possible_'):]
            if field in use_fields:
                field_names_and_counts[field] = val
    for field, count in field_names_and_counts.items():
        print("%5s %3d possible" % (field, count))

    n_subjects = args.n_subjects
    seed_offset = args.seed_offset * n_subjects

    subj_dict_list = list()
    for subj_uid in range(n_subjects):
        subj_dict = build_random_subject(
            seed=subj_uid + seed_offset,
            field_names_and_counts=field_names_and_counts,
            subj_uid=subj_uid)
        subj_dict_list.append(subj_dict)

    my_df = pd.DataFrame(subj_dict_list)
    my_df = my_df.set_index('subj_uid')

    print(my_df.head())

    row_strs = [str(s) for s in my_df.values]
    uvals_U, counts_U = np.unique(row_strs, return_counts=True)

    n_subj_total = 0
    n_correct_total = 0
    print("How often would we expect to identify a subject by guessing?")
    for count in np.unique(counts_U):
        n_subj_with_ct = np.sum(counts_U[counts_U == count])
        n_subj_total += n_subj_with_ct
        pr_correct_per_guess = 1.0/float(count)
        est_correct_guess = n_subj_with_ct * pr_correct_per_guess
        n_correct_total += est_correct_guess

        print("count %3d cur_subj %5d cur_correct %5d | total_subj %5d total_correct %5d total_acc %.3f" % (
            count, n_subj_with_ct, est_correct_guess, n_subj_total, n_correct_total, n_correct_total/float(n_subj_total)))


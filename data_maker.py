```python
def make_batch(batch_size, max_students, max_groups, num_students, num_groups, rng):
    scale = np.linspace(0.7, 2.4, batch_size)
    r = np.arange(max_students)
    # Group-type pref
    group_type_pref = np.abs(rng.normal(0, scale, (max_groups, max_students, batch_size)) + 0.1).T # shape = (None, max_students, max_groups)
    group_type_pref /= np.expand_dims(np.max(group_type_pref, axis=-1), -1)
    group_type_pref[:, num_students:, :] = 0 # Pad attr
    group_type_pref[:, :, num_groups:] = 0 # Pad attr
    group_type_weight = 2**rng.random()-1,
    group_type_pref *= group_type_weight
    # Grade and gender
    gender = (rng.random((batch_size, max_students)) > 0.5).astype(np.int) # shape = (None, max_students)
    gender[gender == 0] = -1
    gender[num_students:] = 0 # Pad attr
    grade = rng.choice([9, 10, 11, 12], (batch_size, max_students)) / 12 # shape = (None, max_students)
    grade[num_students:] = 0 # Pad attr
    # Pairing pref
    pairing_pref = ((rng.random((batch_size, max_students, max_students))-0.4)*30).astype(np.int) # shape = (None, max_students, max_students)
    pairing_pref = np.triu(pairing_pref) # Make triangularly symmetric
    pairing_pref = pairing_pref + np.transpose(pairing_pref, (0, 2, 1))
    pairing_pref += (rng.normal(0, scale, (max_students, max_students, batch_size)).T).astype(np.int) # Add some noise
    pairing_pref[:, num_students:, :] = 0 # Pad attr
    pairing_pref[:, :, num_students:] = 0 # Pad attr
    pairing_pref[:, r, r] = 0 # Self-pairing preference is forced to be 0
    # Aggregate attrs
    student_gender_and_grade = np.stack((gender, grade), -1).astype(np.float32) # shape = (None, max_students, 2)
    student_full_attr = np.concatenate(
        (student_gender_and_grade, group_type_pref, pairing_pref), -1
    ).astype(np.float16) # shape = (None, max_students, max_students+max_groups+2)
    return (tf.convert_to_tensor(group_type_pref, dtype=tf.float32),
            tf.convert_to_tensor(student_gender_and_grade, dtype=tf.float32),
            tf.convert_to_tensor(pairing_pref, dtype=tf.float32),
            tf.convert_to_tensor(student_full_attr, dtype=tf.float32))

def make_dataset(batch_size, max_students, min_students, rng=None):
    if not rng:
        rng = np.random.default_rng()
    dataset = []
    mn_gs_r = min_students//2 - 3
    max_groups = max_students//2
    for num_students in range(min_students, max_students, 2):
        mx_gs = num_students//2
        mn_gs = num_students//min_students+2
        for num_groups in range(mn_gs, mx_gs, (mx_gs-mn_gs)//mn_gs_r):
            # Calculate group distribution standard dev at minimum
            group_extra = num_students%num_groups
            arr = np.zeros(num_groups) + 1*group_extra//num_groups
            arr[:group_extra%num_groups] += 1
            group_ideal_stdev = np.std(arr)
            # Generate batch
            (group_type_pref,
             student_gender_and_grade,
             pairing_pref,
             student_full_attr) = make_batch(batch_size, max_students, max_groups, num_students, num_groups, rng)
            dataset.append([
                num_students,
                num_groups,
                group_ideal_stdev,
                group_type_pref,
                student_gender_and_grade,
                pairing_pref,
                student_full_attr
            ])
    return dataset
import h5py

f = h5py.File("test_h5.hdf5", 'w') # create file

f.create_dataset("Fs", (1000,), dtype='i') # add sampling freq

f.create_dataset("ECG", (1, 3, 5, 7, 9,), dtype='i') # add ECG array

f.create_dataset("PP", (0, 2, 4, 6, 8,), dtype='i') # add Pulse Ples array

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os.path
import numpy as np
import h5py

from util import log

__PATH__ = './datasets/mnist'

rs = np.random.RandomState(123)


class Dataset(object):

    def __init__(self, ids, name='default',
                 max_examples=None, is_train=True, distribution=None, dimension=None):
        self._ids = list(ids)
        self.name = name
        self.is_train = is_train

        if max_examples is not None:
            self._ids = self._ids[:max_examples]

        filename = 'data.hdf5'

        file = os.path.join(__PATH__, distribution, str(dimension), filename)
        log.info("Reading %s ...", file)

        try:
            self.data = h5py.File(file, 'r+')
        except:
            raise IOError('Dataset not found. Please make sure the dataset was downloaded.')
        log.info("Reading Done: %s", file)

    def get_data(self, id):
        # preprocessing and data augmentation
        m = self.data[id]['image'].value/255. * 2 - 1
        try:
            l = self.data[id]['update'].value.astype(np.float32)
        except:
            l = self.data[id]['code'].value.astype(np.float32)
        return m, l

    def set_data(self, id, z):
        try:
            self.data[id]['update'] = z
        except:
            np.allclose(self.data[id]['update'].value, z)
        return

    @property
    def ids(self):
        return self._ids

    def __len__(self):
        return len(self.ids)

    def __repr__(self):
        return 'Dataset (%s, %d examples)' % (
            self.name,
            len(self)
        )


def get_conv_info():
    return np.array([32, 64, 128])


def get_deconv_info():
    return np.array([[100, 4, 2], [50, 4, 2], [25, 4, 2], [6, 4, 2], [1, 4, 2]])


def create_default_splits(is_train=True, distribution=None, dimension=None):
    ids = all_ids(distribution=distribution, dimension=dimension)

    num_trains = 60000

    dataset_train = Dataset(ids[:num_trains], distribution=distribution, dimension=dimension, name='train', is_train=False)
    dataset_test = Dataset(ids[num_trains:], distribution=distribution, dimension=dimension, name='test', is_train=False)
    return dataset_train, dataset_test


def all_ids(distribution=None, dimension=None):
    id_filename = 'id.txt'

    id_txt = os.path.join(__PATH__, distribution, dimension, id_filename)
    try:
        with open(id_txt, 'r') as fp:
            _ids = [s.strip() for s in fp.readlines() if s]
    except:
        raise IOError('Dataset not found. Please make sure the dat set was downloaded.')

    rs.shuffle(_ids)
    return _ids

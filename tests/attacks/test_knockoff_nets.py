# MIT License
#
# Copyright (C) IBM Corporation 2018
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import unittest

import numpy as np
import keras.backend as k

from art.attacks.extraction.knockoff_nets import KnockoffNets

from tests.utils import TestBase, master_seed
from tests.utils import get_image_classifier_tf, get_image_classifier_kr
from tests.utils import get_image_classifier_pt, get_tabular_classifier_tf
from tests.utils import get_tabular_classifier_kr, get_tabular_classifier_pt

logger = logging.getLogger(__name__)

BATCH_SIZE = 10
NB_TRAIN = 100
NB_EPOCHS = 10
NB_STOLEN = 100


class TestKnockoffNets(TestBase):
    """
    A unittest class for testing the KnockoffNets attack.
    """

    @classmethod
    def setUpClass(cls):
        master_seed(seed=1234, set_tensorflow=True)
        super().setUpClass()

    def setUp(self):
        super().setUp()

    def test_tensorflow_classifier(self):
        """
        First test with the TensorFlowClassifier.
        :return:
        """
        # Build TensorFlowClassifier
        victim_tfc, sess = get_image_classifier_tf()

        # Create the thieved classifier
        thieved_tfc, _ = get_image_classifier_tf(load_init=False, sess=sess)

        # Create random attack
        attack = KnockoffNets(
            classifier=victim_tfc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="random",
        )
        thieved_tfc = attack.extract(x=self.x_train_mnist, thieved_classifier=thieved_tfc)

        victim_preds = np.argmax(victim_tfc.predict(x=self.x_train_mnist), axis=1)
        thieved_preds = np.argmax(thieved_tfc.predict(x=self.x_train_mnist), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.3)

        # Create adaptive attack
        attack = KnockoffNets(
            classifier=victim_tfc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="adaptive",
            reward="all",
        )
        thieved_tfc = attack.extract(x=self.x_train_mnist, y=self.y_train_mnist, thieved_classifier=thieved_tfc)

        victim_preds = np.argmax(victim_tfc.predict(x=self.x_train_mnist), axis=1)
        thieved_preds = np.argmax(thieved_tfc.predict(x=self.x_train_mnist), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.4)

        # Clean-up session
        if sess is not None:
            sess.close()

    def test_keras_classifier(self):
        """
        Second test with the KerasClassifier.
        :return:
        """
        # Build KerasClassifier
        victim_krc = get_image_classifier_kr()

        # Create the thieved classifier
        thieved_krc = get_image_classifier_kr(load_init=False)

        # Create random attack
        attack = KnockoffNets(
            classifier=victim_krc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="random",
        )
        thieved_krc = attack.extract(x=self.x_train_mnist, thieved_classifier=thieved_krc)

        victim_preds = np.argmax(victim_krc.predict(x=self.x_train_mnist), axis=1)
        thieved_preds = np.argmax(thieved_krc.predict(x=self.x_train_mnist), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.3)

        # Create adaptive attack
        attack = KnockoffNets(
            classifier=victim_krc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="adaptive",
            reward="all",
        )
        thieved_krc = attack.extract(x=self.x_train_mnist, y=self.y_train_mnist, thieved_classifier=thieved_krc)

        victim_preds = np.argmax(victim_krc.predict(x=self.x_train_mnist), axis=1)
        thieved_preds = np.argmax(thieved_krc.predict(x=self.x_train_mnist), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.4)

        # Clean-up
        k.clear_session()

    def test_pytorch_classifier(self):
        """
        Third test with the PyTorchClassifier.
        :return:
        """
        self.x_train_mnist = np.reshape(self.x_train_mnist, (self.x_train_mnist.shape[0], 1, 28, 28)).astype(np.float32)

        # Build PyTorchClassifier
        victim_ptc = get_image_classifier_pt()

        # Create the thieved classifier
        thieved_ptc = get_image_classifier_pt(load_init=False)

        # Create random attack
        attack = KnockoffNets(
            classifier=victim_ptc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="random",
        )

        thieved_ptc = attack.extract(x=self.x_train_mnist, thieved_classifier=thieved_ptc)

        victim_preds = np.argmax(victim_ptc.predict(x=self.x_train_mnist), axis=1)
        thieved_preds = np.argmax(thieved_ptc.predict(x=self.x_train_mnist), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.3)

        # Create adaptive attack
        attack = KnockoffNets(
            classifier=victim_ptc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="adaptive",
            reward="all",
        )
        thieved_ptc = attack.extract(x=self.x_train_mnist, y=self.y_train_mnist, thieved_classifier=thieved_ptc)

        victim_preds = np.argmax(victim_ptc.predict(x=self.x_train_mnist), axis=1)
        thieved_preds = np.argmax(thieved_ptc.predict(x=self.x_train_mnist), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.4)

        self.x_train_mnist = np.reshape(self.x_train_mnist, (self.x_train_mnist.shape[0], 28, 28, 1)).astype(np.float32)


class TestKnockoffNetsVectors(TestBase):
    @classmethod
    def setUpClass(cls):
        master_seed(seed=1234, set_tensorflow=True)
        super().setUpClass()

    def setUp(self):
        master_seed(seed=1234, set_tensorflow=True)
        super().setUp()

    def test_tensorflow_iris(self):
        """
        First test for TensorFlow.
        :return:
        """
        # Get the TensorFlow classifier
        victim_tfc, sess = get_tabular_classifier_tf()

        # Create the thieved classifier
        thieved_tfc, _ = get_tabular_classifier_tf(load_init=False, sess=sess)

        # Create random attack
        attack = KnockoffNets(
            classifier=victim_tfc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="random",
        )
        thieved_tfc = attack.extract(x=self.x_train_iris, thieved_classifier=thieved_tfc)

        victim_preds = np.argmax(victim_tfc.predict(x=self.x_train_iris), axis=1)
        thieved_preds = np.argmax(thieved_tfc.predict(x=self.x_train_iris), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.3)

        # Create adaptive attack
        attack = KnockoffNets(
            classifier=victim_tfc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="adaptive",
            reward="all",
        )
        thieved_tfc = attack.extract(x=self.x_train_iris, y=self.y_train_iris, thieved_classifier=thieved_tfc)

        victim_preds = np.argmax(victim_tfc.predict(x=self.x_train_iris), axis=1)
        thieved_preds = np.argmax(thieved_tfc.predict(x=self.x_train_iris), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.4)

        # Clean-up session
        if sess is not None:
            sess.close()

    def test_keras_iris(self):
        """
        Second test for Keras.
        :return:
        """
        # Build KerasClassifier
        victim_krc = get_tabular_classifier_kr()

        # Create the thieved classifier
        thieved_krc = get_tabular_classifier_kr(load_init=False)

        # Create random attack
        attack = KnockoffNets(
            classifier=victim_krc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="random",
        )
        thieved_krc = attack.extract(x=self.x_train_iris, thieved_classifier=thieved_krc)

        victim_preds = np.argmax(victim_krc.predict(x=self.x_train_iris), axis=1)
        thieved_preds = np.argmax(thieved_krc.predict(x=self.x_train_iris), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.3)

        # Create adaptive attack
        attack = KnockoffNets(
            classifier=victim_krc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="adaptive",
            reward="all",
        )
        thieved_krc = attack.extract(x=self.x_train_iris, y=self.y_train_iris, thieved_classifier=thieved_krc)

        victim_preds = np.argmax(victim_krc.predict(x=self.x_train_iris), axis=1)
        thieved_preds = np.argmax(thieved_krc.predict(x=self.x_train_iris), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.4)

        # Clean-up
        k.clear_session()

    def test_pytorch_iris(self):
        """
        Third test for Pytorch.
        :return:
        """
        # Build PyTorchClassifier
        victim_ptc = get_tabular_classifier_pt()

        # Create the thieved classifier
        thieved_ptc = get_tabular_classifier_pt(load_init=False)

        # Create random attack
        attack = KnockoffNets(
            classifier=victim_ptc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="random",
        )
        thieved_ptc = attack.extract(x=self.x_train_iris, thieved_classifier=thieved_ptc)

        victim_preds = np.argmax(victim_ptc.predict(x=self.x_train_iris), axis=1)
        thieved_preds = np.argmax(thieved_ptc.predict(x=self.x_train_iris), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.3)

        # Create adaptive attack
        attack = KnockoffNets(
            classifier=victim_ptc,
            batch_size_fit=BATCH_SIZE,
            batch_size_query=BATCH_SIZE,
            nb_epochs=NB_EPOCHS,
            nb_stolen=NB_STOLEN,
            sampling_strategy="adaptive",
            reward="all",
        )
        thieved_ptc = attack.extract(x=self.x_train_iris, y=self.y_train_iris, thieved_classifier=thieved_ptc)

        victim_preds = np.argmax(victim_ptc.predict(x=self.x_train_iris), axis=1)
        thieved_preds = np.argmax(thieved_ptc.predict(x=self.x_train_iris), axis=1)
        acc = np.sum(victim_preds == thieved_preds) / len(victim_preds)

        self.assertGreater(acc, 0.4)


if __name__ == "__main__":
    unittest.main()

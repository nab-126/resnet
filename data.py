import tensorflow as tf
import numpy as np
import pickle
import cv2
from PIL import Image
import imutils

class Data(object):
    def __init__(self, data_dir, height, width, batch_size):
        if data_dir[-1] != "/":
            data_dir = data_dir + "/"
        self.data_dir = data_dir
        self.height = height
        self.width = width
        self.batch_size = batch_size


    def get_rot_data_iterator(self, images, labels, batch_size):
        dataset = tf.data.Dataset.from_tensor_slices((images, labels))
        dataset = dataset.shuffle(134000)
        dataset = dataset.batch(batch_size)
        dataset = dataset.prefetch(self.batch_size)
        return tf.compat.v1.data.make_initializable_iterator(dataset)

    def get_training_data(self):
        print("[INFO] Getting Training Data")
        #Returns the training images and labels.
        images = np.array([])
        for i in range(1,6):
            images = np.append(images, self._get_next_batch_from_file(i)[b'data'])
        return self.convert_images(images), None

    def convert_images(self, raw_images):
        #Normalizes the input images and converts them to the appropriate shape: batch_size x height x width x channels
        images = raw_images / 255.0
        images = raw_images.reshape([-1, 3, self.height, self.width])
        images = images.transpose([0, 2, 3, 1])
        return images

    def _get_next_batch_from_file(self, batch_number):
        data = self._unpickle_data("." + self.data_dir + self._get_batch_name(batch_number))
        return data

    def _get_batch_name(self, number):
        return "data_batch_{0}".format(number)

    def _unpickle_data(self, filepath):
        with open(filepath, 'rb') as data:
            dict = pickle.load(data, encoding='bytes')
        return dict

    def get_test_data(self):
        # Gets the test set from disk.
        test_batch = self._unpickle_data("../data/cifar-10-batches-py/test_batch")
        images = test_batch[b'data']
        images = self.convert_images(images)
        return images, None

    def preprocess_deprecated(self, images):
        # Rotates the images and save the labels for each rotation. 
        result = None
        for img in images:
            if result is None:
                result = np.array(np.array([img, 0]))
            else:
                result = np.vstack((result, (np.array([img, 0]))))
            for degree in [90, 180, 270]:
                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                result = np.vstack((result, (np.array([img, degree]))))
        return result[:,0], result[:,1]

    def preprocess(self, images):
    # Rotates the images and save the labels for each rotation. 
        processed_images = []
        labels = np.array([])
        for r in [0, 1, 2, 3]:
            for i in range(len(images)):
                img = np.rot90(images[i], k=r).reshape(1, 32, 32, 3)
                processed_images.append(img)
                labels = np.append(labels, r)
        return np.concatenate(processed_images), labels

    @staticmethod
    def print_image_to_screen(data):
        """
        Used for debugging purposes. You can use this to see if your image was actually rotated.
        """
        img = Image.fromarray(data, 'RGB')
        img.show()

if __name__ == "__main__":
    #You can use this for testing
    DATA_DIR = "../data/cifar-10-batches-py/"
    data_obj = Data(DATA_DIR, 32, 32, 5000)
    x, y = data_obj.get_training_data()
    xr, yr = data_obj.preprocess(x[:1000])
    print(type(xr))
    print(type(yr))
    
    
    iterator = data_obj.get_rot_data_iterator(xr, yr, data_obj.batch_size)
    x, y = iterator.get_next()
    print(y.shape)
    print(y.shape)
    print(x.dtype)
    print(y.dtype)







    
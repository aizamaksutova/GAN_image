import random
import os

import torch
import torchvision
import torchvision.transforms.functional as TF



class InMemoryArtBench10_256x256:
    def __init__(self, images):
        self.images = images

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        image = self.images[index]
        
        if image.min() < 0:
            # Convert from [-1, 1] to [0, 1]
            normalized_image = (image + 1) / 2
        else:
            # Assuming the image is already in the range [0, 1]
            normalized_image = image

        data = {'images': normalized_image}
        return data

class CatsBase:
    def __init__(self, images):
        self.images = images

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):
        image = self.images[index]
        
        if image.min() < 0:
            # Convert from [-1, 1] to [0, 1]
            normalized_image = (image + 1) / 2
        else:
            # Assuming the image is already in the range [0, 1]
            normalized_image = image

        data = {'images': normalized_image}
        return data
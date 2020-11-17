__author__ = 'hammad'
# Interface for accessing the Visual Genome dataset.

import json
import time
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import numpy as np
import copy
import itertools
import os
from collections import defaultdict
import sys
from visual_genome.utils import parse_image_data, parse_object_data

def _isArrayLike(obj):
    return hasattr(obj, '__iter__') and hasattr(obj, '__len__')


class VisualGenome:
    def __init__(self, image_annotation_file=None, object_annotation_file=None):
        # load dataset
        self.imgs, self.objects = dict(), dict()
        self.imgToAnns = defaultdict(list)
        if not image_annotation_file == None and object_annotation_file is not None:
            print('loading annotations into memory...')
            tic = time.time()
            image_data = json.load(open(image_annotation_file, 'r'))
            object_data = json.load(open(object_annotation_file, 'r'))
            assert _isArrayLike(image_data), 'annotation file format {} not supported'.format(type(image_data))
            assert _isArrayLike(object_data), 'annotation file format {} not supported'.format(type(object_data))
            print('Done (t={:0.2f}s)'.format(time.time()- tic))
            self.image_data = image_data
            self.object_data = object_data
            self.createIndex()

    def createIndex(self):
        # create index
        print('creating index...')

        objects,imgs = {},{}
        imgToAnns = defaultdict(list)
        for data in self.image_data:
            image = parse_image_data(data)
            imgs[image.id] = image
        for data in self.object_data:
            objs = parse_object_data(data['objects'])
            img_id = data["image_id"]
            if objs is None:
                try:
                    del imgs[img_id]
                except:
                    pass
                continue
            imgToAnns[img_id] = objs
            for obj in objs:
                objects[obj.id] = obj.names

        print('index created!')

        # create class members
        self.imgToAnns = imgToAnns
        self.imgs = imgs
        self.objects = objects

    def loadAnns(self, image_ids=[]):
        """
        Load anns with the specified image ids.
        :param image_ids (int array) : integer ids specifying images
        :return: anns (object array) : loaded ann objects
        """
        if _isArrayLike(image_ids):
            return [self.imgToAnns[id] for id in image_ids]
        elif type(image_ids) == int:
            return [self.imgToAnns[image_ids]]

    def loadImgs(self, image_ids=[]):
        """
        Load images with the specified image_ids.
        :param image_ids (int array)       : integer ids specifying img
        :return: imgs (object array) : loaded img objects
        """
        if _isArrayLike(image_ids):
            images =  [self.imgs[id] for id in image_ids]
        elif type(image_ids) == int:
            images =  [self.imgs[image_ids]]
        for image in images:
            image.filename = str(image.id) + '.jpg'
        return images

    def loadObjects(self, ids=[]):
        """
        Load objects with the specified ids.
        :param ids (int array)       : integer ids specifying objects
        :return: names (str)         : loaded objects
        """
        if _isArrayLike(ids):
            return [self.objects[id] for id in ids]
        elif type(ids) == int:
            return [self.objects[ids]]

    def getObjectIds(self):
        """
        Return all object Ids
        :return: ids (int array)   : integer array of objects ids
        """
        return self.objects.keys()
#!/usr/bin/python
"""
Creates the sets for uploaded photos
"""
import logging
import os
import shelve
import sys

import f2flickr.flickr as flickr
import f2flickr.configuration as configuration

SET_DESC = 'auto generated by folders2flickr'

def _creatSet(photoSet, setName, existingSets):
    """
    Creates or updates a set on flickr with the given photos.
    """
    setName = setName.replace('\\',' ')
    setName = setName.replace('/',' ')
    setName = setName.strip()
    photos = [] #real photo objects
    for photo in photoSet:
        photos.append(flickr.Photo(id = photo))

    fset = None
    unicodeSetName = setName.decode(sys.getfilesystemencoding())
    #check if set with the name exists already
    generate = 'Generating'
    for existingSet in existingSets:
        if existingSet.title == unicodeSetName:
            fset = existingSet
            logging.debug('tags2set: Found existing set %s', setName)
            generate = 'Updating'
            break
    msg = "%s set %s with %d pictures" % (generate, setName, len(photoSet))
    logging.debug(msg)
    print msg
    try:
        if(fset == None):
            logging.debug("tags2set: create set %s with photo %s",
                          setName, photos[0])
            fset = flickr.Photoset.create(photos[0], setName, SET_DESC)
            logging.debug('tags2set: created new set %s', setName)
    except Exception, ex:
        logging.error('tags2set: Cannot create set "%s"', setName)
        logging.error(str(ex))
        logging.error(sys.exc_info()[0])

    try:
        fset.editPhotos(photos)
    except Exception, ex:
        logging.error('tags2set: Cannot edit set %s', setName)
        logging.error(str(ex))
        logging.error(sys.exc_info()[0])


    logging.debug('tags2set: ...added %d photos', len(photos))
    return fset

def image2set(image):
    """
    Get the set name for a given image path
    """
    # if true, Set name is the name of the last subfolder
    onlysubs = configuration.configdict.get('only_sub_sets')
    if onlysubs.startswith('true'):
        _, setname = os.path.split(os.path.dirname(image))
    else:
        #set name is really a directory
        setname = os.path.dirname(image)
    return setname

def createSets(uploadedNow, historyFile):
    """
    Create/update all sets for the photos just uploaded
    """
    logging.debug('tags2set: Started tags2set')
    try:
        user = flickr.test_login()
        if not user.id:
            return None
        existingSets = user.getPhotosets()
    except:
        logging.error(sys.exc_info()[0])
        return None

    uploaded = shelve.open( historyFile )
    keys = uploaded.keys()
    keys.sort()
    uploadedSets = set()
    if uploadedNow is not None:
      for uploadedid in uploadedNow:
          try:
              image = uploaded[str(uploadedid)]
          except KeyError:
              continue
          uploadedSets.add(image2set(image))

    lastSetName = ''
    photoSet = []
    createdSets = set()
    setName = ''
    for image in keys:
        if image.find(os.path.sep) == -1: #filter out photoid keys
            continue
        setName = image2set(image)
        # only update sets that have been modified this round
        if setName not in uploadedSets and uploadedNow is not None:
            continue

        if (not lastSetName == setName and not lastSetName == ''):
            #new set is starting so save last
            newset = _creatSet(photoSet, lastSetName, existingSets)
            if newset:
                existingSets.append(newset)
            createdSets.add(lastSetName)
            photoSet = []
        logging.debug("tags2set: Adding image %s", image)
        photoSet.append(uploaded.get(image)[0])
        lastSetName = setName

    existing = set([setentry.title for setentry in existingSets])
    for uploadedSet in uploadedSets:
        if uploadedSet not in existing or uploadedSet not in createdSets:
            _creatSet([uploaded.get(photo)[0] for photo in keys if (
                            photo.find(os.path.sep) != -1
                            and image2set(photo) == uploadedSet)],
                uploadedSet, existingSets)
            createdSets.add(uploadedSet)

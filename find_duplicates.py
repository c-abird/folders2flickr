#! /usr/bin/env python

from pprint import pprint
import flickrapi
import f2flickr.uploadr
import pickle

api_key = f2flickr.uploadr.FLICKR["api_key"]
api_secret = f2flickr.uploadr.FLICKR["secret"]
token = f2flickr.uploadr.flickr.userToken()

flickr = flickrapi.FlickrAPI(api_key, api_secret, token=token)

tags = {}
for tag in flickr.tags_getListUserRaw().iter('tag'):
    raw = tag.find('raw').text
#    if not raw.startswith('#'):
#        continue
    clean = tag.get('clean')
#    tags[clean] = raw[1:].replace('#', ' ').encode('utf8')
    tags[clean] = raw.encode('utf8')

user_id = flickr.test_login().find('user').get('id')

photos = {}
page = 1
total = 1
while page <= total:
    rsp = flickr.people_getPhotos(
            user_id=user_id, per_page=500, extras='tags,date_taken', page=page)
    total = int(rsp.getchildren()[0].get('pages'))
    page += 1
    for photo in rsp.iter('photo'):
        photo_tags = tuple(tags.get(tag) for tag in photo.get('tags').split() if tag in tags)
        photos[photo.get('id')] = (photo.get('title'), photo.get('datetaken'), photo_tags)

datetitle_to_id = {}
for photo_id, (title, datetaken, photo_tags) in photos.iteritems():
    datetitle_to_id.setdefault((title, datetaken), list()).append(photo_id)
for (title, datetaken), list_id in datetitle_to_id.items():
    if len(list_id) <= 1:
        del datetitle_to_id[title, datetaken]

for (title, datetaken), list_id in datetitle_to_id.items():
    datetitle_to_id[title, datetaken] = [photos[photo_id][2] for photo_id in list_id]

pprint(datetitle_to_id)

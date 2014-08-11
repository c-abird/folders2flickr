#! /usr/bin/env python

from pprint import pprint
import flickrapi
import shelve
import f2flickr.uploadr

api_key = f2flickr.uploadr.FLICKR["api_key"]
api_secret = f2flickr.uploadr.FLICKR["secret"]
token = f2flickr.uploadr.flickr.userToken()

flickr = flickrapi.FlickrAPI(api_key, api_secret, token=token)

tags = {}
for tag in flickr.tags_getListUserRaw().iter('tag'):
    raw = tag.find('raw').text
    if not raw.startswith('#'):
        continue
    clean = tag.get('clean')
    tags[clean] = raw[1:].replace('#', ' ').encode('utf8')

photos = {}
page = 1
total = 1
while page <= total:
    rsp = flickr.people_getPhotos(
            user_id=flickr.test_login().find('user').get('id'),
            per_page=500, extras='tags', page=page)
    total = int(rsp.getchildren()[0].get('pages'))
    page += 1
    for photo in rsp.iter('photo'):
        for tag in photo.get('tags').split():
            if tag in tags:
                photos[photo.get('id')] = tags[tag]
                break

photos.update(dict(((v, k) for k, v in photos.iteritems())))
history = shelve.open(f2flickr.uploadr.HISTORY_FILE)
history.update(photos)
history.close()

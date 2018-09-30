# USAGE
# python bingImageParser.py --query "coke can" --output dataset/metal
# python bingImageParser.py --query "plastic water bottle" --output dataset/plastic


# import the necessary packages
from requests import exceptions
import argparse
import requests
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-q", "--query", required=True,
	help="search query to search Bing Image API for")
ap.add_argument("-o", "--output", required=True,
	help="path to output directory of images")
args = vars(ap.parse_args())

# api and constrains
API_KEY = "f140cf3df8d843a5836707af018fd1bf"
MAX_RESULTS = 200
GROUP_SIZE = 80
URL = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

# error handling
EXCEPTIONS = set([IOError, FileNotFoundError, exceptions.RequestException, exceptions.HTTPError,
	exceptions.ConnectionError, exceptions.Timeout])

# parsing variables
searchTerm = args["query"]
headers = {"Ocp-Apim-Subscription-Key" : API_KEY}
params = {"q": searchTerm, "offset": 0, "count": GROUP_SIZE}
path = args["output"] + searchTerm

# make the search
print("[INFO] searching Bing API for '{}'".format(searchTerm))
search = requests.get(URL, headers=headers, params=params)
search.raise_for_status()

# grab the results from the search, including the total number of
# estimated results returned by the Bing API
results = search.json()
estNumResults = min(results["totalEstimatedMatches"], MAX_RESULTS)
print("[INFO] {} total results for '{}'".format(estNumResults,
												searchTerm))

# initialize the total number of images downloaded thus far
total = 0

# loop over the estimated number of results in `GROUP_SIZE` groups
for offset in range(0, estNumResults, GROUP_SIZE):
	# update the search parameters using the current offset, then
	# make the request to fetch the results
	print("[INFO] making request for group {}-{} of {}...".format(
		offset, offset + GROUP_SIZE, estNumResults))
	params["offset"] = offset
	search = requests.get(URL, headers=headers, params=params)
	search.raise_for_status()
	results = search.json()
	print("[INFO] saving images for group {}-{} of {}...".format(
		offset, offset + GROUP_SIZE, estNumResults))

	# loop over the results
	for v in results["value"]:
		# try to download the image
		try:
			# make a request to download the image
			print("[INFO] fetching: {}".format(v["contentUrl"]))
			r = requests.get(v["contentUrl"], timeout=30)

			# build the path to the output image
			ext = v["contentUrl"][v["contentUrl"].rfind("."):]
			p = os.path.sep.join([path, "{}{}".format(
				str(total).zfill(8), ext)])
			print(p)

			# check if file exists
			exists = os.path.isfile(p)
			if exists:
			# Store configuration file values
				p = os.path.sep.join([args["output"] , "{}{}".format(
				str(total+"_1").zfill(8), ext)])
				f = open(p, "wb")
				f.write(r.content)
				f.close()
			else:
				f = open(p, "wb")
				f.write(r.content)
				f.close()
			# Keep presets

			# write the image to disk


		# catch any errors that would not unable us to download the
		# image
		except Exception as e:
			# check to see if our exception is in our list of
			# exceptions to check for
			if type(e) in EXCEPTIONS:
				print("[INFO] skipping: {}".format(v["contentUrl"]))
				continue

		# try to load the image from disk
		image = cv2.imread(p)

		# if the image is `None` then we could not properly load the
		# image from disk (so it should be ignored)
		if image is None:
			print("[INFO] deleting: {}".format(p))

			# more error handling stuff
			try:
				os.remove(p)
			except Exception as e:
				print("Havin issue removing this file: {}. Might not exists. ".format(p))
				continue

		# update the counter
		total += 1
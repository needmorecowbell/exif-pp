# exif-pp

This tool is used for injecting a json object into the UserComment tag in the exif content of a jpeg image. It acts as a directory monitor, waiting for new images to scan. This tool does not contain classifiers by default.  


**Usage:**

```bash
 python3 exif-pp.py [-h] [-v] [-r] [--convert] path

positional arguments:
  path             directory path to watch

optional arguments:
  -h, --help       show this help message and exit
  -v, --verbose    increase output verbosity
  -r, --recursive  search target directory recursively
  --convert        converts any png images to jpg for classification

```

**Example Embedded Json:**

```json

{
  "setting-classifier":{
        "result": ["beach", "outdoors"],
        "confidence": [".3", ".9"]
  },
  "artificial-or-photo":{
        "result": "photo",
        "confidence" : ".91"
  }
 
}

```

**Why would you use this?**

- you wanted to tag every face in your family photos, with the most likely name and pixel coordinate of the individual. You could store this information within the metadata of the image using exif-pp. 

- you are in the process of making training sets of data for machine learning, and want as much quantifiable information about the image as possible. 

- you have a large stream of images and you would like to organize/classify them in interesting ways. 

- you'd like to use this as some form of steganography within exif data






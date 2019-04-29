import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import json
import piexif
import piexif.helper
from PIL import Image

CACHE = [] #list of filenames that have already been scanned

class JPEGHandler(PatternMatchingEventHandler):

    patterns=["*.jpg","*.jgeg"]

    def write_exif(self, report, path):
        # this is where we will write our json report to the metadata of the image
        print("Writing exif...")

        image = Image.open(path)
        exif_dict = {}
        try:
            exif_dict = piexif.load(image.info["exif"])
 
            try:
                user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
                print("user_comments: "+user_comment)
            except Exception as e:
                print("No user comments")

        except Exception as e:
            print("No exif table")
            
        print("Creating comments")

        if(exif_dict):
            exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(report)
        else:
            #Make exif table if it doesnt exist
            exif_dict["Exif"] = {piexif.ExifIFD.UserComment:piexif.helper.UserComment.dump(report) }

        exif_bytes = piexif.dump(exif_dict)

        #Use pillow to write back to the image

        print("Writing report to metadata...")
        image.save(path, "JPEG", exif=exif_bytes) 
        print("Report written to image.")



    def classify_image(self, path):

        print("Running Classifiers...")
        #report = {}
        report = """
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
"""
 
        # image classifiers go here, the results from each classifier should be added with a unique key to the report dictionary

        #report["faces"] =  imageclassifier.faces(path)
        #report["isPhoto"] =  imageclassifier2.isPhoto(path)
        return report
        #return json.dumps(report)

    
    def process(self, event):
        with open(event.src_path, 'rb') as source:
            if(event.src_path not in CACHE):
                print("Processing: "+event.src_path)

                report = self.classify_image(event.src_path)
                CACHE.append(event.src_path)

                if(report): 
                    # if there are items in the dictionary, write them to the image
                    self.write_exif(report,event.src_path)
                else:
                    print("No Classifier results found")


    def on_modified(self, event):
        #print("Modified: "+event.src_path)
        self.process(event)


    def on_moved(self, event):
        self.process(event)


    def on_created(self, event):
        self.process(event)


       
       
if __name__ == '__main__':
    args = sys.argv[1:] # get target path if any
    observer = Observer()
    observer.schedule(JPEGHandler(), path=args[0] if args else '.')
    observer.start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

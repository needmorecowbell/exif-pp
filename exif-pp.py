import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import json
import piexif
import piexif.helper


CACHE = [] #list of filenames that have already been scanned

class JPEGHandler(PatternMatchingEventHandler):

    patterns=["*.jpg","*.jgeg"]

    def write_exif(self, report, image):
        # this is where we will write our json report to the metadata of the image
        print("Writing exif...")

    def classify_image(self, image):

        print("Running Classifiers...")
        report = {}

        # image classifiers go here, the results from each classifier should be added with a unique key to the report dictionary

        #report["faces"] =  imageclassifier.faces(image)
        #report["isPhoto"] =  imageclassifier2.isPhoto(image)
        return report

    
    def process(self, event):
        with open(event.src_path, 'rb') as source:
            if(event.src_path not in CACHE):
                print("Processing: "+event.src_path)
                image = source.read()
                report = self.classify_image(image)

                CACHE.append(event.src_path)

                if(report): 
                    # if there are items in the dictionary, write them to the image
                    self.write_exif(report,image)
                else:
                    print("No Classifier results found")


    def on_modified(self, event):
        #print("Modified: "+event.src_path)
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

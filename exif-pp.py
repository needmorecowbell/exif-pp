import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import json
import piexif
import piexif.helper
from PIL import Image

CACHE = [] #list of filenames that have already been scanned

class PNGHandler (PatternMatchingEventHandler):

    patterns=["*.png"]
            
    def convert(self, event):
        if(event.src_path not in CACHE):
            print("converting png to jpg: "+event.src_path)
            CACHE.append(event.src_path)
            image = Image.open(event.src_path)
            rgb_image = image.convert('RGB')
            rgb_image.save(event.src_path[:-4]+'.jpg')
            print("Image converted")



    def on_modified(self, event):
        #print("Modified: "+event.src_path)
        self.convert(event)

    def on_moved(self, event):
        self.convert(event)

    def on_created(self, event):
        self.convert(event)


class JPEGHandler(PatternMatchingEventHandler):

    patterns=["*.jpg","*.jpeg"]

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
            print("No exif")
            
        print("Creating comments...")

        if(report is not None):
            if(exif_dict):
                exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(report)
            else:
                #Make exif if it doesnt exist
                exif_dict["Exif"] = {piexif.ExifIFD.UserComment:piexif.helper.UserComment.dump(report) }

            exif_bytes = piexif.dump(exif_dict)

            #Use pillow to write back to the image
            print("Writing report to metadata...")
            image.save(path, "JPEG", exif=exif_bytes) 
            print("Report written to image.")



    def classify_image(self, path):
        print("Running Classifiers...")
        report = {}

        # image classifiers go here, the results from each classifier should be added with a unique key to the report dictionary

        #report["faces"] =  imageclassifier.faces(path)
        #report["isPhoto"] =  imageclassifier2.isPhoto(path)
        
        return json.dumps(report) if report else None

    
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
        self.process(event)

    def on_moved(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


       
       
if __name__ == '__main__':
    args = sys.argv[1:] # get target path if any
    observer = Observer()

    observer.schedule(JPEGHandler(), recursive=True, path=args[0] if args else '.')
    observer.schedule(PNGHandler(), recursive= True, path=args[0] if args else '.')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

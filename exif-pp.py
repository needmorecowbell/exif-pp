import argparse 
import logging
import sys
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import json
import piexif
import piexif.helper
from PIL import Image

CACHE = [] #list of filenames that have already been scanned

logger = logging.getLogger(__name__)

logging.getLogger('watchdog').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('piexif.helper').setLevel(logging.WARNING)

class PNGHandler (PatternMatchingEventHandler):

    patterns=["*.png"]
            
    def convert(self, event):
        if(event.src_path not in CACHE):
            logger.info("converting png to jpg: "+event.src_path)

            CACHE.append(event.src_path)
            image = Image.open(event.src_path)
            rgb_image = image.convert('RGB')
            rgb_image.save(event.src_path[:-4]+'.jpg')

            logger.debug("Image converted")


    def on_modified(self, event):
        self.convert(event)

    def on_moved(self, event):
        self.convert(event)

    def on_created(self, event):
        self.convert(event)


class JPEGHandler(PatternMatchingEventHandler):

    patterns=["*.jpg","*.jpeg"]

    def write_exif(self, report, path):
        # this is where we will write our json report to the metadata of the image
        logger.debug:("Writing exif...")

        image = Image.open(path)
        exif_dict = {}

        try:
            exif_dict = piexif.load(image.info["exif"])
 
            try:
                user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
                logger.debug("user_comments: "+user_comment)
            except Exception as e:
                logger.debug("No user comments")

        except Exception as e:
            logger.debug("No exif")
            
        logger.debug("Creating comments...")

        if(report is not None):
            if(exif_dict):
                exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(report)
            else:
                #Make exif if it doesnt exist
                exif_dict["Exif"] = {piexif.ExifIFD.UserComment:piexif.helper.UserComment.dump(report) }

            exif_bytes = piexif.dump(exif_dict)

            #Use pillow to write back to the image
            logger.debug("Writing report to metadata...")
            image.save(path, "JPEG", exif=exif_bytes) 
            logger.debug("Report written to image.")




    def classify_image(self, path):
        logger.debug("Running Classifiers...")
        report = {}

        # image classifiers go here, the results from each classifier should be added with a unique key to the report dictionary

        #report["faces"] =  imageclassifier.faces(path)
        #report["isPhoto"] =  imageclassifier2.isPhoto(path)
        
        return json.dumps(report) if report else None

    
    def process(self, event):
        with open(event.src_path, 'rb') as source:
            if(event.src_path not in CACHE):
                logger.info("Processing: "+event.src_path)

                report = self.classify_image(event.src_path)
                CACHE.append(event.src_path)

                if(report): 
                    # if there are items in the dictionary, write them to the image
                    self.write_exif(report,event.src_path)
                else:
                    logger.debug("No Classifier results found")


    def on_modified(self, event):
        self.process(event)

    def on_moved(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)


def main():
    art= '''
  ________   _______ ______      _____  _____  
 |  ____\ \ / /_   _|  ____|    |  __ \|  __ \ 
 | |__   \ V /  | | | |__ ______| |__) | |__) |
 |  __|   > <   | | |  __|______|  ___/|  ___/ 
 | |____ / . \ _| |_| |         | |    | |     
 |______/_/ \_\_____|_|         |_|    |_|     
                                               
    '''
    print(art+"Exif Post Processor\n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-r" , "--recursive", help="search target directory recursively", action="store_true")
    parser.add_argument("--convert", help="converts any png images to jpg for classification", action="store_true")
    parser.add_argument("path", help="directory path to watch")

    args = parser.parse_args()

    

    observer = Observer()

    if(args.convert):
        observer.schedule(PNGHandler(), recursive= args.recursive, path=args.path)

    observer.schedule(JPEGHandler(), recursive=args.recursive, path=args.path)


    if(args.verbose):
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s - %(message)s', level= logging.INFO)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()      

if __name__ == '__main__':
    main()


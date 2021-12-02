import argparse
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import sys
from tqdm import tqdm
import random


class visualization_data_2_html:
  def __init__(self, images_dir, labels_dir, name, save_dir, labels, random_size, only):
    self.imgDir = images_dir
    self.labDir = labels_dir
    self.name = name
    self.save_dir = save_dir
    self.labels = labels
    self.random_size = random_size
    if len(only) == 0:
      self.only = labels
    else:
      self.only = only
  
  def run(self):
    imgDir = self.imgDir
    labDir = self.labDir
    labels = self.labels
    ls_img = list(Path(imgDir).glob('**/*.jpg'))
    if self.random_size != -1:
      ls_img = random.sample(ls_img, self.random_size)
    ls_lab = list(Path(labDir).glob('**/*.txt'))
    ls_img = sorted(ls_img)
    ls_lab = sorted(ls_lab)

    no_mask = []
    mask = []
    incorrect_mask = []

    category = [[]]
    for i in range(len(labels)):
      category.append([])

    #print(ls_img)
    for i in tqdm(range(0, len(ls_img))):

      imgdir = str(ls_img[i])
      labdir = Path(labDir)
      labdir = labdir / (ls_img[i].stem+".txt")
      labdir = str(labdir)
      
      #print(str(ls_img[i]))

      f = open(labdir, "r")
      image = Image.open(imgdir)
      width, height = image.size

      for x in f:
        bouding_box_info = list(map(float, x.split(" ")))
        
        #print(bouding_box_info)
        x_min = min((bouding_box_info[1] - bouding_box_info[3]/2) * width, 0)
        y_min = min((bouding_box_info[2] - bouding_box_info[4]/2) * height, 0)
        x_max = max((bouding_box_info[1] + bouding_box_info[3]/2) * width, width)
        y_max = max((bouding_box_info[2] + bouding_box_info[4]/2) * height, height)

        bouding_box = (x_min, y_min, x_max, y_max)
        cropImg = image.crop(bouding_box)
        
        buffered = BytesIO()
        cropImg.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        img_base64 = bytes("data:image/jpeg;base64,", encoding='utf-8') + img_str
        #print(img_base64.decode("utf-8"))
        category[int(bouding_box_info[0])].append((ls_img[i].stem, img_base64.decode("utf-8")))

    print("\t")
    for i in range(len(labels)):
      if labels[i] in self.only:
        print(labels[i], len(category[i]))
        message = '<html><head></head><style>.page { max-width: 800px ; margin: auto; } img {filter: drop-shadow(0 0 0.75rem ); height: 182px ; padding-left: 28px ; padding-top: 9px ;}</style><body><div class="page"><div>'
        message = message + "<h2>Box count: " + str(len(category[i])) + "</h2>"
        fileName = ""
        for j in range(len(category[i])):
          filename, base64Str = category[i][j]
          if filename != fileName:
            message = message + '<h3>'+ filename + '</h3> <br>'
            fileName = filename
          message = message + '<img src="' + base64Str + '" alt="' + filename + '" />'

        message = message + '</div></div></body></html>'

        saveDir = Path(self.save_dir)
        fileName = self.name + "_" + labels[i] + ".html"
        saveDir = saveDir / fileName
        f = open( saveDir ,'w')
        f.write(message)
        f.close()  
    print(("check " + self.save_dir + " folder to see result."))

def parser():
    args = argparse.ArgumentParser()
    args.add_argument('--images-dir', type=str, help='specify your images path', required=True)
    args.add_argument('--labels-dir', type=str, help='specify your labels path', required=True)
    args.add_argument('--save-dir', type=str, help='specify your save path', required=True)
    args.add_argument('--name', type=str, help='specify your html file name', required=True)
    args.add_argument('--labels', nargs="+", help='list of your bounding box labels', required=True)
    args.add_argument('--random-size', type=int, default=-1, help='make number of random list from dataset')
    args.add_argument('--only', nargs="+", default=[], help='specify your list of class you want to see')
    args = args.parse_args()
    
    return args

def main(opt):
  #print(vars(opt))
  html = visualization_data_2_html(**vars(opt))
  html.run()

if __name__ == "__main__":
    main(parser())

"""

File Name: thresh_display.py
Origin: Netflora (https://github.com/NetFlora/Netflora)

"""


from ipywidgets import SelectionSlider, interact
from IPython.display import display, clear_output
from PIL import Image
import glob
import os

class ImageDisplayer:
    def __init__(self, base_dir='runs/detect', save_dir='results/imagens_threshold', thresholds=None, image_limit=5):
        self.base_dir = base_dir
        self.save_dir = save_dir
        self.thresholds = thresholds if thresholds is not None else [0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
        self.image_limit = image_limit
        
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        
        self.preprocess_and_save_all_images()

        
        self.setup_slider()

    def setup_slider(self):
        
        self.threshold_slider = SelectionSlider(
            options=[(f'{value}', value) for value in self.thresholds],
            value=self.thresholds[0],
            description='Threshold:',
            continuous_update=True,
            readout=True
        )
        interact(self.display_saved_image, threshold=self.threshold_slider)

    def preprocess_and_save_all_images(self):
        
        for threshold in self.thresholds:
            self.process_images_for_threshold(threshold)

    def process_images_for_threshold(self, threshold):
        
        image_dir = f'{self.base_dir}/{threshold:.2f}'
        images = glob.glob(os.path.join(image_dir, '*.jpg'))[:self.image_limit]
        
        if images:
            self.create_and_save_composite_image(images, threshold)
        else:
            print(f'Nenhuma imagem encontrada para threshold {threshold:.2f}.')

    def create_and_save_composite_image(self, images, threshold):
        
        size = (640, 640)
        composite_img = Image.new('RGB', (size[0] * len(images), size[1]))

        for i, img_path in enumerate(images):
            img = Image.open(img_path).resize(size, Image.Resampling.LANCZOS)
            composite_img.paste(img, (i * size[0], 0))

        composite_save_path = os.path.join(self.save_dir, f'composite_threshold_{threshold:.2f}.jpg')
        composite_img.save(composite_save_path)

    def display_saved_image(self, threshold):
        
        clear_output(wait=True)  
        composite_path = os.path.join(self.save_dir, f'composite_threshold_{threshold:.2f}.jpg')

        if os.path.exists(composite_path):
            img = Image.open(composite_path)
            display(img)
            print(f'Threshold: {threshold}')
        else:
            print(f'Nenhuma imagem composta encontrada para threshold {threshold:.2f}.')


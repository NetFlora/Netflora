"""

File Name: tiles.py
Origin: Netflora (hhttps://github.com/NetFlora/Netflora)

"""

import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import rasterio
from rasterio.windows import Window
from utils.credentials import credentials
from PIL import Image
import numpy as np
import pandas as pd
import shutil
from tqdm.notebook import tqdm
import requests
import os
import csv
import json



class TileGenerator:
    def __init__(self):
        self.verified = False
        self.attempted_verification = False
        self.crs = None
        self.specs = {
            'Açaí': {'name': 'Acai', 'size': 1536, 'overlap': 128, 'link': 'https://github.com/NetFlora/Netflora/releases/download/Assets/ACAI_Embrapa00.pt'},
            'Palmeiras': {'name': 'Palmeiras', 'size': 1536, 'overlap': 256,'link': 'https://github.com/NetFlora/Netflora/releases/download/Assets/PALMEIRAS_Embrapa00.pt'},
            'Castanheira': {'name': 'Castanheira', 'size': 2048, 'overlap': 1024, 'link': None},
            'PMFS': {'name': 'PMFS', 'size': 1536, 'overlap': 768, 'link': 'https://github.com/NetFlora/Netflora/releases/download/Assets/PMFS_Embrapa00.pt'},
            'PFNMs': {'name': 'PFNMs', 'size': 1536, 'overlap': 512, 'link': 'https://github.com/NetFlora/Netflora/releases/download/Assets/NM_Embrapa00.pt'},
            'Ecológico': {'name': 'Ecologico', 'size': 3000, 'overlap': 0, 'link': None},
        }
        self.setup_ui()
        self.verify()

    def verify(self):
        if self.attempted_verification:
            return self.verified
        self.attempted_verification = True

        try:
            with open('json/response_status.json', 'r', encoding='utf-8') as file:
                variables = json.load(file)
                if variables['status_code'] == 200:
                    self.verified = True
                
        except FileNotFoundError:
            pass
        except json.JSONDecodeError as e:
            pass
        if not self.verified:
            display(HTML('<span style="color: red;">Por gentileza, aceite o Termo de Uso!</span>'))
            display(HTML('<span style="color: orange;">Por favor, preencha os dados e rode essa cécula novamente!</span>'))
            if credentials(): 
                self.verified = True
                
                
        if self.verified:
            self.enable_ui()

    def enable_ui(self):
        """Enable UI elements after successful verification."""
        self.image_path_text.disabled = False
        self.dropdown.disabled = False
        self.button.disabled = False


    def download_model_weights(self, url, output_path):
        if url is not None:
            response = requests.get(url)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            

    def create_tiles_with_overlap_and_save_coords(self, image_path, tile_size, overlap, output_dir, csv_path):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        tile_counter = 0

        with rasterio.open(image_path) as src:
            self.crs = src.crs
            with open(csv_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['filename', 'minX', 'minY', 'maxX', 'maxY', 'crs'])

                width, height = src.width, src.height
                total_tiles = ((height - overlap) // (tile_size - overlap)) * ((width - overlap) // (tile_size - overlap))

                pbar_creation = tqdm(total=total_tiles, desc="Creating Tiles")

                for i in range(0, height, tile_size - overlap):
                    for j in range(0, width, tile_size - overlap):
                        w = min(tile_size, width - j)
                        h = min(tile_size, height - i)
                        window = Window(j, i, w, h)
                        transform = src.window_transform(window)
                        tile = src.read(window=window)

                        if np.any(tile):
                            if tile.shape[0] == 4:
                                tile_image = Image.fromarray(np.moveaxis(tile, 0, -1)).convert('RGB')
                            else:
                                tile_image = Image.fromarray(np.moveaxis(tile, 0, -1))

                            tile_filename = f'tile_{tile_counter}.jpg'
                            tile_image.save(os.path.join(output_dir, tile_filename), 'JPEG')

                            bounds = rasterio.transform.array_bounds(h, w, transform)
                            writer.writerow([tile_filename, bounds[0], bounds[1], bounds[2], bounds[3], str(self.crs)])

                            tile_counter += 1

                        pbar_creation.update(1)

                pbar_creation.close()

        pbar_verification = tqdm(total=tile_counter, desc="Processing Tiles")
        for _ in os.listdir(output_dir):
            pbar_verification.update(1)
        pbar_verification.close()

        return tile_counter

    def get_tif_center(self, image_path):
        with rasterio.open(image_path) as tif:
            center_x = (tif.bounds.left + tif.bounds.right) / 2
            center_y = (tif.bounds.top + tif.bounds.bottom) / 2
        return center_x, center_y


    def find_closest_images(self, csv_path, center, max_distance=100, max_images=5, images_folder='output_tiles', output_folder='processing/selected_images'):
        
        df = pd.read_csv(csv_path)

        
        df['center_x'] = (df['minX'] + df['maxX']) / 2
        df['center_y'] = (df['minY'] + df['maxY']) / 2

        distances = np.sqrt((df['center_x'] - center[0]) ** 2 + (df['center_y'] - center[1]) ** 2)
        df['distance'] = distances

        closest_images = df[df['distance'] <= max_distance].nsmallest(max_images, 'distance')

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for _, row in closest_images.iterrows():
            image_path = os.path.join(images_folder, row['filename'])
            output_image_path = os.path.join(output_folder, row['filename'])
            if os.path.exists(image_path):
                shutil.copy(image_path, output_image_path)
            else:
                print(f"A imagem {row['filename']} não foi encontrada em {images_folder}.")

        print(f"{len(closest_images)} imagens foram copiadas para {output_folder}.")
        
    def setup_ui(self):
        self.image_path_text = widgets.Text(
            value='',
            placeholder='Insira o caminho da ortofoto aqui',
            description='Ortofoto:',
            disabled=True
        )

        self.dropdown = widgets.Dropdown(
            options=['Selecione'] + list(self.specs.keys()),
            value='Selecione',
            description='Algoritmo:',
            disabled=True
        )

        self.button = widgets.Button(description="Gerar Tiles", disabled=True)
        self.output = widgets.Output()

        self.button.on_click(self.on_button_clicked)
        
        self.dropdown.observe(self.on_algorithm_change, names='value')

        display(self.image_path_text, self.dropdown, self.button, self.output)
        
    def on_algorithm_change(self, change):
       
        with self.output:
            clear_output(wait=True)
            if change['new'] == 'Selecione':
                
                display(HTML('<span style="color: red;">Por favor, selecione um algoritmo.</span>'))
            else:
                
                display(HTML(f'<span style="color: blue;">O algoritmo {change["new"]} foi selecionado.</span>'))

    def on_button_clicked(self, b):
      with self.output:
        clear_output()
        if self.dropdown.value == 'Selecione':
            display(HTML('<span style="color: red;">Por favor, selecione um algoritmo.</span>'))
        else:
            selected_spec = self.specs[self.dropdown.value]
            
            
            if selected_spec['link'] is None:
                
                display(HTML(f'<span style="color: orange;">O algoritmo {selected_spec["name"]} está em fase de desenvolvimento. Estamos trabalhando para disponibilizá-lo em breve. Fique atento(a) às próximas atualizações!</span>'))
            else:
                
                image_path = self.image_path_text.value
                output_dir = 'processing/output_tiles'
                csv_path = 'processing/tile_coords.csv'
                
                model_weights_path = 'model_weights.pt'
                display(HTML('<span style="color: orange;">Carregando algoritmo...</span>'))
                self.download_model_weights(selected_spec['link'], model_weights_path)
                display(HTML('<span style="color: green;">O algoritmo foi carregado com sucesso.</span>'))

                num_tiles = self.create_tiles_with_overlap_and_save_coords(image_path, selected_spec['size'], selected_spec['overlap'], output_dir, csv_path)
                display(HTML(f'<span style="color: green;">Número total de tiles criados: {num_tiles}</span>'))

                center = self.get_tif_center(image_path)
                self.find_closest_images(csv_path, center, max_distance=100, max_images=5, images_folder=output_dir, output_folder='processing/selected_images')

                variables = {
                    'crs': str(self.crs),
                    'algorithm': self.dropdown.value,
                    'tile_size': selected_spec['size'],
                    'overlap': selected_spec['overlap']
                }

                with open('processing/variable.json', 'w') as f:

                    json.dump(variables, f, indent=4)
 

"""

File Name: results.py
Origin: Netflora (https://github.com/NetFlora/Netflora)

"""

import argparse
import re
import os
import glob
import shutil
import json
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
from pathlib import Path
from IPython.display import Image, display


with open('processing/variable.json', 'r', encoding='utf-8') as file:
        variables = json.load(file)
        crs = variables['crs']
        algorithm = variables['algorithm']

with open('json/groups.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        species_dict = data['species_dict']
        categories = data['categories']

coords = pd.read_csv("processing/tile_coords.csv")
base_path = "runs/detect/"
output_shapefile_directory = "results/shapefiles/"
output_csv_directory = "results/csv/"
output_dir = "results/"

def map_species_names(df, species_dict):
    df['common_name'] = df['class_id'].map(lambda x: species_dict[x]['common_name'] if x in species_dict else 'Desconhecido')
    return df

def filter_by_algorithm(df, algorithm, categories):
    if algorithm in categories:
        valid_species_codes = categories[algorithm]
        return df[df['class_id'].isin(valid_species_codes)]
    else:
        print(f"Algoritmo {algorithm} não encontrado nas categorias. Usando dados completos.")
        return df

def get_latest_exp_directory(base_path):
    
    base_directory = Path(base_path)
    exp_directories = []

    
    for d in base_directory.iterdir():
        if d.is_dir() and re.match(r"^exp(\d+)?$", d.name):
            exp_directories.append(d)

    if exp_directories:
        
        exp_directories.sort(key=lambda x: int(re.findall(r'\d+', x.name)[0]) if re.findall(r'\d+', x.name) else 0)
        return exp_directories[-1]  
    else:
        return None

def check_and_create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def calculate_iou(bb1, bb2):
    intersection = bb1.intersection(bb2).area
    union = bb1.union(bb2).area
    iou = intersection / union
    return iou

def calculate_score(bb, alpha):
    area_score = bb.area
    shape_score = bb.length
    score = (1 - alpha) * area_score + alpha * shape_score
    return score

def apply_nms_with_score(gdf, iou_threshold, alpha):
    to_remove = []
    for i in range(len(gdf)):
        for j in range(i + 1, len(gdf)):
            bb1 = gdf['geometry'].iloc[i]
            bb2 = gdf['geometry'].iloc[j]

            iou = calculate_iou(bb1, bb2)
            if iou > iou_threshold:
                score_bb1 = calculate_score(bb1, alpha)
                score_bb2 = calculate_score(bb2, alpha)

                if score_bb1 > score_bb2:
                    to_remove.append(j)
                else:
                    to_remove.append(i)

    gdf_nms = gdf.drop(to_remove)
    return gdf_nms

def filter_rectangular_bounding_boxes(gdf, min_aspect_ratio, max_aspect_ratio):
    rectangular_indices = []

    for i, row in gdf.iterrows():
        x1, y1, x2, y2 = row['geometry'].bounds
        width = x2 - x1
        height = y2 - y1
        aspect_ratio = height / width

        if min_aspect_ratio <= aspect_ratio <= max_aspect_ratio:
            rectangular_indices.append(i)

    gdf_filtered = gdf.loc[rectangular_indices].copy()
    return gdf_filtered

def plot_class_distribution(gdf_nms_final, output_dir, algorithm):
    colors = plt.cm.tab20(np.linspace(0, 1, len(gdf_nms_final['name'].unique())))
    class_counts = gdf_nms_final['name'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(class_counts.index, class_counts.values, color=colors, edgecolor='grey')

    for bar, color in zip(bars, colors):
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    color='black')

    plt.title(f'Distribuição de Frequência - {algorithm}', fontsize=18, fontweight='bold', color='black')
    plt.xlabel('Espécie', fontsize=14, fontweight='bold', color='black')
    plt.ylabel('Contagem', fontsize=14, fontweight='bold', color='black')
    plt.xticks(rotation=45, ha='right', fontsize=12, fontweight='normal', color='black')
    plt.yticks(fontsize=12, fontweight='bold', color='black')
    ax.set_facecolor('white')
    fig.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.3)
    ax.xaxis.set_tick_params(size=0)
    ax.yaxis.set_tick_params(size=0)
    plt.tight_layout()
    plt.savefig(f'{output_dir}frequencia_de_{algorithm}.png', dpi=300)
    plt.show()

def showResults(): 
    output_dir = "results/"
    chart_name = f'frequencia_de_{algorithm}.png'
    if os.path.exists(f'{output_dir}{chart_name}'):
        display(Image(f'{output_dir}{chart_name}'))
    else:
        print(f"File not found: {output_dir}{chart_name}")

def downloadResults(): 
    output_dir = "results/"
    zip_name = f"resultados_{algorithm}.zip"
    zip_path = f"{os.getcwd()}/{zip_name}"

    if os.path.exists(zip_path):
        os.remove(zip_path)

    shutil.make_archive(f"resultados_{algorithm}", 'zip', output_dir)
    print(f"Pasta '{output_dir}' zipada como '{zip_path}'.")

    try:
        from google.colab import files
        files.download(zip_path)
        print(f"Initiating file download: {zip_path}")
    except ImportError:
        print(f"Download not available. File saved at {zip_path}")

def main():  
    parser = argparse.ArgumentParser(description="Process and visualize detection data.")
    parser.add_argument('--graphics', action='store_true', help="Generate and display class distribution graphics.")
    parser.add_argument('--download', action='store_true', help="Zip and download the results directory.")
    parser.add_argument('--conf', type=float, default=0.25, help="Confidence threshold for filtering detections.")
    args = parser.parse_args()


    latest_exp_directory = get_latest_exp_directory(base_path)

    if latest_exp_directory:
        base_directory = str(latest_exp_directory) + "/"
    else:
        print("Nenhuma detecão encontrada. Execute primeiro o processo de detecção.")
        base_directory = None  

    time_data = {}

    check_and_create_dir(output_shapefile_directory)
    check_and_create_dir(output_csv_directory)

    pasta_labels = os.path.join(base_directory, "labels")
    arquivos_txt = glob.glob(os.path.join(pasta_labels, "*.txt"))

    data = []

    for arquivo_txt in arquivos_txt:
        filename = os.path.basename(arquivo_txt)[:-4] + ".jpg"
        if filename not in coords['filename'].values:
            print(f"Coordinates not found for {filename} in the CSV. Skipping.")
            continue

        coords_row = coords[coords['filename'] == filename].iloc[0]
        utm_xmin, utm_ymin, utm_xmax, utm_ymax = coords_row[['minX', 'minY', 'maxX', 'maxY']]
        utm_width = utm_xmax - utm_xmin
        utm_height = utm_ymax - utm_ymin

        with open(arquivo_txt, "r") as txt_file:
            for line in txt_file:
                parts = line.split()
                if len(parts) != 6:
                    continue

                class_id, cse_x, cse_y, width, height, confidence = map(float, parts)
                bb_xcenter = utm_xmin + cse_x * utm_width
                bb_ycenter = utm_ymax - cse_y * utm_height
                bb_xmin = bb_xcenter - (width * utm_width / 2)
                bb_ymin = bb_ycenter - (height * utm_height / 2)
                bb_xmax = bb_xmin + width * utm_width
                bb_ymax = bb_ymin + height * utm_height

                data.append([filename, class_id, cse_x, cse_y, width, height,confidence, bb_xmin, bb_ymin, bb_xmax, bb_ymax])

    confidence_threshold = args.conf

    if data:
        df = pd.DataFrame(data, columns=['filename', 'class_id', 'cse_x', 'cse_y', 'width', 'height','confidence', 'bb_xmin', 'bb_ymin', 'bb_xmax', 'bb_ymax'])
        df['num_tiles'] = len(arquivos_txt)
        df = df[df['confidence'] >= confidence_threshold]

        geometry = [box(x1, y1, x2, y2) for x1, y1, x2, y2 in zip(df['bb_xmin'], df['bb_ymin'], df['bb_xmax'], df['bb_ymax'])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)


    else:
        print("No data found in the .txt files. No file will be created.")

    iou_threshold = 0.20
    alpha = 0.20

    min_aspect_ratio = 0.5
    max_aspect_ratio = 2

    gdf_filtered = filter_rectangular_bounding_boxes(gdf, min_aspect_ratio, max_aspect_ratio)
    gdf_filtered = gdf_filtered.reset_index(drop=True)
    gdf_nms = apply_nms_with_score(gdf_filtered, iou_threshold, alpha)


    species_category = categories.get(algorithm, [])
    species_codes = [item["specie"] for item in species_category]


    gdf_nms['name'] = gdf_nms['class_id'].apply(
        lambda x: species_dict.get(species_codes[int(x)], {'common_name': 'Desconhecido'})['common_name'] 
        if int(x) < len(species_codes) else 'Desconhecido'
    )

    gdf_nms['sci_name'] = gdf_nms['class_id'].apply(
        lambda x: species_dict.get(species_codes[int(x)], {'scientific_name': 'Desconhecido'})['scientific_name'] 
        if int(x) < len(species_codes) and species_dict.get(species_codes[int(x)]) else 'Desconhecido'
    )


    gdf_nms_final = gdf_nms[['filename', 'class_id', 'name', 'sci_name', 'confidence', 'geometry']].copy()


    gdf_nms_final.to_file(f'{output_shapefile_directory}/resultados_{algorithm}.shp')
    csv_path = os.path.join(output_csv_directory, f'resultados_{algorithm}.csv')
    gdf_nms_final.to_csv(csv_path, index=False)

    
    if args.graphics:
        
        print("Gerando relatório...")
        print(f'Os resultados da detecção de {algorithm} foram salvos na pasta results')
        plot_class_distribution(gdf_nms_final, output_dir, algorithm)
        showResults()
      
        
        

    if args.download:
        
        print("Zipping and downloading...")
        downloadResults()     

if __name__ == "__main__":
    main()

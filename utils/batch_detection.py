"""

File Name: batch_detection.py
Origin: Netflora (https://github.com/NetFlora/Netflora)

"""



# batch_detection.py
import subprocess
from tqdm import tqdm

def runBatchDetection(thresholds=[0.01, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50],
                        detect_script_path='detect.py',
                        weights_path='model_weights.pt',
                        img_size=640,
                        source_path='processing/selected_images',
                        device=0,
                        save_txt=False):

    for conf in tqdm(thresholds, desc="Processing thresholds"):
        result_name = f'{conf:.2f}'
        command = f'python {detect_script_path} --device {device} --weights {weights_path} --img {img_size} --conf {conf} --source {source_path} --name {result_name} --save-txt {save_txt}'
        subprocess.run(command, shell=True)
    
    print("Amostras para vizualização de theshold criadas com sucesso.")
    
    return


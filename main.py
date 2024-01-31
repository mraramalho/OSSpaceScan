import os
from tqdm import tqdm
import pandas as pd
import argparse

parser = argparse.ArgumentParser(prog='OSSpaceScan',
                        description="Scanner for the size of each folder in the operating system.")
parser.add_argument('--root', type=str, help='root path from where the system crawler must begin', default="C:\\")
parser.add_argument('--min_depth', help='min depth folder for the crawler to consider', type=int, default=3)
parser.add_argument('--max_depth', help='max depth folder for the crawler to consider', type=int, default=3)
parser.add_argument('--report', help='if set to 1, saves an excel report with folders size', type=int, default=0)
parser.add_argument('--log', help='if set to 0, the craler will not save an .txt file with a log of each folders size', type=int, default=1)
parser.add_argument('--quiet', help='if set to 0, the craler will print each folder crawled and its size', type=int, default=1)
args = parser.parse_args()

def logging(folder, total_size):
    cmd = f"echo '{folder}: {total_size} gb' >> log.txt"
    os.system(cmd)

# definir uma função que calcula o tamanho de uma pasta em bytes
def get_folder_size(path):
    # inicializar o tamanho total como zero
    total_size = 0
    # usar o os.walk para iterar sobre todos os arquivos e subpastas
    for dirpath, dirnames, filenames in os.walk(path):
        # para cada arquivo, obter o seu tamanho e somar ao total
        for file in filenames:
            file_path = os.path.join(dirpath, file)
            # pular links simbólicos para evitar recursão infinita
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)
                
    # retornar o tamanho total em bytes     
    return total_size

# definir uma função que retorna uma lista de todas as pastas no computador
def get_all_folders(root, min_depth, max_depth):
    # inicializar uma lista vazia
    folders = []
    # usar o os.walk para iterar sobre todas as pastas na raiz    
    for dirpath, dirnames, filenames in tqdm(os.walk(root),
                                            desc="Getting folders...", 
                                            unit="files", 
                                            ncols=75,
                                            colour='#37B6BD'):
        # verifica a profundidade das pastas
        depth = dirpath.count(os.sep)
        if  depth >= min_depth and depth <= max_depth:
        # para cada pasta, adicionar o seu caminho à lista
            for dir in dirnames:
                dir_path = os.path.join(dirpath, dir)
                folders.append(dir_path)
        else:
            continue
    # retornar a lista de pastas
    return folders

if __name__ == '__main__':
    
    # obter a lista de todas as pastas no computador
    root = args.root
    all_folders = get_all_folders(root, args.min_depth, args.max_depth)
    # criar um dicionário que mapeia cada pasta ao seu tamanho
    folder_sizes = {}
    # para cada pasta na lista, calcular o seu tamanho e adicionar ao dicionário
    for folder in tqdm(all_folders,
                    desc="Getting folders size...", 
                    unit="files", 
                    ncols=75,
                    colour='#37B6BD'):
        
        size = get_folder_size(folder)
        size_gb = round(size / (1024 ** 2), 2)
        folder_sizes[folder] = size_gb
        
        if args.log:
            logging(folder, size_gb)
        
        if not args.quiet:
            print(f'{folder}: {size_gb} gb')
            
    # ordenar o dicionário pelo tamanho em ordem decrescente
    sorted_folder_sizes = dict(sorted(folder_sizes.items(), key=lambda item: item[1], reverse=True))
    # cria um relatório em excel
    if args.report:
        pd.DataFrame(folder_sizes.items(), columns=['Folder', 'Size (Gb)']).\
                                sort_values(by=['Size (Gb)'], ascending=False).\
                                to_excel('OS Size Analysis.xlsx')
        

# **Netflora**

<a href="https://colab.research.google.com/gist/karasinski-mauro/aa12600b2edc9431adc2191be834c354/netflora.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>

<p align="justify">O Projeto Netflora envolve a aplicação de geotecnologias na automação florestal e no mapeamento dos estoques de carbono em áreas de floresta nativa na Amazônia Ocidental, é uma iniciativa desenvolvida pela Embrapa Acre com o apoio do Fundo JBS pela Amazônia.

<p align="justify"> Aqui vamos tratar do componente “Inventário Florestal com uso de drones”. Drones e inteligência artificial são utilizados para automatizar etapas do inventário florestal na identificação de espécies estratégicas. Mais de 40 mil hectares de áreas de floresta já foram mapeados com o objetivo de coletar informações para compor o dataset do Netflora.


<div style="display: flex;">

 <img src="https://github.com/NetFlora/NetFlora/blob/main/logo/Netflora.png?raw=true" width="200" alt="Logo Netflora">

  <img src="https://github.com/NetFlora/NetFlora/blob/main/logo/Embrapa-Acre.png?raw=true" width="200" alt="Logo JBS">
    
   <img src="https://github.com/NetFlora/NetFlora/blob/main/logo/Fundo-JBS.png?raw=true" width="200" alt="Logo Fundo JBS">

</div>

 

 

## Executando a Detecção

``!python detect.py --device 0 --weights model_weights.pt --img 1536``

## Vizualizando os Resultados da Detecção

``!python detect.py --device 0 --weights model_weights.pt --img 1536``

## Exemplos de Detecção pelos Algoritmos

<div style="display: flex;">

 <img src="https://github.com/NetFlora/NetFlora/blob/main/inference/images/Acai.jpg?raw=true" width="230" alt="Acai"> 

 <img src="https://github.com/NetFlora/NetFlora/blob/main/inference/images/Palmeiras.jpg?raw=true" width="250" alt="Palmeira">
 
 <img src="https://github.com/NetFlora/NetFlora/blob/main/inference/images/PFMNs.jpg?raw=true" width="230" alt="PFMNs">
  
 </div>

## Web Site

https://www.embrapa.br/acre/netflora


## Citação


## Licença

Distribuído sob a licença GPL 3.0. Veja [LICENSE](LICENSE.md) para mais informações.

## Links Úteis
- [Ortofoto exemplo](https://drive.google.com/drive/folders/1OcRel7fJHALwm9ZAdU3rSlFwV_4iaZnp?usp=sharing)
- [Curso EAD](https://ava.sede.embrapa.br/course/view.php?id=470)
- [Perguntas Frequentes (FAQ)](https://www.embrapa.br/web/portal/acre/netflora/perguntas-e-respostas)
- [Embrapa Acre](https://www.embrapa.br/acre/)
- [Fundo JBS pela Amazônia](https://fundojbsamazonia.org/)



## Agradencimentos

<details><summary> <b>Expandir</b> </summary>

* [https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet)
* [https://github.com/WongKinYiu/yolov7](https://github.com/WongKinYiu/yolov7)

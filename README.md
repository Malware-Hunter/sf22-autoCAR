# sf22_classification_based_on_association_rules

Ferramenta para automatizar e simplificar a execução dos modelos de classificação baseados em regras de associação. A ferramenta também deverá executar pelo menos dois modelos de aprendizado suporvisionados, para fins de comparação (e.g., SVM e RF).

Primeiras ideias:
(1) a ferramenta deve ser capaz de executar o modelo selecionado pelo usuário;
(2) a ferramenta deve ser flexível e simples para incorporar novos modelos de classificação (e.g., 1 diretório e 1 script de bootstrap por método);
(4) a ferramenta irá apresentar o resultado das métricas dos modelos;
(5) a ferramenta deve permitir especificar: 
- o dataset de entrada;
- o prefixo dos arquivos de saída dos modelos;
(6) a ferramenta poderá também gerar automaticamente gráficos ou tabelas das saídas dos modelos;

Exemplos de parâmetros e execução:

tool.py --list-cbar-models --list-ml-models

tool.py --run-cbar-cba --run-cbar-eqar --run-ml-rf --run-ml-svm --output-cbar-cba cba.csv --output-cbar-eqar eqar.csv --output-ml-rf rf.csv --output-ml-svm svm.csv --plot-graph-all --dataset motodroid.csv 

tool.py --run-cbar-all --run-ml-all --plot-graph-all --datasets motodroid.csv androcrawl.csv drebin215.csv

tool.py --run-cbar-all --run-ml-all --plot-graph-all --datasets-all


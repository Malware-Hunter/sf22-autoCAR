# AutoCAR

### Environment

The tool has been tested and used in practice in the following environments:

**Ubuntu 20.04**

- Kernel = `Linux version 5.4.0-120-generic (buildd@lcy02-amd64-006) (gcc version 9.4.0 (Ubuntu 9.4.0-1ubuntu1~20.04.1)) #136-Ubuntu SMP Fri Jun 10 13:40:48 UTC 2022`
- Python = `Python 3.8.10`
- R 4.2.1


For Installation, Follow Instructions in **How to Install** Section or Run `setup.sh` Script.

### How to Install

**0. Requirements**

- Install R (How to in [CRAN](https://cran.r-project.org/) - Last Acess 17/July/2022):
    ```sh
    $ apt-get update
    $ sudo apt install --no-install-recommends software-properties-common dirmngr
    $ wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
    $ sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
    $ sudo apt update
    $ sudo apt install --no-install-recommends r-base
    ```

- Install Required Python Libraries:
    ```sh
    $ pip install -r requirements.txt
    ```

- Install R Packages:
    ```sh
    $ R
    > install.packages('arulesCBA')
    > q()
    ```

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

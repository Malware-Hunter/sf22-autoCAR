# AutoCAR

### Environment

The tool has been tested and used in practice in the following environments:

**Ubuntu 20.04**

- Kernel = `Linux version 5.4.0-120-generic (buildd@lcy02-amd64-006) (gcc version 9.4.0 (Ubuntu 9.4.0-1ubuntu1~20.04.1)) #136-Ubuntu SMP Fri Jun 10 13:40:48 UTC 2022`
- Python = `Python 3.8.10`
- R = `R 4.2.1`
- Java = `openjdk 17.0.3 2022-04-19`


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

- Install R Package **arulesCBA**

  **Stable CRAN version:** Install From Within R With

    ``` r
    install.packages("arulesCBA")
    ```

  **Current development version:** Install From
    [r-universe.](https://mhahsler.r-universe.dev/ui#package:arulesCBA)

    ``` r
    install.packages("arulesCBA", repos = "https://mhahsler.r-universe.dev")
    ```

### Example Usage

- List Models:

  List Models in Machine Learning (ml) Directory
    ```sh
    $ autocar.py --list-models ml
    ```

  List Models in Association Rules (cbar) and Machine Learning (ml) Directories
    ```sh
    $ autocar.py --list-models cbar ml
    ```

  List All Models
    ```sh
    $ autocar.py --list-models-all
    ```

- Run Models:

  Run Models **CBA** and **EQAR** With Dataset **drebin215.csv** Using Minimum Support at 10% and Rule Quality **prec**
    ```sh
    $ autocar.py --run-cbar cba eqar --datasets drebin215.csv -s 0.1 -q prec
    ```

  Run Models **CPAR** and **SVM** With Datasets **drebin215.csv** and **androit.csv** Using Balanced Datasets
    ```sh
    $ autocar.py --run-cbar cpar --rum-ml svm --datasets drebin215.csv androit.csv --use-balanced-datasets
    ```

  Run All **CBAR** Models With Dataset **drebin215.csv** Using Minimum Support at 20% and Rule Quality **prec**, Generating **Classification** and **Metrics** Graphs
    ```sh
    $ autocar.py --run-cbar-all --datasets drebin215.csv -s 0.2 -q prec --plot-graph class metrics
    ```

  Run All **CBAR** and **ML** Models With All Datasets in **datasets** Directory Using Threshold at 20%, Rule Quality **prec**, Saving Results and Graphs in **outputs** Directory
    ```sh
    $ autocar.py --run-cbar-all --run-ml-all --datasets datasets/*.csv -t 0.2 -q prec --output-dir outputs
    ```

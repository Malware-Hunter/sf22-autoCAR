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
    $ autocar.py --list-models ml
    ```

  List All Models
    ```sh
    $ autocar.py --list-models-all
    ```

- Run Models:

  Run Models **CBA** and **EQAR** With dataset **drebin215.csv** Using Minimum Support at 10% and Rule Quality **prec**
    ```sh
    $ autocar.py --run-cbar cba eqar --datasets drebin215.csv -s 0.1 -q prec
    ```



tool.py --run-cbar-cba --run-cbar-eqar --run-ml-rf --run-ml-svm --output-cbar-cba cba.csv --output-cbar-eqar eqar.csv --output-ml-rf rf.csv --output-ml-svm svm.csv --plot-graph-all --dataset motodroid.csv

tool.py --run-cbar-all --run-ml-all --plot-graph-all --datasets motodroid.csv androcrawl.csv drebin215.csv

tool.py --run-cbar-all --run-ml-all --plot-graph-all --datasets-all

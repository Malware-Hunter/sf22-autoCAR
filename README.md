# AutoCAR

# Environment

The tool has been tested in the following environments:

**Ubuntu 20.04**

- Kernel = `Linux version 5.4.0-120-generic (buildd@lcy02-amd64-006) (gcc version 9.4.0 (Ubuntu 9.4.0-1ubuntu1~20.04.1)) #136-Ubuntu SMP Fri Jun 10 13:40:48 UTC 2022`
- Python = `Python 3.8.10`
- R = `R 4.2.1`
- Java = `openjdk 17.0.3 2022-04-19`


# How to Install

**Requirements**

- Install R (How to in [CRAN](https://cran.r-project.org/) - Last Acess 17/July/2022):
    ```sh
    $ apt-get update
    $ sudo apt install --no-install-recommends software-properties-common dirmngr
    $ wget -qO- https://cloud.r-project.org/bin/linux/ubuntu/marutter_pubkey.asc | sudo tee -a /etc/apt/trusted.gpg.d/cran_ubuntu_key.asc
    $ sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu $(lsb_release -cs)-cran40/"
    $ sudo apt update
    $ sudo apt install --no-install-recommends r-base
    ```

- Install required Python libraries:
    ```sh
    $ pip install -r requirements.txt
    ```

- Install R package **arulesCBA**

  **Stable CRAN version:** Install from within R using the following command

    ``` r
    install.packages("arulesCBA")
    ```

  **Current development version:** Install From
    [r-universe.](https://mhahsler.r-universe.dev/ui#package:arulesCBA)

    ``` r
    install.packages("arulesCBA", repos = "https://mhahsler.r-universe.dev")
    ```

# Usage examples 

- List available models:

  List all machine learning (ml) models
    ```sh
    $ autocar.py --list-models ml
    ```

  List all classification based on association rules (cbar) models
    ```sh
    $ autocar.py --list-models cbar
    ```

  List all available models
    ```sh
    $ autocar.py --list-models-all
    ```

- Running models:

  Run models **CBA** and **EQAR** for the **drebin215.csv** dataset with minimum support at 10% and rule quality **prec**
    ```sh
    $ autocar.py --run-cbar cba eqar --datasets drebin215.csv -s 0.1 -q prec
    ```

  Run models **CPAR** and **SVM** for the **drebin215.csv** and **androit.csv** datasets and automatically balance (i.e., same number of malign and benign samples) each of them
    ```sh
    $ autocar.py --run-cbar cpar --rum-ml svm --datasets drebin215.csv androit.csv --use-balanced-datasets
    ```

  Run all **CBAR** models for the **drebin215.csv** dataset, minimum support at 20%, rule quality **prec** and generate **classification** and **metrics** graphs
    ```sh
    $ autocar.py --run-cbar-all --datasets drebin215.csv -s 0.2 -q prec --plot-graph class metrics
    ```

  Run all **CBAR** and **ML** models for all datasets within the **datasets** directory using threshold at 20%, rule quality **prec**, saving numeric results and graphs in the **outputs** directory
    ```sh
    $ autocar.py --run-cbar-all --run-ml-all --datasets datasets/*.csv -t 0.2 -q prec --output-dir outputs
    ```

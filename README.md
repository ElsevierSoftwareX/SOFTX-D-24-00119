<p align="center">
  <img height="115px" src="images/logo.png" alt="frouros_logo">
</p>

---

<p align="center">
  <!-- CI -->
  <a href="https://github.com/IFCA/frouros/actions/workflows/ci.yml">
    <img src="https://github.com/IFCA/frouros/actions/workflows/ci.yml/badge.svg?style=flat-square" alt="ci"/>
  </a>
  <!-- Code coverage -->
  <a href="https://codecov.io/gh/IFCA/frouros">
    <img src="https://codecov.io/gh/IFCA/frouros/branch/main/graph/badge.svg?token=DLKQSWYTYM" alt="coverage"/>
  </a>
  <!-- Documentation -->
  <a href="https://frouros.readthedocs.io/">
    <img src="https://readthedocs.org/projects/frouros/badge/?version=latest" alt="documentation"/>
  </a>
  <!-- Downloads -->
  <a href="https://pepy.tech/project/frouros">
    <img src="https://static.pepy.tech/badge/frouros/month" alt="downloads"/>
  </a>
  <!-- PyPI -->
  <a href="https://pypi.org/project/frouros">
    <img src="https://img.shields.io/pypi/v/frouros.svg?label=release&color=blue" alt="pypi">
  </a>
  <!-- Python -->
  <a href="https://pypi.org/project/frouros">
    <img src="https://img.shields.io/pypi/pyversions/frouros" alt="python">
  </a>
  <!-- License -->
  <a href="https://opensource.org/licenses/BSD-3-Clause">
    <img src="https://img.shields.io/badge/License-BSD%203--Clause-blue.svg" alt="bsd_3_license">
  </a>
</p>

Frouros is a Python library for drift detection in machine learning systems that provides a combination of classical and more recent algorithms for both concept and data drift detection.

<p align="center">
    <i>
        "Everything changes and nothing stands still"
    </i>
</p>
<p align="center">
    <i>
        "You could not step twice into the same river"
    </i>
</p>
<div align="center" style="width: 70%;">
    <p align="right">
        <i>
            Heraclitus of Ephesus (535-475 BCE.)
        </i>
    </p>
</div>

----

## ⚡️ Quickstart

### Concept drift

As a quick example, we can use the wine dataset to which concept drift it is induced in order to show the use of a concept drift detector like DDM (Drift Detection Method).

```python
import numpy as np
from sklearn.datasets import load_wine
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from frouros.detectors.concept_drift import DDM, DDMConfig

np.random.seed(seed=31)

# Load wine dataset
X, y = load_wine(return_X_y=True)

# Split train (70%) and test (30%)
(
    X_train,
    X_test,
    y_train,
    y_test,
) = train_test_split(X, y, train_size=0.7, random_state=31)

# IMPORTANT: Induce/simulate concept drift in the last part (20%)
# of y_test by modifying some labels (50% approx). Therefore, changing P(y|X))
drift_size = int(y_test.shape[0] * 0.2)
y_test_drift = y_test[-drift_size:]
modify_idx = np.random.rand(*y_test_drift.shape) <= 0.5
y_test_drift[modify_idx] = (y_test_drift[modify_idx] + 1) % len(np.unique(y_test))
y_test[-drift_size:] = y_test_drift

# Define and fit model
pipeline = Pipeline(
    [
        ("scaler", StandardScaler()),
        ("model", LogisticRegression()),
    ]
)
pipeline.fit(X=X_train, y=y_train)

# Detector configuration and instantiation
config = DDMConfig(warning_level=2.0,
                   drift_level=3.0,
                   min_num_instances=30,)
detector = DDM(config=config)

# Simulate data stream (assuming test label available after prediction)
for i, (X, y) in enumerate(zip(X_test, y_test)):
    y_pred = pipeline.predict(X.reshape(1, -1))
    error = 1 - int(y_pred == y)
    detector.update(value=error)
    status = detector.status
    if status["drift"]:
        print(f"Drift detected at index {i}")
        break

>> Drift detected at index 44
```

More concept drift examples can be found [here](https://frouros.readthedocs.io/en/latest/examples.html#data-drift).

### Data drift

As a quick example, we can use the iris dataset to which data drift in order to show the use of a data drift detector like Kolmogorov-Smirnov test.

```python
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from frouros.detectors.data_drift import KSTest

np.random.seed(seed=31)

# Load iris dataset
X, y = load_iris(return_X_y=True)

# Split train (70%) and test (30%)
(
    X_train,
    X_test,
    y_train,
    y_test,
) = train_test_split(X, y, train_size=0.7, random_state=31)

# Set the feature index to which detector is applied
dim_idx = 0

# IMPORTANT: Induce/simulate data drift in the selected feature of y_test by
# applying some gaussian noise. Therefore, changing P(X))
X_test[:, dim_idx] += np.random.normal(
    loc=0.0,
    scale=3.0,
    size=X_test.shape[0],
)

# Define and fit model
model = DecisionTreeClassifier(random_state=31)
model.fit(X=X_train, y=y_train)

# Set significance level for hypothesis testing
alpha = 0.001
# Define and fit detector
detector = KSTest()
detector.fit(X=X_train[:, dim_idx])

# Apply detector to the selected feature of X_test
result = detector.compare(X=X_test[:, dim_idx])

# Check if drift is taking place
result[0].p_value < alpha
>> True # Data drift detected.
# Therefore, we can reject H0 (both samples come from the same distribution).
```

More data drift examples can be found [here](https://frouros.readthedocs.io/en/latest/examples.html#data-drift).

## 🛠 Installation

Frouros can be installed via pip:

```bash
pip install frouros
```

## 🕵🏻‍♂️️ Drift detection methods

The currently implemented detectors are listed in the following table.

<table>
<thead>
  <tr>
    <th>Drift detector</th>
    <th>Type</th>
    <th>Family</th>
    <th>Univariate (U) / Multivariate (M)</th>
    <th>Numerical (N) / Categorical (C)</th>
    <th>Method</th>
    <th>Reference</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="12">Concept drift</td>
    <td rowspan="12">Streaming</td>
    <td rowspan="3">CUMSUM</td>
    <td>U</td>
    <td>N</td>
    <td>CUMSUM</td>
    <td><a href="https://doi.org/10.2307/2333009">Page (1954)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Geometric moving average</td>
    <td><a href="https://doi.org/10.2307/1266443">Roberts (1959)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Page Hinkley</td>
    <td><a href="https://doi.org/10.2307/2333009">Page (1954)</a></td>
  </tr>
  <tr>
    <td rowspan="6">Statistical process control</td>
    <td>U</td>
    <td>N</td>
    <td>DDM</td>
    <td><a href="https://doi.org/10.1007/978-3-540-28645-5_29">Gama et al. (2004)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>ECDD-WT</td>
    <td><a href="https://doi.org/10.1016/j.patrec.2011.08.019">Ross et al. (2012)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>EDDM</td>
    <td><a href="https://www.researchgate.net/publication/245999704_Early_Drift_Detection_Method">Baena-Garcıa et al. (2006)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>HDDM-A</td>
    <td><a href="https://doi.org/10.1109/TKDE.2014.2345382">Frias-Blanco et al. (2014)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>HDDM-W</td>
    <td><a href="https://doi.org/10.1109/TKDE.2014.2345382">Frias-Blanco et al. (2014)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>RDDM</td>
    <td><a href="https://doi.org/10.1016/j.eswa.2017.08.023">Barros et al. (2017)</a></td>
  </tr>
  <tr>
    <td rowspan="3">Window based</td>
    <td>U</td>
    <td>N</td>
    <td>ADWIN</td>
    <td><a href="https://doi.org/10.1137/1.9781611972771.42">Bifet and Gavalda (2007)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>KSWIN</td>
    <td><a href="https://doi.org/10.1016/j.neucom.2019.11.111">Raab et al. (2020)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>STEPD</td>
    <td><a href="https://doi.org/10.1007/978-3-540-75488-6_27">Nishida and Yamauchi (2007)</a></td>
  </tr>
  <tr>
    <td rowspan="14">Data drift</td>
    <td rowspan="12">Batch</td>
    <td rowspan="8">Distance based</td>
    <td>U</td>
    <td>N</td>
    <td>Bhattacharyya distance</td>
    <td><a href="https://www.jstor.org/stable/25047882">Bhattacharyya (1946)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Earth Mover's distance</td>
    <td><a href="https://doi.org/10.1023/A:1026543900054">Rubner et al. (2000)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Hellinger distance</td>
    <td><a href="https://doi.org/10.1515/CRLL.1909.136.210">Hellinger (1909)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Histogram intersection normalized complement</td>
    <td><a href="https://doi.org/10.1007/BF00130487">Swain and Ballard (1991)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Jensen-Shannon distance</td>
    <td><a href="https://doi.org/10.1109/18.61115">Lin (1991)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Kullback-Leibler divergence</td>
    <td><a href="https://doi.org/10.1214/aoms/1177729694">Kullback and Leibler (1951)</a></td>
  </tr>
  <tr>
    <td>M</td>
    <td>N</td>
    <td>MMD</td>
    <td><a href="https://dl.acm.org/doi/10.5555/2188385.2188410">Gretton et al. (2012)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>PSI</td>
    <td><a href="https://doi.org/10.1057/jors.2008.144">Wu and Olson (2010)</a></td>
  </tr>
  <tr>
    <td rowspan="4">Statistical test</td>
    <td>U</td>
    <td>C</td>
    <td>Chi-square test</td>
    <td><a href="https://doi.org/10.1080/14786440009463897">Pearson (1900)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Cramér-von Mises test</td>
    <td><a href="https://doi.org/10.1080/03461238.1928.10416862">Cramér (1902)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Kolmogorov-Smirnov test</td>
    <td><a href="https://doi.org/10.2307/2280095">Massey Jr (1951)</a></td>
  </tr>
  <tr>
    <td>U</td>
    <td>N</td>
    <td>Welch's T-Test</td>
    <td><a href="https://doi.org/10.2307/2332510">Welch (1947)</a></td>
  </tr>
  <tr>
    <td rowspan="2">Streaming</td>
    <td>Distance based</td>
    <td>M</td>
    <td>N</td>
    <td>MMD</td>
    <td><a href="https://dl.acm.org/doi/10.5555/2188385.2188410">Gretton et al. (2012)</a></td>
  </tr>
  <tr>
    <td>Statistical test</td>
    <td>U</td>
    <td>N</td>
    <td>Incremental Kolmogorov-Smirnov test</td>
    <td><a href="https://doi.org/10.1145/2939672.2939836">dos Reis et al. (2016)</a></td>
  </tr>
</tbody>
</table>

## ✅ Who is using Frouros?

Frouros is actively being used by the following projects to implement drift
detection in machine learning pipelines:

 * [AI4EOSC](https://ai4eosc.eu).
 * [iMagine](https://imagine-ai.eu).

If you want your project listed here, do not hesitate to send us a pull request.

## 👍 Contributing

Check out the [contribution](https://github.com/IFCA/frouros/blob/main/CONTRIBUTING.md) section.

## 💬 Citation

Although Frouros paper is still in preprint, if you want to cite it you can use the [preprint](https://arxiv.org/abs/2208.06868) version (to be replaced by the paper once is published).

```bibtex
@article{cespedes2022frouros,
  title={Frouros: A Python library for drift detection in Machine Learning problems},
  author={C{\'e}spedes Sisniega, Jaime and L{\'o}pez Garc{\'\i}a, {\'A}lvaro },
  journal={arXiv preprint arXiv:2208.06868},
  year={2022}
}
```

## 📝 License

Frouros is an open-source software licensed under the [BSD-3-Clause license](https://github.com/IFCA/frouros/blob/main/LICENSE).

## 🙏 Acknowledgements

Frouros has received funding from the Agencia Estatal de Investigación, Unidad de Excelencia María de Maeztu, ref. MDM-2017-0765.

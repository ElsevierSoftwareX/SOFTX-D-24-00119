"""EDDM (Early drift detection method) module."""

import copy
from typing import Dict, Optional, Union, Tuple  # noqa: TYP001

from sklearn.base import BaseEstimator  # type: ignore
from sklearn.utils.validation import check_is_fitted  # type: ignore
import numpy as np  # type: ignore

from frouros.supervised.ddm_based.base import DDMBaseConfig, DDMBasedEstimator


class EDDMConfig(DDMBaseConfig):
    """EDDM (Early drift detection method) configuration class."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        alpha: float = 0.95,
        beta: float = 0.9,
        level: float = 2.0,
        min_num_misclassified_instances: int = 30,
        min_num_instances: int = 30,
    ) -> None:
        """Init method.

        :param alpha: warning zone value
        :type alpha: float
        :param beta: change zone value
        :param level: level factor
        :type level: float
        :param min_num_misclassified_instances: minimum numbers of instances
        to start looking for changes
        :type min_num_misclassified_instances: int
        :param min_num_instances: minimum numbers of instances
        to start looking for changes
        :type min_num_instances: int
        """
        super().__init__(min_num_instances=min_num_instances)
        self.alpha = alpha
        self.beta = beta
        self.level = level
        self.min_num_misclassified_instances = min_num_misclassified_instances

    @property
    def alpha(self) -> float:
        """Alpha property.

        :return: warning zone value
        :rtype: float
        """
        return self._alpha

    @alpha.setter
    def alpha(self, value: float) -> None:
        """Alpha setter.

        :param value: value to be set
        :type value: float
        """
        self._alpha = value

    @property
    def beta(self) -> float:
        """Beta property.

        :return: change zone value
        :rtype: float
        """
        return self._beta

    @beta.setter
    def beta(self, value: float) -> None:
        """Beta setter.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value <= 0.0:
            raise ValueError("beta must be greater than 0.0.")
        if value >= self.alpha:
            raise ValueError("beta must be less than alpha.")
        self._beta = value

    @property
    def level(self) -> float:
        """Level property.

        :return: Level to use in detecting drift
        :rtype: float
        """
        return self._level

    @level.setter
    def level(self, value: float) -> None:
        """Level setter.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value <= 0.0:
            raise ValueError("drift level must be greater than 0.0.")
        self._level = value

    @property
    def min_num_misclassified_instances(self) -> int:
        """Minimum number of misclassified instances property.

        :return: minimum number of misclassified instances to use
        :rtype: float
        """
        return self._min_num_misclassified_instances

    @min_num_misclassified_instances.setter
    def min_num_misclassified_instances(self, value: int) -> None:
        """Minimum number of misclassified instances setter.

        :param value: value to be set
        :type value: int
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError(
                "min_num_misclassified_instances must be greater or equal than 0."
            )
        self._min_num_misclassified_instances = value


class EDDM(DDMBasedEstimator):
    """EDDM (Early drift detection method) algorithm class."""

    def __init__(
        self,
        estimator: BaseEstimator,
        config: EDDMConfig,
    ) -> None:
        """Init method.

        :param estimator: sklearn estimator
        :type estimator: BaseEstimator
        :param config: configuration parameters
        :type config: EDDMConfig
        """
        super().__init__(estimator=estimator, config=config)
        self.actual_distance_error = 0.0
        self.distance_threshold = 0.0
        self.last_distance_error = copy.copy(self.actual_distance_error)
        self.max_distance_threshold = float("-inf")
        self.mean_distance_error = 0.0
        self.num_misclassified_instances = 0
        self.old_mean_distance_error = copy.copy(self.mean_distance_error)
        self.variance_distance_error = 0.0

    @property
    def actual_distance_error(self) -> float:
        """Actual distance error property.

        :return: actual distance error
        :rtype: float
        """
        return self._actual_distance_error

    @actual_distance_error.setter
    def actual_distance_error(self, value: float) -> None:
        """Actual distance error setter.

        :param value: value to be set
        :type value: float
        """
        if value < 0:
            raise ValueError("actual_distance_error must be great or equal than 0.")
        self._actual_distance_error = value

    @property
    def distance_threshold(self) -> float:
        """Distance threshold property.

        :return: distance threshold
        :rtype: float
        """
        return self._distance_threshold

    @distance_threshold.setter
    def distance_threshold(self, value: float) -> None:
        """Distance threshold setter.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError("distance_threshold must be great or equal than 0.")
        self._distance_threshold = value

    @property
    def last_distance_error(self) -> float:
        """Last distance error property.

        :return: last distance error
        :rtype: float
        """
        return self._last_distance_error

    @last_distance_error.setter
    def last_distance_error(self, value: float) -> None:
        """Last distance error setter.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError("last_distance_error must be great or equal than 0.")
        self._last_distance_error = value

    @property
    def max_distance_threshold(self) -> float:
        """Maximum distance threshold property.

        :return: maximum distance threshold
        :rtype: float
        """
        return self._max_distance_threshold

    @max_distance_threshold.setter
    def max_distance_threshold(self, value: float) -> None:
        """Maximum distance threshold setter.

        :param value: value to be set
        :type value: float
        """
        self._max_distance_threshold = value

    @property
    def mean_distance_error(self) -> float:
        """Mean distance error property.

        :return: mean distance error
        :rtype: float
        """
        return self._mean_distance_error

    @mean_distance_error.setter
    def mean_distance_error(self, value: float) -> None:
        """Mean distance error property.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError("mean_distance_error must be great or equal than 0.")
        self._mean_distance_error = value

    @property
    def num_misclassified_instances(self) -> int:
        """Minimum number of misclassified instances property.

        :return: minimum number of misclassified instances to use
        :rtype: float
        """
        return self._num_misclassified_instances

    @num_misclassified_instances.setter
    def num_misclassified_instances(self, value: int) -> None:
        """Minimum number of misclassified instances setter.

        :param value: value to be set
        :type value: int
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError(
                "num_misclassified_instances must be greater or equal than 0."
            )
        self._num_misclassified_instances = value

    @property
    def old_mean_distance_error(self) -> float:
        """Old mean distance error property.

        :return: old mean distance error
        :rtype: float
        """
        return self._old_mean_distance_error

    @old_mean_distance_error.setter
    def old_mean_distance_error(self, value: float) -> None:
        """Old mean distance error setter.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError("old_mean_distance_error must be great or equal than 0.")
        self._old_mean_distance_error = value

    @property
    def std_distance_error(self) -> float:
        """Standard deviation distance error property.

        :return: standard deviation distance error
        :rtype: float
        """
        return self._std_distance_error

    @std_distance_error.setter
    def std_distance_error(self, value: float) -> None:
        """Standard deviation distance error setter.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError("std_distance_error must be great or equal than 0.")
        self._std_distance_error = value

    @property
    def variance_distance_error(self) -> float:
        """Variance distance error property.

        :return: variance deviation distance error
        :rtype: float
        """
        return self._variance_distance_error

    @variance_distance_error.setter
    def variance_distance_error(self, value: float) -> None:
        """Variance distance error setter.

        :param value: value to be set
        :type value: float
        :raises ValueError: Value error exception
        """
        if value < 0:
            raise ValueError("variance must be great or equal than 0.")
        self._variance_distance_error = value

    def _normal_response(self) -> Dict[str, Union[bool, float]]:
        response: Dict[str, Union[bool, float]] = self._response(
            drift=False, warning=False
        )
        return response

    def _response(self, drift: bool, warning: bool) -> Dict[str, Union[bool, float]]:
        response: Dict[str, Union[bool, float]] = self._get_update_response(
            drift=drift,
            warning=warning,
            distance_threshold=self.distance_threshold,
            max_distance_threshold=self.max_distance_threshold,
            mean_distance_error=self.mean_distance_error,
            std_distance_error=self.std_distance_error,
        )
        return response

    def update(self, y: np.array) -> Dict[str, Optional[Union[float, bool]]]:
        """Update drift detector.

        :param y: input data
        :type y: numpy.ndarray
        :return predicted values
        :rtype: numpy.ndarray
        """
        check_is_fitted(self.estimator)
        X, y_pred = self.delayed_predictions.popleft()  # noqa: N806
        self.num_instances += y_pred.shape[0]

        try:
            misclassified_idxs = np.argwhere(~(y != y_pred))[0]
            non_misclassified_instances = False
        except IndexError:
            non_misclassified_instances = True

        if non_misclassified_instances:
            response = self._normal_response()
            return response  # type: ignore

        X = X[misclassified_idxs, :]  # noqa: N806
        y = y[misclassified_idxs]
        y_pred = y_pred[misclassified_idxs]

        self.num_misclassified_instances += misclassified_idxs.size

        self.last_distance_error = self.actual_distance_error
        self.actual_distance_error = self.num_instances - 1

        # Welford´s method to compute incremental mean and standard deviation
        distance = self.actual_distance_error - self.last_distance_error
        self.old_mean_distance_error = self.mean_distance_error
        self.mean_distance_error += (
            distance - self.mean_distance_error
        ) / self.num_misclassified_instances
        self.variance_distance_error += (distance - self.mean_distance_error) * (
            distance - self.old_mean_distance_error
        )
        self.std_distance_error = (
            np.sqrt(self.variance_distance_error / self.num_misclassified_instances)
            if self.num_misclassified_instances > 0
            else 0.0
        )

        if self.num_instances < self.config.min_num_instances:
            response = self._normal_response()
            return response  # type: ignore

        if self._drift_insufficient_samples:
            drift_completed_flag = self._check_drift_insufficient_samples(X=X, y=y)
            if drift_completed_flag:
                response = self._response(drift=True, warning=True)
                return response  # type: ignore

        self.ground_truth.extend(y)
        self.predictions.extend(y_pred)

        if (
            self.num_misclassified_instances
            < self.config.min_num_misclassified_instances  # type: ignore
        ):
            response = self._normal_response()
            return response  # type: ignore

        self.distance_threshold = (
            self.mean_distance_error
            + self.config.level * self.std_distance_error  # type: ignore
        )
        if self.distance_threshold > self.max_distance_threshold:
            self.max_distance_threshold = self.distance_threshold
            response = self._normal_response()
            return response  # type: ignore

        p = self.distance_threshold / self.max_distance_threshold

        drift, warning = self._check_case(X=X, y=y, p=p)

        response = self._response(drift=drift, warning=warning)
        return response  # type: ignore

    def _check_case(
        self, X: np.ndarray, y: np.ndarray, p: float  # noqa: N803
    ) -> Tuple[bool, bool]:
        if p < self.config.beta:  # type: ignore
            # Out-of-Control
            self._drift_case(X=X, y=y)
            drift = True
            warning = True
        else:
            drift = False
            if p < self.config.alpha:  # type: ignore
                # Warning
                self._warning_case(X=X, y=y)
                warning = True
            else:
                self._normal_case(y=y)
                warning = False

        return drift, warning

    def _reset(self) -> None:
        super()._reset()
        self.actual_distance_error = 0.0
        self.distance_threshold = 0.0
        self.last_distance_error = copy.copy(self.actual_distance_error)
        self.max_distance_threshold = float("-inf")
        self.mean_distance_error = 0.0
        self.num_misclassified_instances = 0
        self.old_mean_distance_error = copy.copy(self.mean_distance_error)
        self.variance_distance_error = 0.0

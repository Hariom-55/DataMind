from app.services.insight.insight_generator import InsightGenerator


class StatisticalInsightGenerator(InsightGenerator):

    STRONG_CORRELATION_THRESHOLD = 0.60
    VERY_STRONG_CORRELATION_THRESHOLD = 0.80

    def generate(
        self,
        analysis_results: dict
    ) -> list[dict]:

        statistical_result = (
            analysis_results.get("statistical")
        )

        if not statistical_result:
            return []

        insights = []

        insights.extend(
            self._generate_distribution_insights(
                statistical_result
            )
        )

        insights.extend(
            self._generate_correlation_insights(
                statistical_result
            )
        )

        insights.extend(
            self._generate_hypothesis_insights(
                statistical_result
            )
        )

        return insights

    def _generate_distribution_insights(
        self,
        statistical_result: dict
    ) -> list[dict]:

        distributions = statistical_result.get(
            "distributions",
            {}
        )

        insights = []

        for column, distribution in (
            distributions.items()
        ):

            shape = distribution.get("shape")

            if shape == "RIGHT_SKEWED":

                insights.append(
                    self._build_insight(
                        key=f"right-skewed-{column}",
                        severity="INFO",
                        title=(
                            f"{column} is right-skewed"
                        ),
                        description=(
                            f"The distribution of '{column}' "
                            "shows positive skew."
                        ),
                        evidence={
                            "column": column,
                            "shape": shape,
                            "skewness": (
                                distribution.get(
                                    "skewness"
                                )
                            )
                        },
                        recommendation=(
                            "Consider the distribution shape "
                            "when selecting statistical methods "
                            "or transformations."
                        )
                    )
                )

            elif shape == "LEFT_SKEWED":

                insights.append(
                    self._build_insight(
                        key=f"left-skewed-{column}",
                        severity="INFO",
                        title=(
                            f"{column} is left-skewed"
                        ),
                        description=(
                            f"The distribution of '{column}' "
                            "shows negative skew."
                        ),
                        evidence={
                            "column": column,
                            "shape": shape,
                            "skewness": (
                                distribution.get(
                                    "skewness"
                                )
                            )
                        },
                        recommendation=(
                            "Consider the distribution shape "
                            "when selecting statistical methods "
                            "or transformations."
                        )
                    )
                )

            if (
                distribution.get("tailBehavior")
                == "HEAVY_TAILED"
            ):

                insights.append(
                    self._build_insight(
                        key=f"heavy-tailed-{column}",
                        severity="MEDIUM",
                        title=(
                            f"{column} has heavy tails"
                        ),
                        description=(
                            f"The distribution of '{column}' "
                            "shows relatively heavy tails."
                        ),
                        evidence={
                            "column": column,
                            "kurtosis": (
                                distribution.get(
                                    "kurtosis"
                                )
                            ),
                            "tailBehavior": (
                                distribution.get(
                                    "tailBehavior"
                                )
                            )
                        },
                        recommendation=(
                            "Review extreme observations and "
                            "distribution assumptions before "
                            "using methods sensitive to tails."
                        )
                    )
                )

            normality = distribution.get(
                "normality"
            )

            if not normality:
                continue

            if not normality.get("available"):
                continue

            if normality.get("decision") == "REJECT_NULL":

                insights.append(
                    self._build_insight(
                        key=f"non-normal-{column}",
                        severity="MEDIUM",
                        title=(
                            f"{column} shows evidence "
                            "against normality"
                        ),
                        description=(
                            f"The Shapiro-Wilk normality test "
                            f"returned p-value "
                            f"{normality.get('pValue')} "
                            f"at alpha "
                            f"{normality.get('alpha')}."
                        ),
                        evidence={
                            "column": column,
                            "test": normality.get("test"),
                            "statistic": (
                                normality.get(
                                    "statistic"
                                )
                            ),
                            "pValue": (
                                normality.get(
                                    "pValue"
                                )
                            ),
                            "alpha": (
                                normality.get(
                                    "alpha"
                                )
                            ),
                            "decision": (
                                normality.get(
                                    "decision"
                                )
                            )
                        },
                        recommendation=(
                            "Consider methods that are robust "
                            "to non-normal data or investigate "
                            "whether a transformation is appropriate."
                        )
                    )
                )

        return insights

    def _generate_correlation_insights(
        self,
        statistical_result: dict
    ) -> list[dict]:

        correlation_analysis = (
            statistical_result.get(
                "correlationAnalysis",
                {}
            )
        )

        insights = []

        seen_pairs = set()

        for method, analysis in (
            correlation_analysis.items()
        ):

            for pair in analysis.get(
                "strongest",
                []
            ):

                column1 = pair.get("column1")
                column2 = pair.get("column2")
                correlation = pair.get("correlation")

                if correlation is None:
                    continue

                pair_key = tuple(
                    sorted(
                        [column1, column2]
                    )
                )

                unique_key = (
                    method,
                    pair_key
                )

                if unique_key in seen_pairs:
                    continue

                seen_pairs.add(unique_key)

                absolute_correlation = abs(
                    correlation
                )

                if absolute_correlation < (
                    self.STRONG_CORRELATION_THRESHOLD
                ):
                    continue

                if absolute_correlation >= (
                    self.VERY_STRONG_CORRELATION_THRESHOLD
                ):

                    strength = "VERY_STRONG"

                else:

                    strength = "STRONG"

                insights.append(
                    self._build_insight(
                        key=(
                            f"correlation-{method}-"
                            f"{column1}-{column2}"
                        ),
                        severity="INFO",
                        title=(
                            f"Strong {method} relationship "
                            f"between {column1} and {column2}"
                        ),
                        description=(
                            f"The {method} correlation between "
                            f"'{column1}' and '{column2}' is "
                            f"{correlation}."
                        ),
                        evidence={
                            "method": method,
                            "column1": column1,
                            "column2": column2,
                            "correlation": correlation,
                            "strength": strength,
                            "direction": pair.get(
                                "direction"
                            )
                        },
                        recommendation=(
                            "Investigate the relationship "
                            "further. Correlation does not "
                            "establish causation."
                        )
                    )
                )

        return insights

    def _generate_hypothesis_insights(
        self,
        statistical_result: dict
    ) -> list[dict]:

        hypothesis_results = statistical_result.get(
            "hypothesisTesting"
        )

        if not hypothesis_results:
            return []

        if isinstance(
            hypothesis_results,
            dict
        ):

            if "test" in hypothesis_results:
                hypothesis_results = [
                    hypothesis_results
                ]

            else:
                hypothesis_results = list(
                    hypothesis_results.values()
                )

        if not isinstance(
            hypothesis_results,
            list
        ):
            return []

        insights = []

        for index, result in enumerate(
            hypothesis_results
        ):

            if not isinstance(result, dict):
                continue

            if not result.get("significant"):
                continue

            test_name = result.get(
                "test",
                "HYPOTHESIS_TEST"
            )

            p_value = result.get(
                "pValue"
            )

            insights.append(
                self._build_insight(
                    key=(
                        f"hypothesis-significant-"
                        f"{index}-{test_name}"
                    ),
                    severity="INFO",
                    title=(
                        f"Statistically significant result "
                        f"from {test_name}"
                    ),
                    description=(
                        f"The {test_name} produced a "
                        f"statistically significant result "
                        f"with p-value {p_value}."
                    ),
                    evidence={
                        "test": test_name,
                        "pValue": p_value,
                        "alpha": result.get("alpha"),
                        "decision": result.get(
                            "decision"
                        )
                    },
                    recommendation=(
                        "Interpret the result together with "
                        "effect size, assumptions, sample size, "
                        "and domain context."
                    )
                )
            )

        return insights

    @staticmethod
    def _build_insight(
        key: str,
        severity: str,
        title: str,
        description: str,
        evidence: dict,
        recommendation: str
    ) -> dict:

        return {
            "key": key,
            "category": "STATISTICAL",
            "severity": severity,
            "source": "STATISTICS",
            "title": title,
            "description": description,
            "evidence": evidence,
            "recommendation": recommendation
        }
from app.services.statistical.correlation_service import CorrelationService

class TestCorrelationService:

    def setup_method(self):
        self.service = CorrelationService()

    def test_correlation_strength_classification(self):
        assert (
            self.service._correlation_strength(0.10)
            == "VERY_WEAK"
        )

        assert (
            self.service._correlation_strength(0.20)
            == "WEAK"
        )

        assert (
            self.service._correlation_strength(0.40)
            == "MODERATE"
        )

        assert (
            self.service._correlation_strength(0.60)
            == "STRONG"
        )

        assert (
            self.service._correlation_strength(0.80)
            == "VERY_STRONG"
        )

    def test_correlation_strength_uses_absolute_value(self):
        assert (
            self.service._correlation_strength(-0.85)
            == "VERY_STRONG"
        )

        assert (
            self.service._correlation_strength(-0.55)
            == "MODERATE"
        )

    def test_correlation_direction_classification(self):
        assert (
            self.service._correlation_direction(0.75)
            == "POSITIVE"
        )

        assert (
            self.service._correlation_direction(-0.75)
            == "NEGATIVE"
        )

        assert (
            self.service._correlation_direction(0.0)
            == "NONE"
        )
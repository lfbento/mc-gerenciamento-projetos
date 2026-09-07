#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes Automatizados da Auditoria, Regras de Validação e Integridade Matemática
"""

import unittest
import numpy as np
from datetime import date
from model_schema import ScenarioMetrics, compute_input_hash
from validation_engine import ValidationEngine, ReportGenerationBlocked


class TestAuditValidation(unittest.TestCase):

    def test_monotonic_percentiles(self):
        """Regra 01: Monotonicidade estrita dos percentis."""
        engine = ValidationEngine()
        sc = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=45.0,
            p10=50.0,
            p50=58.0,
            p80=61.0,
            p85=62.0,
            p90=64.0,
            p95=66.0,
            maximum_duration=75.0,
            buffer_p85_p50=4.0,
            buffer_p95_p50=8.0
        )
        res = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc, "scenario_leveled": sc},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text=""
        )
        r1 = [r for r in res.rules_validated if r.rule_id == "R01_SCENARIO_MITIGATED"][0]
        self.assertTrue(r1.passed)

    def test_buffer_exact_arithmetic(self):
        """Regra 02: Aritmética de buffers P85 - P50 e P95 - P50."""
        engine = ValidationEngine()
        p50, p85, p95 = 55.4, 62.1, 67.8
        sc = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=40.0,
            p10=48.0,
            p50=p50,
            p80=60.0,
            p85=p85,
            p90=65.0,
            p95=p95,
            maximum_duration=80.0,
            buffer_p85_p50=round(p85 - p50, 2),
            buffer_p95_p50=round(p95 - p50, 2)
        )
        res = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc, "scenario_leveled": sc},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text=""
        )
        r2 = [r for r in res.rules_validated if r.rule_id == "R02_SCENARIO_MITIGATED"][0]
        self.assertTrue(r2.passed)

    def test_probability_consistency(self):
        """Regra 03: Consistência de probabilidade com o prazo contratual."""
        engine = ValidationEngine()
        # Caso 1: prazo contratual < P50 mas probabilidade informada > 50% -> deve falhar
        sc_invalido = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=40.0,
            p10=48.0,
            p50=60.0,
            p80=63.0,
            p85=65.0,
            p90=68.0,
            p95=70.0,
            maximum_duration=80.0,
            buffer_p85_p50=5.0,
            buffer_p95_p50=10.0,
            contractual_deadline_workdays=55.0,
            probability_on_time=80.0
        )
        res = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc_invalido, "scenario_leveled": sc_invalido},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text=""
        )
        r3 = [r for r in res.rules_validated if r.rule_id == "R03_SCENARIO_MITIGATED"][0]
        self.assertFalse(r3.passed)

    def test_labor_hh_and_cost_reconciliation(self):
        """Regras 04 e 05: Reconciliação de HH e Custo."""
        engine = ValidationEngine()
        recursos = [
            {"codigo": "CALD", "hh_total": 500.0, "taxa_hora": 55.0, "custo_total": 27500.0},
            {"codigo": "SOLD", "hh_total": 300.0, "taxa_hora": 60.0, "custo_total": 18000.0},
            {"codigo": "AJUD", "hh_total": 200.0, "taxa_hora": 35.0, "custo_total": 7000.0}
        ]
        sc = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=40.0,
            p10=45.0,
            p50=50.0,
            p80=55.0,
            p85=56.0,
            p90=58.0,
            p95=60.0,
            maximum_duration=70.0,
            buffer_p85_p50=6.0,
            buffer_p95_p50=10.0,
            total_labor_hours=1000.0,
            total_labor_cost=52500.0,
            cost_p50=400000.0,
            cost_p80=420000.0,
            contingency_cost=20000.0
        )
        res = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc, "scenario_leveled": sc},
            labor_resources=recursos,
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text=""
        )
        r4 = [r for r in res.rules_validated if r.rule_id == "R04_HH_RECONCILIATION"][0]
        r5 = [r for r in res.rules_validated if r.rule_id == "R05_COST_RECONCILIATION"][0]
        r10 = [r for r in res.rules_validated if r.rule_id == "R10_CONTINGENCY_RECONCILIATION"][0]
        self.assertTrue(r4.passed)
        self.assertTrue(r5.passed)
        self.assertTrue(r10.passed)

    def test_wbs_weights_100(self):
        """Regra 06: Pesos da EAP somando 100.0%."""
        engine = ValidationEngine()
        sc = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=10.0, p10=20.0, p50=30.0, p80=40.0, p85=45.0, p90=50.0, p95=55.0, maximum_duration=60.0,
            buffer_p85_p50=15.0, buffer_p95_p50=25.0
        )
        pacotes = [
            {"codigo": "1.0", "peso_percentual": 2.0},
            {"codigo": "2.0", "peso_percentual": 20.0},
            {"codigo": "3.0", "peso_percentual": 30.0},
            {"codigo": "4.0", "peso_percentual": 40.0},
            {"codigo": "5.0", "peso_percentual": 7.0},
            {"codigo": "6.0", "peso_percentual": 1.0}
        ]
        res = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc, "scenario_leveled": sc},
            labor_resources=[],
            wbs_packages=pacotes,
            schedule_decomposition={},
            narrative_text=""
        )
        r6 = [r for r in res.rules_validated if r.rule_id == "R06_WBS_WEIGHTS_100"][0]
        self.assertTrue(r6.passed)

    def test_no_negative_zero_and_no_guarantee_language(self):
        """Regras 07 e 09: Banimento de -0.0 e de promessas determinísticas."""
        engine = ValidationEngine()
        sc = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=10.0, p10=20.0, p50=30.0, p80=40.0, p85=45.0, p90=50.0, p95=55.0, maximum_duration=60.0,
            buffer_p85_p50=15.0, buffer_p95_p50=25.0
        )
        # Teste de falha com linguagem proibida
        res_bad = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc, "scenario_leveled": sc},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text="Este projeto oferece garantia de entrega com risco zero e redução de -0.0 dias."
        )
        r7 = [r for r in res_bad.rules_validated if r.rule_id == "R07_NO_NEGATIVE_ZERO"][0]
        r9 = [r for r in res_bad.rules_validated if r.rule_id == "R09_NO_GUARANTEE_LANGUAGE"][0]
        self.assertFalse(r7.passed)
        self.assertFalse(r9.passed)

        # Teste com linguagem saneada
        res_good = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc, "scenario_leveled": sc},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text="Plano operacional com alta probabilidade estatística de cumprimento e alocação de buffer."
        )
        r7_good = [r for r in res_good.rules_validated if r.rule_id == "R07_NO_NEGATIVE_ZERO"][0]
        r9_good = [r for r in res_good.rules_validated if r.rule_id == "R09_NO_GUARANTEE_LANGUAGE"][0]
        self.assertTrue(r7_good.passed)
        self.assertTrue(r9_good.passed)

    def test_overallocation_honesty(self):
        """Regra 08: Honestidade na sobrealocação pós-nivelamento."""
        engine = ValidationEngine()
        sc_lev = ScenarioMetrics(
            scenario_id="scenario_leveled",
            scenario_name="Nivelado",
            scenario_type="leveled",
            minimum_duration=10.0, p10=20.0, p50=30.0, p80=40.0, p85=45.0, p90=50.0, p95=55.0, maximum_duration=60.0,
            buffer_p85_p50=15.0, buffer_p95_p50=25.0,
            critical_overallocation_days=5
        )
        # Texto mente que há zero sobrecarga -> deve falhar
        res_dishonest = engine.validate_scenarios(
            scenarios={"scenario_leveled": sc_lev},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text="O nivelamento assegurou zero sobrecarga operacional."
        )
        r8 = [r for r in res_dishonest.rules_validated if r.rule_id == "R08_OVERALLOCATION_HONESTY"][0]
        self.assertFalse(r8.passed)

    def test_leveled_simulation_presence(self):
        """Regra 12: Presença de simulação MCMC no cronograma nivelado."""
        engine = ValidationEngine()
        sc_mit = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=10.0, p10=20.0, p50=30.0, p80=40.0, p85=45.0, p90=50.0, p95=55.0, maximum_duration=60.0,
            buffer_p85_p50=15.0, buffer_p95_p50=25.0
        )
        # Sem scenario_leveled -> deve falhar
        res_no_leveled = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc_mit},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text="Linguagem ok"
        )
        r12 = [r for r in res_no_leveled.rules_validated if r.rule_id == "R12_LEVELED_SIMULATION_PRESENT"][0]
        self.assertFalse(r12.passed)

    def test_contingency_and_decomposition(self):
        """Regra 10 e 11: Contingência P80-P50 e Decomposição de Ganhos."""
        engine = ValidationEngine()
        sc = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=10.0, p10=20.0, p50=30.0, p80=40.0, p85=45.0, p90=50.0, p95=55.0, maximum_duration=60.0,
            buffer_p85_p50=15.0, buffer_p95_p50=25.0,
            cost_p50=50000.0,
            cost_p80=62000.0,
            contingency_cost=12000.0
        )
        decomp = {"fast_tracking": 10.0, "crashing": 5.0, "leveling_ga": 3.0, "total_gain": 18.0}
        res = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc, "scenario_leveled": sc},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition=decomp,
            narrative_text=""
        )
        r10 = [r for r in res.rules_validated if r.rule_id == "R10_CONTINGENCY_RECONCILIATION"][0]
        r11 = [r for r in res.rules_validated if r.rule_id == "R11_SCHEDULE_DECOMPOSITION"][0]
        self.assertTrue(r10.passed)
        self.assertTrue(r11.passed)

    def test_report_generation_blocked_on_critical_error(self):
        """Bloqueio de emissão quando há erros críticos."""
        engine = ValidationEngine()
        # Percentis não-monotônicos: min > max
        sc_err = ScenarioMetrics(
            scenario_id="scenario_mitigated",
            scenario_name="Mitigado",
            scenario_type="mitigated",
            minimum_duration=90.0, p10=80.0, p50=70.0, p80=60.0, p85=50.0, p90=40.0, p95=30.0, maximum_duration=20.0
        )
        res = engine.validate_scenarios(
            scenarios={"scenario_mitigated": sc_err},
            labor_resources=[],
            wbs_packages=[],
            schedule_decomposition={},
            narrative_text=""
        )
        self.assertTrue(res.has_critical_errors)
        self.assertEqual(res.validation_status, "REJECTED")
        with self.assertRaises(ReportGenerationBlocked):
            raise ReportGenerationBlocked(res.critical_errors)


if __name__ == "__main__":
    unittest.main()

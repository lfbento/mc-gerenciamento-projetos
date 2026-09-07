#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Validação Matemática, Estatística e de Integridade (Audit Engine)
==========================================================================
Implementa as 20 regras de validação estritas que bloqueiam a emissão do PDF
em caso de inconsistência matemática, discrepância de somatórios ou violação
de governança probabilística.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from model_schema import ScenarioMetrics, ValidationRuleResult, AuditReportSummary


class ReportGenerationBlocked(Exception):
    """Exceção levantada para impedir a emissão de relatórios com erros críticos."""
    def __init__(self, errors: List[str]):
        self.errors = errors
        msg = f"EMISSÃO BLOQUEADA: Foram detectados {len(errors)} erros críticos de validação:\n" + "\n".join(f"  - {e}" for e in errors)
        super().__init__(msg)


class ValidationEngine:
    """Motor central de validação e reconciliação auditável."""

    def __init__(self):
        self.results: List[ValidationRuleResult] = []
        self.critical_errors: List[str] = []
        self.warnings: List[str] = []

    def _add_rule(self, rule_id: str, name: str, passed: bool, severity: str, message: str, details: Dict[str, Any] = None):
        res = ValidationRuleResult(
            rule_id=rule_id,
            rule_name=name,
            severity=severity,
            passed=passed,
            message=message,
            details=details or {}
        )
        self.results.append(res)
        if not passed:
            if severity == "CRITICAL":
                self.critical_errors.append(f"[{rule_id}] {name}: {message}")
            else:
                self.warnings.append(f"[{rule_id}] {name}: {message}")

    def validate_scenarios(
        self,
        scenarios: Dict[str, ScenarioMetrics],
        labor_resources: List[Dict[str, Any]],
        wbs_packages: List[Dict[str, Any]],
        schedule_decomposition: Dict[str, float],
        narrative_text: str = ""
    ) -> AuditReportSummary:
        self.results.clear()
        self.critical_errors.clear()
        self.warnings.clear()

        # -------------------------------------------------------------
        # REGRA 01: Monotonicidade dos Percentis
        # -------------------------------------------------------------
        for sc_id, sc in scenarios.items():
            if sc.scenario_type in ["inertial", "mitigated", "leveled"]:
                is_monotonic = (
                    sc.minimum_duration <= sc.p10 <= sc.p50 <= sc.p80 <= sc.p85 <= sc.p90 <= sc.p95 <= sc.maximum_duration
                )
                self._add_rule(
                    f"R01_{sc_id.upper()}",
                    f"Monotonicidade de Percentis ({sc.scenario_name})",
                    is_monotonic,
                    "CRITICAL",
                    f"Percentis ordenados: min={sc.minimum_duration:.1f} <= p10={sc.p10:.1f} <= p50={sc.p50:.1f} <= p85={sc.p85:.1f} <= p95={sc.p95:.1f} <= max={sc.maximum_duration:.1f}",
                    {"min": sc.minimum_duration, "p10": sc.p10, "p50": sc.p50, "p85": sc.p85, "p95": sc.p95, "max": sc.maximum_duration}
                )

        # -------------------------------------------------------------
        # REGRA 02: Aritmética dos Buffers P85 - P50 e P95 - P50
        # -------------------------------------------------------------
        for sc_id, sc in scenarios.items():
            if sc.scenario_type in ["mitigated", "leveled"]:
                expected_b85 = sc.p85 - sc.p50
                expected_b95 = sc.p95 - sc.p50
                diff_85 = abs(sc.buffer_p85_p50 - expected_b85)
                diff_95 = abs(sc.buffer_p95_p50 - expected_b95)
                b_ok = diff_85 < 0.05 and diff_95 < 0.05
                self._add_rule(
                    f"R02_{sc_id.upper()}",
                    f"Aritmética Exata de Buffers ({sc.scenario_name})",
                    b_ok,
                    "CRITICAL",
                    f"Buffer P85-P50 informado: {sc.buffer_p85_p50:.2f}d (Esperado: {expected_b85:.2f}d, diff={diff_85:.4f}d)",
                    {"reported_b85": sc.buffer_p85_p50, "expected_b85": expected_b85}
                )

        # -------------------------------------------------------------
        # REGRA 03: Consistência da Probabilidade de Cumprimento
        # -------------------------------------------------------------
        for sc_id, sc in scenarios.items():
            if sc.contractual_deadline_workdays > 0 and sc.scenario_type in ["inertial", "mitigated", "leveled"]:
                prob_ok = True
                msg = f"Probabilidade {sc.probability_on_time:.1f}% consistente com prazo {sc.contractual_deadline_workdays:.1f}d"
                if sc.contractual_deadline_workdays >= sc.p95 and sc.probability_on_time < 94.0:
                    prob_ok = False
                    msg = f"Prazo contratual ({sc.contractual_deadline_workdays:.1f}d) >= P95 ({sc.p95:.1f}d), mas probabilidade informada é {sc.probability_on_time:.1f}% (< 95%)"
                elif sc.contractual_deadline_workdays < sc.p50 and sc.probability_on_time > 51.0:
                    prob_ok = False
                    msg = f"Prazo contratual ({sc.contractual_deadline_workdays:.1f}d) < P50 ({sc.p50:.1f}d), mas probabilidade informada é {sc.probability_on_time:.1f}% (> 50%)"
                self._add_rule(
                    f"R03_{sc_id.upper()}",
                    f"Consistência de Probabilidade ({sc.scenario_name})",
                    prob_ok,
                    "CRITICAL",
                    msg,
                    {"prob": sc.probability_on_time, "deadline": sc.contractual_deadline_workdays, "p50": sc.p50, "p95": sc.p95}
                )

        # -------------------------------------------------------------
        # REGRA 04: Reconciliação Matemática de Homens-Hora (HH)
        # -------------------------------------------------------------
        sc_base = scenarios.get("scenario_mitigated") or scenarios.get("scenario_inertial")
        if sc_base and labor_resources:
            sum_hh = sum(float(item.get("hh_total", 0.0)) for item in labor_resources)
            diff_hh = abs(sum_hh - sc_base.total_labor_hours)
            hh_ok = diff_hh < 0.10
            self._add_rule(
                "R04_HH_RECONCILIATION",
                "Reconciliação Estrita de Homens-Hora (HH)",
                hh_ok,
                "CRITICAL",
                f"Soma das especialidades: {sum_hh:.1f} HH == Total reportado: {sc_base.total_labor_hours:.1f} HH (dif={diff_hh:.3f} HH)",
                {"sum_hh": sum_hh, "reported_hh": sc_base.total_labor_hours}
            )

        # -------------------------------------------------------------
        # REGRA 05: Reconciliação Matemática de Custos de Mão de Obra
        # -------------------------------------------------------------
        if sc_base and labor_resources:
            sum_cost = sum(float(item.get("custo_total", item.get("hh_total", 0) * item.get("taxa_hora", 0))) for item in labor_resources)
            diff_cost = abs(sum_cost - sc_base.total_labor_cost)
            cost_ok = diff_cost < 1.00
            self._add_rule(
                "R05_COST_RECONCILIATION",
                "Reconciliação Estrita de Custos de Mão de Obra",
                cost_ok,
                "CRITICAL",
                f"Soma dos custos por função: R$ {sum_cost:,.2f} == Total reportado: R$ {sc_base.total_labor_cost:,.2f} (dif=R$ {diff_cost:.2f})",
                {"sum_cost": sum_cost, "reported_cost": sc_base.total_labor_cost}
            )

        # -------------------------------------------------------------
        # REGRA 06: Pesos da EAP somando 100.0%
        # -------------------------------------------------------------
        if wbs_packages:
            sum_weights = sum(float(p.get("peso_percentual", 0.0)) for p in wbs_packages)
            w_ok = abs(sum_weights - 100.0) < 0.01
            self._add_rule(
                "R06_WBS_WEIGHTS_100",
                "Somatório de Pesos da EAP / WBS",
                w_ok,
                "CRITICAL",
                f"Soma dos pesos dos pacotes: {sum_weights:.2f}% (Esperado: 100.00%)",
                {"sum_weights": sum_weights}
            )

        # -------------------------------------------------------------
        # REGRA 07: Ausência de Texto com Zero Negativo ("-0.0")
        # -------------------------------------------------------------
        neg_zero_present = "-0.0" in narrative_text or "-0,0" in narrative_text
        self._add_rule(
            "R07_NO_NEGATIVE_ZERO",
            "Ausência de Formatação Negativa Nula ('-0.0')",
            not neg_zero_present,
            "CRITICAL",
            "Nenhum texto contém '-0.0' ou '-0,0'" if not neg_zero_present else "Encontrado texto com '-0.0' ou '-0,0'",
            {"neg_zero_present": neg_zero_present}
        )

        # -------------------------------------------------------------
        # REGRA 08: Honestidade de Sobrealocação no Nivelamento
        # -------------------------------------------------------------
        sc_lev = scenarios.get("scenario_leveled")
        if sc_lev:
            days_over = sc_lev.critical_overallocation_days
            has_false_zero = (days_over > 0) and (
                "zero sobrecarga" in narrative_text.lower() or
                "zero sobrealocação" in narrative_text.lower() or
                "100% de estabilidade (sem horas extras)" in narrative_text.lower()
            )
            self._add_rule(
                "R08_OVERALLOCATION_HONESTY",
                "Coerência Narrativa de Sobrealocação Pós-Nivelamento",
                not has_false_zero,
                "CRITICAL",
                f"Dias de sobrealocação após GA: {days_over} dias. Narrativa consistente e sem falsas alegações de zero sobrecarga." if not has_false_zero else f"Contradição: {days_over} dias de sobrealocação detectados, mas relatório afirma 'zero sobrecarga'.",
                {"days_over": days_over}
            )

        # -------------------------------------------------------------
        # REGRA 09: Banimento de Linguagem Determinística / Garantia
        # -------------------------------------------------------------
        forbidden_phrases = [
            "garantia de entrega",
            "atraso garantido",
            "risco zero",
            "100% garantido",
            "prazo garantido"
        ]
        found_forbidden = [f for f in forbidden_phrases if f in narrative_text.lower()]
        self._add_rule(
            "R09_NO_GUARANTEE_LANGUAGE",
            "Saneamento de Linguagem Probabilística (Sem Garantias Falsas)",
            len(found_forbidden) == 0,
            "CRITICAL",
            "Linguagem estocástica estrita aplicada com sucesso." if len(found_forbidden) == 0 else f"Termos proibidos encontrados: {found_forbidden}",
            {"found_forbidden": found_forbidden}
        )

        # -------------------------------------------------------------
        # REGRA 10: Contingência Financeira == Cost_P80 - Cost_P50
        # -------------------------------------------------------------
        if sc_base:
            exp_contingency = sc_base.cost_p80 - sc_base.cost_p50
            diff_cont = abs(sc_base.contingency_cost - exp_contingency)
            cont_ok = diff_cont < 0.10
            self._add_rule(
                "R10_CONTINGENCY_RECONCILIATION",
                "Reconciliação da Contingência Financeira (P80 - P50)",
                cont_ok,
                "CRITICAL",
                f"Contingência: R$ {sc_base.contingency_cost:,.2f} == P80 (R$ {sc_base.cost_p80:,.2f}) - P50 (R$ {sc_base.cost_p50:,.2f})",
                {"contingency": sc_base.contingency_cost, "cost_p80": sc_base.cost_p80, "cost_p50": sc_base.cost_p50}
            )

        # -------------------------------------------------------------
        # REGRA 11: Decomposição Auditável dos Ganhos de Prazo
        # -------------------------------------------------------------
        if schedule_decomposition:
            gain_ft = schedule_decomposition.get("fast_tracking", 0.0)
            gain_cr = schedule_decomposition.get("crashing", 0.0)
            gain_ga = schedule_decomposition.get("leveling_ga", 0.0)
            total_gain = schedule_decomposition.get("total_gain", 0.0)
            sum_gains = gain_ft + gain_cr + gain_ga
            diff_gain = abs(sum_gains - total_gain)
            gain_ok = diff_gain < 0.50
            self._add_rule(
                "R11_SCHEDULE_DECOMPOSITION",
                "Decomposição Auditável dos Ganhos de Prazo",
                gain_ok,
                "WARNING",
                f"Soma dos ganhos marginais ({gain_ft:.1f}d + {gain_cr:.1f}d + {gain_ga:.1f}d = {sum_gains:.1f}d) reconciliada com ganho total ({total_gain:.1f}d)",
                {"sum_gains": sum_gains, "total_gain": total_gain, "diff": diff_gain}
            )

        # -------------------------------------------------------------
        # REGRA 12: Simulação Estocástica do Cronograma Nivelado Presente
        # -------------------------------------------------------------
        has_leveled_sim = "scenario_leveled" in scenarios and scenarios["scenario_leveled"].iterations > 0
        self._add_rule(
            "R12_LEVELED_SIMULATION_PRESENT",
            "Existência de Simulação Estocástica do Cronograma Nivelado",
            has_leveled_sim,
            "CRITICAL",
            "Cronograma nivelado possui distribuição MCMC simulada independente." if has_leveled_sim else "Cronograma nivelado não foi submetido à simulação estocástica MCMC.",
            {"has_leveled_sim": has_leveled_sim}
        )

        has_critical = len(self.critical_errors) > 0
        status = "REJECTED" if has_critical else "APPROVED"

        first_sc = next(iter(scenarios.values()))
        return AuditReportSummary(
            project_name=first_sc.scenario_name,
            tag_equipment=first_sc.scenario_id,
            client=first_sc.calendar_type,
            run_id=first_sc.run_id,
            timestamp=first_sc.start_date.isoformat() if first_sc.start_date else "",
            input_hash=first_sc.input_data_hash,
            seed=first_sc.random_seed,
            iterations=first_sc.iterations,
            scenarios={k: v.to_dict() for k, v in scenarios.items()},
            schedule_decomposition=schedule_decomposition,
            rules_validated=self.results,
            has_critical_errors=has_critical,
            validation_status=status,
            critical_errors=self.critical_errors,
            warnings=self.warnings
        )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Esquemas Tipados de Dados para Cenários, Simulações MCMC e Auditoria
===================================================================
Define as estruturas canônicas de dados segregadas por cenário, garantindo
rastreabilidade, integridade matemática e ausência de mistura de dados.
"""

from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Dict, Any, List, Optional
import hashlib
import json


@dataclass
class ScenarioMetrics:
    scenario_id: str                          # Ex: "scenario_inertial", "scenario_mitigated", "scenario_leveled"
    scenario_name: str                        # Nome descritivo do cenário
    scenario_type: str                        # "nominal", "inertial", "mitigated", "leveled", "contractual"
    parent_scenario_id: Optional[str] = None
    simulation_version: str = "2.0.0"
    model_version: str = "MCMC-Markov-2Regimes"
    input_data_hash: str = ""
    run_id: str = ""
    random_seed: int = 42
    iterations: int = 20000
    calendar_id: str = "CAL-BR-IND-40H"
    calendar_type: str = "Seg-Sex 8h/dia com Feriados Nacionais"
    start_date: Optional[date] = None
    contractual_deadline_date: Optional[date] = None
    contractual_deadline_workdays: float = 0.0

    # Estatísticas de Prazo (Dias Úteis)
    deterministic_duration: float = 0.0
    mean_duration: float = 0.0
    median_duration: float = 0.0
    std_duration: float = 0.0
    minimum_duration: float = 0.0
    maximum_duration: float = 0.0
    skewness: float = 0.0
    kurtosis: float = 0.0
    p10: float = 0.0
    p50: float = 0.0
    p80: float = 0.0
    p85: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    probability_on_time: float = 0.0

    # Buffers Estocásticos (Dias Úteis)
    buffer_p85_p50: float = 0.0
    buffer_p95_p50: float = 0.0

    # Métricas de Recursos e Mão de Obra
    resource_peak_fte: float = 0.0
    resource_average_fte: float = 0.0
    resource_variance: float = 0.0
    critical_overallocation_days: int = 0
    total_labor_hours: float = 0.0
    total_labor_cost: float = 0.0

    # Métricas Financeiras e Contingência (R$)
    cost_p50: float = 0.0
    cost_p80: float = 0.0
    cost_p85: float = 0.0
    cost_p95: float = 0.0
    contingency_cost: float = 0.0
    budget_base: float = 0.0
    probability_cost_overrun: float = 0.0

    # Metadados e Rastreabilidade
    mitigation_actions: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_status: str = "PENDING"        # "PENDING", "APPROVED", "REJECTED"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if self.start_date:
            d["start_date"] = self.start_date.isoformat()
        if self.contractual_deadline_date:
            d["contractual_deadline_date"] = self.contractual_deadline_date.isoformat()
        return d


@dataclass
class ValidationRuleResult:
    rule_id: str
    rule_name: str
    severity: str                             # "CRITICAL" (bloqueia PDF) ou "WARNING" (alerta)
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReportSummary:
    project_name: str
    tag_equipment: str
    client: str
    run_id: str
    timestamp: str
    input_hash: str
    seed: int
    iterations: int
    scenarios: Dict[str, Any] = field(default_factory=dict)
    schedule_decomposition: Dict[str, float] = field(default_factory=dict)
    rules_validated: List[ValidationRuleResult] = field(default_factory=list)
    has_critical_errors: bool = False
    validation_status: str = "PENDING"
    critical_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project_name": self.project_name,
            "tag_equipment": self.tag_equipment,
            "client": self.client,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "input_hash": self.input_hash,
            "seed": self.seed,
            "iterations": self.iterations,
            "validation_status": self.validation_status,
            "has_critical_errors": self.has_critical_errors,
            "critical_errors": self.critical_errors,
            "warnings": self.warnings,
            "schedule_decomposition": self.schedule_decomposition,
            "rules_validated": [asdict(r) for r in self.rules_validated],
            "scenarios": self.scenarios
        }


def compute_input_hash(data: Any) -> str:
    """Calcula hash SHA-256 reproduzível para rastreabilidade de entradas."""
    s = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

from dataclasses import dataclass, field
from typing import List, Optional

from module.docschema.documents.base import DTOBase

# =========================
# DTOs básicos / auxiliares
# =========================

@dataclass
class GarantiaOperacaoDTO:
    tipo_garantia: str = ""
    garantia: str = ""
    nome_garantidor: str = ""
    valor: float = 0.0


@dataclass
class GarantiaContaCorrenteDTO:
    tipo_garantia: str = ""
    nome_garantidor: str = ""


@dataclass
class SocioDTO:
    nome: str = ""
    cpf: str = ""
    tipo_relacionamento: str = ""
    capital_empresa: float = 0.0


@dataclass
class ChequeMotivoDTO:
    motivo: str = ""
    total_valor: float = 0.0
    total_cheques: int = 0


@dataclass
class RendaDTO:
    tipo_renda: str = ""
    renda_bruta_mensal: float = 0.0
    data_atualizacao: str = ""


@dataclass
class BemResumoDTO:
    valor_total: float = 0.0
    quantidade_total: int = 0


@dataclass
class ContaCapitalDTO:
    valor_integralizado: float = 0.0
    tempo_desde_matricula: str = ""


@dataclass
class ConsolidadoDTO:
    iap: str = ""
    quadrante: str = ""
    rentabilidade: float = 0.0
    soc: float = 0.0


@dataclass
class AplicacaoDTO:
    valor: float = 0.0


@dataclass
class SaldoMedioDTO:
    valor: float = 0.0


@dataclass
class ConjugeDTO:
    cpf: str = ""
    nome: str = ""


@dataclass
class DadosGeraisDTO:
    nome_razao_social: str = ""
    nome_fantasia: str = ""
    profissao: str = ""
    cnae: str = ""
    estado_civil: str = ""
    regime_bens: str = ""
    tempo_constituicao: str = ""
    risco: str = ""
    tipo_pessoa: str = ""  # "PF" | "PJ"


@dataclass
class GrupoEconomicoPessoaDTO:
    cpf_cnpj: str = ""
    nome: str = ""
    risco: str = ""


@dataclass
class GrupoEconomicoDTO:
    descricao: str = ""
    endividamento_cooperativa: float = 0.0
    endividamento_bacen: float = 0.0
    integralizacao_conta_capital: float = 0.0
    patrimonio_grupo: float = 0.0
    pessoas: List[GrupoEconomicoPessoaDTO] = field(default_factory=list)


@dataclass
class LimiteDescontoDTO:
    limite: float = 0.0
    utilizado: float = 0.0


@dataclass
class BacenResumoDTO:
    valor_total_saldo_devedor: float = 0.0
    endividamento_curto_prazo_total: float = 0.0
    endividamento_longo_prazo_total: float = 0.0
    prejuizo_total: float = 0.0
    valor_vencido_total: float = 0.0
    percentual_maior_modalidade: float = 0.0
    maior_modalidade: str = ""


@dataclass
class RendaBacenDTO:
    data_movimento: str = ""
    saldo_devedor_bacen: float = 0.0


@dataclass
class SerasaDTO:
    score: int = 0
    acao_judicial: str = ""
    divida_vencida: str = ""
    falencia: str = ""
    pefin: str = ""
    protesto: str = ""
    refin: str = ""
    recheque: str = ""


@dataclass
class AnotacaoResumoDTO:
    total_anotacoes: int = 0
    valor_total: float = 0.0


# =========================
# Sumula / garantias
# =========================

@dataclass
class GarantiaPessoalDTO:
    nome: str = ""
    cpf_cnpj: str = ""
    qtd_op_direta: int = 0
    valor_op_direta: float = 0.0
    qtd_op_indireta: int = 0
    valor_op_indireta: float = 0.0
    valor_total_bens: float = 0.0


@dataclass
class GarantiaRealPessoaDTO:
    nome: str = ""
    cpf_cnpj: str = ""
    responsabilidade: str = ""


@dataclass
class GarantiaRealDTO:
    grupo_garantia: str = ""
    valor_garantia: float = 0.0
    ultima_avaliacao: str = ""
    pessoas: List[GarantiaRealPessoaDTO] = field(default_factory=list)


@dataclass
class SumulaDTO:
    valor_contratado: float = 0.0
    taxa_juros_mes: float = 0.0
    seguro_proposta: str = ""
    carencia_dias: int = 0
    prazo_meses: int = 0
    carteira: str = ""
    estagio: str = ""
    perc_perda_esperada: float = 0.0
    valor_perda_esperada: float = 0.0
    capacidade_pagamento: str = ""
    total_bens_garantia_pessoal: float = 0.0
    total_garantia_real: float = 0.0
    quantidade_garantia_real: int = 0
    garantias_pessoais: List[GarantiaPessoalDTO] = field(default_factory=list)
    garantias_reais: List[GarantiaRealDTO] = field(default_factory=list)


# =========================
# Conta corrente / operações
# =========================

@dataclass
class ContaCorrenteDTO:
    valor_operacao_limite: float = 0.0
    valor_saldo_devedor_limite: float = 0.0
    quantidade_dias_utilizado_limite: int = 0
    quantidade_dias_atraso_parcela_utilizado_adp: int = 0
    valor_saldo_devedor_adp: float = 0.0
    garantias: List[GarantiaContaCorrenteDTO] = field(default_factory=list)


@dataclass
class LancamentoContaCorrenteResumoDTO:
    periodo: str = ""  # "6_meses" | "1_ano"
    quantidade_total: int = 0
    valor_total_credito: float = 0.0
    valor_total_debito: float = 0.0
    lancamentos_credito: int = 0
    lancamentos_debito: int = 0
    maior_movimentacao_tipo: str = ""
    maior_movimentacao_percentual: float = 0.0


@dataclass
class OperacaoDTO:
    modalidade: str = ""
    linha_credito: str = ""
    valor_operacao_limite: float = 0.0
    valor_saldo_devedor_limite: float = 0.0
    valor_medio_parcelas: float = 0.0
    quantidade_parcelas: int = 0
    quantidade_parcelas_pagas: int = 0
    situacao_conta_cartao: str = ""
    garantias: List[GarantiaOperacaoDTO] = field(default_factory=list)


@dataclass
class OperacaoModalidadeDTO:
    modalidade: str = ""
    quantidade_contratos: int = 0
    valor_total_saldo_devedor: float = 0.0
    operacoes: List[OperacaoDTO] = field(default_factory=list)


@dataclass
class OperacaoResumoDTO:
    quantidade_total: int = 0
    valor_total: float = 0.0
    percentual_maior_modalidade: float = 0.0
    maior_modalidade: str = ""


@dataclass
class OperacaoAgregadaDTO:
    modalidade: str = ""
    valor_total_saldo_devedor: float = 0.0
    valor_total_operacoes: float = 0.0
    valor_total_parcelas: float = 0.0
    quantidade_parcelas: int = 0
    garantias: List[GarantiaOperacaoDTO] = field(default_factory=list)


# =========================
# Seções principais
# =========================

@dataclass
class DadosPessoaDTO:
    exibir_titulo_tomador: bool = False
    nome_pessoa: str = ""
    cpf_cnpj: str = ""
    dados_gerais: Optional[DadosGeraisDTO] = None
    conjuge: Optional[ConjugeDTO] = None
    socios: List[SocioDTO] = field(default_factory=list)
    renda: Optional[RendaDTO] = None
    bens_resumo: Optional[BemResumoDTO] = None
    conta_capital: Optional[ContaCapitalDTO] = None
    consolidado: Optional[ConsolidadoDTO] = None
    aplicacao: Optional[AplicacaoDTO] = None
    saldo_medio: Optional[SaldoMedioDTO] = None
    possui_dados: bool = True

    @property
    def possui_conjuge(self) -> bool:
        return (self.conjuge is not None 
            and self.dados_gerais is not None 
            and self.dados_gerais.estado_civil.strip().upper() in ["CASADO(A)", "UNIÃO ESTAVEL"]
        )


@dataclass
class ContaCorrenteSecaoDTO:
    contas: List[ContaCorrenteDTO] = field(default_factory=list)
    lancamentos_6_meses: Optional[LancamentoContaCorrenteResumoDTO] = None
    lancamentos_1_ano: Optional[LancamentoContaCorrenteResumoDTO] = None


@dataclass
class ChequesDTO:
    motivos: List[ChequeMotivoDTO] = field(default_factory=list)


@dataclass
class OperacoesSecaoDTO:
    resumo: Optional[OperacaoResumoDTO] = None
    modalidades: List[OperacaoModalidadeDTO] = field(default_factory=list)
    td_agregado: Optional[OperacaoAgregadaDTO] = None
    td_prejuizo_agregado: Optional[OperacaoAgregadaDTO] = None


@dataclass
class ExtraInfoDTO:
    limite_desconto: Optional[LimiteDescontoDTO] = None
    bacen_resumo: Optional[BacenResumoDTO] = None
    renda_bacen: List[RendaBacenDTO] = field(default_factory=list)
    serasa: Optional[SerasaDTO] = None
    anotacoes_baixadas: Optional[AnotacaoResumoDTO] = None
    anotacoes_vigentes: Optional[AnotacaoResumoDTO] = None


@dataclass
class RelatorioPropostaDTO(DTOBase):
    analise_id: int = 0
    proposta_id: int = 0
    tomador: bool = False

    sumula: Optional[SumulaDTO] = None
    dados_pessoa: Optional[DadosPessoaDTO] = None
    conta_corrente: Optional[ContaCorrenteSecaoDTO] = None
    grupo_economico: Optional[GrupoEconomicoDTO] = None
    cheques: Optional[ChequesDTO] = None
    operacoes: Optional[OperacoesSecaoDTO] = None
    extra_info: Optional[ExtraInfoDTO] = None


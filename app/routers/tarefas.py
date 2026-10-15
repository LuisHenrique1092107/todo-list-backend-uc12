from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.dependencies import obter_tarefa_servico
from app.enums import CampoOrdenacao, Ordem, PrioridadeTarefa, StatusTarefa
from app.models import Tarefa
from app.repositories import FiltroDeTarefas
from app.schemas import TarefaCreate, TarefaOut, TarefaUpdate
from app.services import AlteracoesDaTarefa, TarefaServico

router = APIRouter(prefix="/tarefas", tags=["tarefas"])


@router.post(
    "",
    response_model=TarefaOut,
    status_code=status.HTTP_201_CREATED,
    summary="criar tarefa",
    responses={404: {"description": "Usuario nao encontrado!"}},
)
def criar_tarefa(
    dados: TarefaCreate,
    servico: Annotated[TarefaServico, Depends(obter_tarefa_servico)],
) -> TarefaOut:
    return servico.criar(
        usuario_id=dados.usuario_id,
        titulo=dados.titulo,
        prioridade=dados.prioridade,
        prazo=dados.prazo,
    )


def _montar_alteracoes(dados: TarefaUpdate) -> AlteracoesDaTarefa:
    return AlteracoesDaTarefa(**dados.model_dump(exclude_unset=True))


@router.get(
    "",
    response_model=list[TarefaOut],
    summary="Listar tarefas",
)
def listar_tarefas(
    usuario_id: Annotated[int, Query(description="ID do usuário")],
    servico: Annotated[TarefaServico, Depends(obter_tarefa_servico)],
    status_tarefa: Annotated[
        StatusTarefa | None,
        Query(alias="status", description="Status da tarefa para filtrar"),
    ] = None,
    prioridade: Annotated[
        PrioridadeTarefa | None,
        Query(description="Prioridade da tarefa para filtrar"),
    ] = None,
    prazo_ate: Annotated[
        date | None,
        Query(alias="prazoAte", description="Filtra tarefas com prazo até esta data"),
    ] = None,
    ordenar_por: Annotated[
        CampoOrdenacao,
        Query(alias="ordenarPor", description="Campo usado na ordenação"),
    ] = CampoOrdenacao.CRIADO_EM,
    ordem: Annotated[
        Ordem,
        Query(description="Sentido da ordenação"),
    ] = Ordem.DESC,
    limite: Annotated[int, Query(description="Quantidade máxima de itens retornados")] = 50,
    deslocamento: Annotated[int, Query(description="Número de itens ignorados na paginação")] = 0,
) -> list[Tarefa]:
    filtro = FiltroDeTarefas(
        usuario_id=usuario_id,
        status=status_tarefa,
        prioridade=prioridade,
        prazo_ate=prazo_ate,
        ordenar_por=ordenar_por,
        ordem=ordem,
        limite=limite,
        deslocamento=deslocamento,
    )
    return servico.listar(filtro)


@router.get(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Buscar tarefa",
    responses={404: {"description": "Tarefa nao encontrada!"}},
)
def buscar_tarefa(
    tarefa_id: int,
    servico: Annotated[TarefaServico, Depends(obter_tarefa_servico)],
) -> TarefaOut:
    return servico.buscar(tarefa_id)


@router.patch(
    "/{tarefa_id}",
    response_model=TarefaOut,
    summary="Atualizar tarefa",
    responses={404: {"description": "Tarefa nao encontrada!"}},
)
def atualizar_tarefa(
    tarefa_id: int,
    dados: TarefaUpdate,
    servico: Annotated[TarefaServico, Depends(obter_tarefa_servico)],
) -> TarefaOut:
    return servico.atualizar(tarefa_id, _montar_alteracoes(dados))


@router.delete(
    "/{tarefa_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar tarefa",
    responses={404: {"description": "Tarefa nao encontrada!"}},
)
def remover_tarefa(
    tarefa_id: int,
    servico: Annotated[TarefaServico, Depends(obter_tarefa_servico)],
    response: Response,
) -> None:
    servico.remover(tarefa_id)
    response.status_code = status.HTTP_204_NO_CONTENT
    return None

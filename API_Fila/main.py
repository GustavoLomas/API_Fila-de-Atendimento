from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Literal
import uvicorn

MyApp = FastAPI()

class Fila(BaseModel):
    id: int     
    nome: str
    Dt_Entrada: str
    Atendido: bool = False
    Tp_Atendimento: Literal ['Normal', 'Preferencial']

db_FilaClientes = [
    Fila(id=1, nome="Gustavo", Dt_Entrada='24/11/2024', Atendido=False, Tp_Atendimento='Normal'),
    Fila(id=2, nome="Brenner", Dt_Entrada='24/11/2024', Atendido=False, Tp_Atendimento='Normal'),
    Fila(id=3, nome="Camila", Dt_Entrada='24/11/2024', Atendido=False, Tp_Atendimento='Normal'),
    Fila(id=4, nome="Isabella", Dt_Entrada='24/11/2024', Atendido=False, Tp_Atendimento='Normal'),
]

@MyApp.get("/")
async def root():
    return {"message": "Bem vindo ao MyApp, gerenciador de filas "}

@MyApp.get("/fila/", status_code=status.HTTP_200_OK)
async def exibir_fila():
    Fila_Atual = [fila_exibe for fila_exibe in db_FilaClientes if fila_exibe.Atendido == False]
    if not Fila_Atual:
        return {}
    Fila_Atual = sorted(Fila_Atual, key=lambda x: x.id)
    return [{"Posição": cliente.id, "Nome": cliente.nome, "Dt_Entrada": cliente.Dt_Entrada} for cliente in Fila_Atual]


@MyApp.get("/fila/{id}", status_code=status.HTTP_200_OK)
async def mostra_cliente(id: int):
    cliente_escolhido = [clt for clt in db_FilaClientes if clt.id == id]
    if not cliente_escolhido:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    return {
        "Cliente": {
            "Posição": cliente_escolhido[0].id,
            "Nome": cliente_escolhido[0].nome,
            "Dt_Entrada": cliente_escolhido[0].Dt_Entrada
        }
    }

@MyApp.post("/fila/", status_code=status.HTTP_201_CREATED)
async def adiciona_cliente(novo_cliente: Fila):
    if len(novo_cliente.nome) > 20:
        raise HTTPException(status_code=400, detail="Nome deve ter no máximo 20 caracteres.")
    
    novo_cliente.id = len(db_FilaClientes) + 1
    if novo_cliente.Tp_Atendimento == 'Preferencial':
        pos_ultimo_prioritario = -1
        for idx, cliente in enumerate(db_FilaClientes):
            if cliente.Tp_Atendimento == 'Preferencial':
                pos_ultimo_prioritario = idx
        if pos_ultimo_prioritario != -1:
            db_FilaClientes.insert(pos_ultimo_prioritario + 1, novo_cliente)
        else:
            db_FilaClientes.insert(0, novo_cliente)
    else:
        db_FilaClientes.append(novo_cliente)
    for idx, cliente in enumerate(db_FilaClientes, start=1):
        cliente.id = idx

    return {"mensagem": f"Cliente '{novo_cliente.nome}' adicionado com sucesso!", "ID": novo_cliente.id}

@MyApp.put("/fila/", status_code=status.HTTP_200_OK)

async def atualizar_fila():
    if not db_FilaClientes:
        raise HTTPException(status_code=404, detail="Fila vazia.")
    for cliente in db_FilaClientes:
        if cliente.id > 1:
            cliente.id -= 1
        else:
            cliente.Atendido = True

    return {"mensagem": "Fila atualizada com sucesso!"}

@MyApp.delete("/fila/{id}", status_code=status.HTTP_200_OK)

async def remover_cliente(id: int):
    cliente_removido = None
    for cliente in db_FilaClientes:
        if cliente.id == id:
            cliente_removido = cliente
            db_FilaClientes.remove(cliente)
            break
    if not cliente_removido:
        raise HTTPException(status_code=404, detail="Cliente não encontrado.")
    for cliente in db_FilaClientes:
        if cliente.id > id:
            cliente.id -= 1
    return {"mensagem": "Cliente removido. Fila atualizada com sucesso!"}
if __name__== "__main__":
    uvicorn.run(MyApp, port=8000)
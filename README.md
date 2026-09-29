# Gestão de Devoluções

Aplicação em Streamlit para acompanhar devoluções em três etapas: Comercial, Logística e Garantia da Qualidade.

## Requisitos

- Python 3.10 ou superior
- Arquivos Excel de dados na pasta `data/`

## Instalação e execução

No terminal, na raiz do repositório:

```bash
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux ou macOS
source .venv/bin/activate
```

Instale as dependências e inicie o app:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Arquivos de dados

Coloque os arquivos abaixo na pasta `data/` antes de iniciar a aplicação:

- `fato_devolucoes.xlsx`
- `dim_clientes.xlsx`
- `dim_produtos.xlsx`

Os cadastros de dimensão devem conter `ID_Cliente` e `Nome_Cliente`, ou `ID_Produto` e `Nome_Produto`, respectivamente. A tabela fato deve conter as colunas `COM_ID_Devolucao`, `COM_ID_Cliente`, `COM_ID_Produto`, `LOG_Transportadora` e `QUA_Status_Qualidade`. O app adiciona as colunas obrigatórias ausentes ao carregar e acrescenta os campos dos formulários quando necessário.

Os arquivos `.xlsx` e `.xls` são ignorados pelo Git para evitar publicar dados de clientes e da operação. Obtenha esses arquivos por um canal seguro e mantenha-os localmente em `data/`.

## Etapas do fluxo

1. **Comercial** registra a devolução, selecionando cliente e produto pelos nomes dos cadastros.
2. **Logística** vê os registros sem transportadora e informa os dados do transporte.
3. **Qualidade** vê os registros com transportadora e sem status de qualidade e registra o laudo.

Após cada gravação, o arquivo `data/fato_devolucoes.xlsx` é atualizado e a tela recarrega para refletir a fila atual.

## Organização do código

- `app.py`: entrada do Streamlit.
- `devolucoes/application.py`: inicialização, carregamento dos dados e navegação.
- `devolucoes/config.py`: caminhos e colunas essenciais.
- `devolucoes/repositories/excel_repository.py`: leitura e gravação dos arquivos Excel.
- `devolucoes/services/workflow_service.py`: regras de criação, filas e transições.
- `devolucoes/ui/`: formulários compartilhados e uma tela por etapa.
- `tests/`: testes das regras, persistência e inicialização das telas.

## Testes

Com as dependências instaladas e na raiz do projeto, execute:

```bash
python -m unittest discover -v
```

Os testes exercitam a seleção das filas, geração sequencial de IDs, transição entre etapas, junção dos nomes das dimensões, leitura e gravação Excel temporária e renderização dos três perfis Streamlit.

## Observação sobre armazenamento

O Excel é adequado para uso local ou demonstração. Como o arquivo é compartilhado e sobrescrito, múltiplas gravações simultâneas podem conflitar. Para publicação com vários usuários, use um armazenamento transacional com controle de acesso e migre a persistência para um banco de dados.

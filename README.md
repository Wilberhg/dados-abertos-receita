# Dados Abertos Receita

Projeto de ingestão e processamento de dados públicos com foco em arquitetura limpa.

## Estrutura principal

- `app/main.py` - entrada do pipeline mensal.
- `app/services/monthly_service.py` - orquestra a extração e conversão de arquivos.
- `app/infra` - implementações de infraestrutura, incluindo API e manipulação de arquivos.
- `app/models` - entidades de domínio.
- `app/repositories` - persistência de dados.
- `app/business` - regras de negócio e casos de uso.

## Boas práticas aplicadas

- injeção de dependências para desacoplamento
- modelos de domínio em vez de dicionários soltos
- abstrações de portas (`ports`) para facilitar testes e substituição de implementações
- logging centralizado

## Executar

```bash
python main.py
```

## Observações

- Arquivos de entrada são esperados em `data/input/clientes.json`.
- A implementação de `buscar_cliente` em `app/infra/api/dados_abertos.py` é atualmente um placeholder e deve ser adaptada ao endpoint real.
# dados-abertos-receita

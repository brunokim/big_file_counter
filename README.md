# big_file_counter
Implementação do desafio de contar elementos com memória limitada

Leia o post: https://medium.com/@brunokim-mc/python-e-um-cont%C3%AAiner-sem-mem%C3%B3ria-3bea4d6b96e4

## Comandos

Cria a imagem Docker `big_file_counter`. Isso pode demorar um pouco pois são criados 3 arquivos com 100 MiB para exercitar o contador.

```sh
$ make build
```

Executa o contador sobre um dos arquivos. Você provavelmente vai querer modificar o comando para testar outras hipóteses.

```sh
$ make run
```

## Dependências

O projeto foi escrito com Python 3.10 e utiliza as dependências listadas em `requirements.txt` -- a saber, apenas a biblioteca
[`SortedContainers`](https://www.grantjenks.com/docs/sortedcontainers/).

## Arquivos

- `human_size.py`: Pacote que converte entre uma string como `"10 MiB"` e o número de bytes correspondente. 
- `make_file.py`: Ferramenta CLI que cria um arquivo com tamanho `--size`, contendo `--num_elements` elementos distintos.
- `runtime.py`: Pacote com utilitários para observar e reportar o uso de memória dentro de um container.
- `count_file_lines.py`: Ferramenta CLI que conta a frequência de linhas do arquivo passado, buscando usar no máximo `--max_memory_occupancy` da memória
   disponível

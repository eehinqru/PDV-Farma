# PDV Pharmacy

# Como executar o programa

## 1. Crie uma venv (Virtual Environment) para executar

```
python -m venv .venv
```

<br>

## 2. Selecione o ambiente


###  <ins>Windows</ins>

Abra o arquivo **activate.bat** dentro de:

```
.venv/Scripts/activate.bat
```

### <ins>Linux ou MacOS</ins>

Execute o comando **source** com o seguinte diretório:

```
source .venv/bin/activate
```

<br>


# 3. Baixe as dependências

```
pip install -r requirements.txt
```

<br>


# 4. Execute o programa

```
python PDVfarma/manage.py runserver 0.0.0.0:8000
```
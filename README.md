# Sistema de Cadastro e Geração de PDF

Aplicação web profissional desenvolvida em Python (Flask) para cadastro de usuários e geração automática de relatórios em PDF. O sistema conta com validações robustas, interface moderna e responsiva.

## Funcionalidades

### Frontend (Interface Web)
*   **Design Profissional**: Interface limpa e responsiva utilizando **Bootstrap 5**.
*   **Validação em Tempo Real**: Feedback imediato para o usuário enquanto preenche os campos.
*   **Máscaras de Entrada**: Formatação automática para CPF, Telefone e CEP.
*   **Acessibilidade**: Estrutura HTML semântica compatível com WCAG 2.1.
*   **Persistência Local**: Funcionalidade "Salvar Rascunho" que armazena os dados no navegador para não perder o preenchimento.

### Backend (Python/Flask)
*   **Validação de Dados**: Verificação de CPF (algoritmo oficial), idade mínima (18 anos) e consistência de emails.
*   **Geração de PDF**: Motor de renderização utilizando **ReportLab** para criar documentos PDF elegantes e bem formatados.
*   **Segurança**: Sanitização de entradas e tratamento de erros.

## Campos do Formulário

*   **Dados Pessoais**: Nome Completo, CPF, RG, Data de Nascimento, Gênero, Estado Civil, Nome da Mãe, Profissão.
*   **Contato**: Email (com confirmação), Telefone Celular.
*   **Endereço**: CEP, Logradouro, Número, Complemento, Bairro, Cidade, Estado.
*   **Outros**: Campo de observação com contador de caracteres.

## Como Executar

1.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Inicie o servidor**:
    ```bash
    python app.py
    ```

3.  **Acesse a aplicação**:
    Abra o navegador em `http://127.0.0.1:5000`

## Estrutura de Arquivos

*   `app.py`: Controlador principal (Backend).
*   `pdf_generator.py`: Lógica de criação do PDF.
*   `templates/index.html`: Interface do usuário.
*   `static/js/script.js`: Lógica de validação e máscaras no cliente.
*   `static/css/`: Estilos personalizados (opcional).

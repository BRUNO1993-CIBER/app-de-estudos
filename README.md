# 📚 Gestão de Estudos Pro

Um aplicativo desktop desenvolvido em **Python** para gerenciamento de estudos focado em produtividade e consistência. O sistema utiliza a técnica **Pomodoro** e gerencia automaticamente a rotação de matérias, salvando todo o progresso em um banco de dados local.

## 🚀 Funcionalidades

- **⏱️ Timer Pomodoro:** Cronômetro integrado de 25 minutos para foco total.
- **🔄 Rotação Automática:** Gerenciamento inteligente de matérias (Matemática, História, Física, etc.).
- **📊 Ciclos de Estudo:** Contagem automática de ciclos. Ao completar 4 ciclos (100 min), o sistema sugere avançar para a próxima matéria ou continuar.
- **📈 Relatório de Desempenho:** Histórico detalhado com tempos líquidos de estudo por matéria e data.
- **💾 Persistência de Dados:** Tudo é salvo automaticamente em banco de dados SQLite (não perde dados ao fechar).
- **🎨 Interface Gráfica:** Interface limpa e intuitiva construída com Tkinter.

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Interface (GUI):** Tkinter (Nativo)
- **Banco de Dados:** SQLite3
- **Estrutura:** Arquitetura Modular (Frontend separado do Backend)

## 📂 Estrutura do Projeto

O projeto foi refatorado para ser modular e fácil de manter:

| Arquivo | Função |
|---|---|
| `app.py` | **Frontend:** Responsável por toda a interface visual, botões, janelas e interação com o usuário. |
| `backend.py` | **Backend:** Responsável pela lógica de negócio, regras do Pomodoro e conexões com o banco de dados. |
| `study_plans_v2.db` | **Database:** Arquivo gerado localmente para salvar seus estudos (ignorado pelo Git para privacidade). |

## 🔧 Como Executar

Certifique-se de ter o **Python 3** instalado em sua máquina.

1. Clone o repositório:
    ```bash
    git clone https://github.com/BRUNO1993-CIBER/app-de-estudos.git
    ```
2. Entre na pasta do projeto:
    ```bash
    cd app-de-estudos
    ```
3. Execute o aplicativo:
    ```bash
    python app.py
    ```

Nota: o banco de dados será criado automaticamente na primeira execução.

## 📝 Como Contribuir

- Faça um Fork do projeto.
- Crie uma branch para sua feature:
  ```bash
  git checkout -b feature/NovaFeature
  ```
- Faça commits claros e atômicos:
  ```bash
  git commit -m "Descreva a mudança"
  ```
- Faça push para sua branch:
  ```bash
  git push origin feature/NovaFeature
  ```
- Abra um Pull Request descrevendo a mudança.

Desenvolvido por BRUNO1993-CIBER


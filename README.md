# Painel Biblioteca 2026

Painel de progresso do projeto didático Biblioteca 2026 (Turmas A e B), publicado via GitHub Pages.

- **Painel:** https://ensismoebius.github.io/biblioteca_2Mtec_2026_dashboard/
- **Dados de:** [biblioteca_2Mtec_2026_A](https://github.com/ensismoebius/biblioteca_2Mtec_2026_A) e [biblioteca_2Mtec_2026_B](https://github.com/ensismoebius/biblioteca_2Mtec_2026_B)
- **Atualização:** uma GitHub Action (`.github/workflows/refresh.yml`) roda todo domingo às 23:00 UTC (20:00 horário de Brasília), coleta issues/milestones dos dois repositórios via API pública do GitHub e faz commit do `index.html` atualizado. Também pode ser disparada manualmente na aba Actions (`workflow_dispatch`).
- **Story points:** somados a partir da label `esforço: N` em cada issue.

Este repositório contém apenas o painel — nenhum código do projeto Laravel.

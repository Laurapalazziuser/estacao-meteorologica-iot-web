# estacao-meteorologica-iot-web
## 🧩 Divisão de Arquitetura (Projeto em Equipe)

Este ecossistema foi desenvolvido de forma modular em equipe, consumindo a mesma base de dados via REST API:

* **Circuito & Firmware IoT (Minha autoria):** Coleta de grandezas físicas com ESP32-S3 e exibição local no LCD 20x4 (`firmware-wokwi/`).
* **Portal Web Público (Minha autoria):** Interface acessível ao cidadão com animações climáticas e tabelas históricas (`web-dashboard/`).
* **Dashboard Analítico (Desenvolvido por colega de equipe):** Módulo complementar focado em gráficos gerenciais e análise estatística dos dados coletados pela estação.

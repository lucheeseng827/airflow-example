# 🚀 Airflow Learning Hub

A comprehensive, hands-on repository for **DevOps Engineers**, **ML Engineers**, and **Data Engineers** to learn Apache Airflow from fundamentals to advanced pipeline orchestration.

[![CI](https://github.com/lucheeseng827/airflow-example/workflows/CI/badge.svg)](https://github.com/lucheeseng827/airflow-example/actions)
[![Lint](https://github.com/lucheeseng827/airflow-example/workflows/Lint/badge.svg)](https://github.com/lucheeseng827/airflow-example/actions)
[![Format](https://github.com/lucheeseng827/airflow-example/workflows/Format%20Check/badge.svg)](https://github.com/lucheeseng827/airflow-example/actions)

## 📚 What You'll Learn

This repository provides practical, production-ready examples for:

- **Building Data Pipelines**: ETL/ELT workflows for data processing
- **ML Pipeline Orchestration**: Training, evaluation, and deployment workflows
- **DevOps Automation**: CI/CD, infrastructure provisioning, and monitoring
- **Monitoring & Observability**: Track pipeline health and performance
- **Notifications & Alerts**: Slack, Email, PagerDuty integrations
- **Cloud Integrations**: AWS, GCP, Azure service orchestration
- **Best Practices**: Testing, code quality, and production patterns

## 🎯 Who This Is For

### DevOps Engineers
Learn to automate infrastructure provisioning, deployments, backup jobs, and monitoring workflows.

### ML Engineers
Discover how to orchestrate model training, hyperparameter tuning, feature engineering, and model deployment pipelines.

### Data Engineers
Master building robust ETL/ELT pipelines, data quality checks, and data warehouse orchestration.

## 🗂️ Repository Structure

```
airflow-example/
├── dags/                          # DAG examples organized by use case
│   ├── 01_basics/                # Getting started with Airflow
│   ├── 02_devops/                # DevOps automation examples
│   ├── 03_ml_pipelines/          # Machine Learning workflows
│   ├── 04_data_engineering/      # Data pipeline examples
│   ├── 05_monitoring/            # Monitoring and observability
│   ├── 06_notifications/         # Alert and notification patterns
│   └── 07_integrations/          # Cloud and third-party integrations
├── docs/                          # Learning guides and tutorials
│   ├── getting-started.md        # Airflow fundamentals
│   ├── operators-guide.md        # Understanding operators
│   ├── monitoring-guide.md       # Monitoring best practices
│   ├── testing-guide.md          # Testing your DAGs
│   └── best-practices.md         # Production-ready patterns
├── plugins/                       # Custom operators and hooks
├── test/                          # Unit and integration tests
├── requirements.txt               # Core dependencies
├── requirements-dev.txt           # Development tools
└── pyproject.toml                # Linting and formatting config
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda
- (Optional) Docker for local Airflow instance

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/lucheeseng827/airflow-example.git
   cd airflow-example
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Initialize Airflow database**
   ```bash
   export AIRFLOW_HOME=$(pwd)
   airflow db init
   airflow users create \
       --username admin \
       --firstname Admin \
       --lastname User \
       --role Admin \
       --email admin@example.com
   ```

5. **Start Airflow**
   ```bash
   # Terminal 1: Start the webserver
   airflow webserver --port 8080

   # Terminal 2: Start the scheduler
   airflow scheduler
   ```

6. **Access the UI**
   Navigate to `http://localhost:8080` and log in with your credentials.

## 📖 Learning Path

### Level 1: Fundamentals (Start Here!)
1. [Getting Started Guide](docs/getting-started.md)
2. [Understanding DAGs](dags/01_basics/)
3. [Operators Overview](docs/operators-guide.md)
4. [Basic Examples](dags/01_basics/basic_dag.py)

### Level 2: Use Case Examples
- **DevOps**: [CI/CD Pipelines](dags/02_devops/), [Infrastructure Automation](dags/02_devops/)
- **ML Engineering**: [Model Training](dags/03_ml_pipelines/), [Feature Engineering](dags/03_ml_pipelines/)
- **Data Engineering**: [ETL Workflows](dags/04_data_engineering/), [Data Quality](dags/04_data_engineering/)

### Level 3: Advanced Topics
- [Monitoring & Alerting](dags/05_monitoring/)
- [Custom Notifications](dags/06_notifications/)
- [Cloud Integrations](dags/07_integrations/)
- [Testing Best Practices](docs/testing-guide.md)
- [Production Patterns](docs/best-practices.md)

## 🔔 Example Use Cases

### DevOps Automation
- **CI/CD Pipeline**: Trigger builds, run tests, deploy applications
- **Backup Automation**: Schedule database and file backups
- **Infrastructure Monitoring**: Health checks and auto-remediation
- **Log Aggregation**: Collect and process logs from multiple sources

### ML Pipeline Orchestration
- **Model Training**: Automated training workflows with hyperparameter tuning
- **Feature Engineering**: Daily feature computation and storage
- **Model Evaluation**: A/B testing and performance tracking
- **Deployment Pipeline**: Model validation and deployment to production

### Data Engineering
- **ETL Workflows**: Extract from APIs, transform data, load to warehouse
- **Data Quality Checks**: Automated validation and anomaly detection
- **Data Lake Management**: Organize and partition data efficiently
- **Real-time Processing**: Stream processing with Kafka integration

## 🛠️ Key Features & Integrations

### Monitoring & Observability
- DAG execution tracking
- Task duration monitoring
- Failure detection and alerting
- Custom metrics and logging

### Notification Channels
- **Slack**: Real-time alerts to channels
- **Email**: Detailed failure reports
- **PagerDuty**: Critical incident escalation
- **Custom Webhooks**: Integration with any service

### Cloud Integrations
- **AWS**: S3, EMR, Redshift, Lambda, SageMaker
- **GCP**: BigQuery, Cloud Storage, Dataflow
- **Azure**: Blob Storage, Data Factory
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis

## 🧪 Testing & Quality

```bash
# Run linter
ruff check dags/ test/

# Format code
ruff format dags/ test/

# Run tests
pytest test/ -v

# Validate DAGs
python -c "from airflow.models import DagBag; DagBag('dags/')"
```

## 📊 Monitoring Your Pipelines

Learn to implement comprehensive monitoring:

1. **Execution Metrics**: Track task duration, success rates, and retries
2. **Custom Alerts**: Configure alerts for specific failure patterns
3. **SLA Monitoring**: Set and track Service Level Agreements
4. **Performance Dashboards**: Visualize pipeline performance over time

See [Monitoring Guide](docs/monitoring-guide.md) for details.

## 🎓 Additional Resources

### Official Documentation
- [Apache Airflow Docs](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

### Community
- [Airflow Slack](https://apache-airflow-slack.herokuapp.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/airflow)

### Tutorials & Blogs
- [Astronomer Guides](https://docs.astronomer.io/learn)
- [Testing in Airflow](https://blog.usejournal.com/testing-in-airflow-part-1-dag-validation-tests-dag-definition-tests-and-unit-tests-2aa94970570c)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Ensure all tests pass and code is properly formatted:
```bash
ruff check dags/ test/
ruff format dags/ test/
pytest test/
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Apache Airflow community
- Contributors and maintainers
- All learners using this repository

---

**Ready to start?** Head to [Getting Started Guide](docs/getting-started.md) 🚀

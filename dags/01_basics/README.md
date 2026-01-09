# 01 - Basics

Introduction to Airflow fundamentals. Start here if you're new to Airflow!

## Examples in This Directory

### basic_dag.py
**Difficulty:** Beginner
**Topics:** DAG definition, Task creation, Dependencies, Templating

Learn the fundamentals:
- How to define a DAG
- Create tasks with different operators
- Set task dependencies
- Use Jinja templating

**Run it:**
```bash
airflow dags test basic_example 2024-01-01
```

### tutorial_adding_files.py (Original)
**Difficulty:** Beginner
**Topics:** BashOperator, Task dependencies, Templating

Original tutorial DAG showing:
- Basic task creation
- Bash commands
- Templated commands with Jinja
- Setting task dependencies

### tutorial_sync_s3.py (Original)
**Difficulty:** Beginner
**Topics:** AWS S3, BashOperator, Scheduling

Simple S3 sync example:
- Scheduled execution
- S3 sync operations
- Task dependencies

## Learning Path

1. **Read** [Getting Started Guide](../../docs/getting-started.md)
2. **Study** `basic_dag.py` to understand core concepts
3. **Experiment** by modifying the examples
4. **Test** your DAGs: `airflow dags test <dag_id> <execution_date>`

## Key Concepts Covered

- **DAG**: Directed Acyclic Graph - the workflow definition
- **Operators**: Define what each task does (BashOperator, PythonOperator)
- **Tasks**: Individual units of work
- **Dependencies**: Define execution order (`>>` operator)
- **Scheduling**: When and how often DAGs run
- **Templating**: Dynamic values using Jinja (`{{ ds }}`, `{{ execution_date }}`)

## Next Steps

Once you're comfortable with these basics:
- Explore [DevOps Examples](../02_devops/) for automation workflows
- Check out [ML Pipeline Examples](../03_ml_pipelines/) for machine learning
- Review [Data Engineering Examples](../04_data_engineering/) for ETL patterns

## Common Commands

```bash
# List all DAGs
airflow dags list

# Test a DAG without scheduling
airflow dags test basic_example 2024-01-01

# List tasks in a DAG
airflow tasks list basic_example

# Test a specific task
airflow tasks test basic_example print_date 2024-01-01

# Trigger a DAG run
airflow dags trigger basic_example

# View DAG structure
airflow dags show basic_example
```

## Troubleshooting

**DAG not showing in UI?**
- Check for Python syntax errors
- Ensure file is in `dags/` directory
- Wait for scheduler to parse (default: 5 minutes)

**Task failing?**
- Check task logs in the Airflow UI
- Test task individually: `airflow tasks test <dag_id> <task_id> <date>`
- Verify all dependencies are installed

## Resources

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Operators Guide](../../docs/operators-guide.md)
- [Best Practices](../../docs/best-practices.md)

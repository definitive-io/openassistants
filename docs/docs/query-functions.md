---
sidebar_position: 3
---

# Query functions

One of the key ideas in OpenAssistants is the ability to dynamically populate the chat context with dynamic information.

One of the ways in which we support that is through the integrated SQL functions, such as the `DuckDBQueryFunction`.

Here's an example YAML that uses the `DuckDBQueryFunction` to pull in data from multiple CSV files that are part of our application.

```yaml
name: show_recent_purchases
display_name: Show recent purchases
description: |
  Show a list of recent purchases (last 5)
sample_questions:
- show recent purchases
parameters:
  json_schema:
    type: object
    properties: {}
    required: []
type: DuckDBQueryFunction
dataset: "dummy-data/"
sqls:
- |
  SELECT purchases.id, purchases.product, employees.email
  FROM "purchases.csv"
  INNER JOIN "employees.csv" ON purchases.employee = employees.id
  ORDER BY purchases.id DESC
  LIMIT 5
visualizations: []
summarization: 'Describe these purchases'
```

The information produced by these queries is part of the conversation after use and can be used by the LLM to call other functions.
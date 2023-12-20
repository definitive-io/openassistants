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
  Show a list of recent purchases (i.e. "Show recent Tesla purchases")
sample_questions:
  - Show recent Tesla purchases
parameters:
  json_schema:
    type: object
    properties:
      product:
        type: string
        format: STRING
        description: product name
    required:
      - product
type: DuckDBQueryFunction
dataset: 'dummy-data/'
sqls:
  - |
    SELECT purchases.id, purchases.product, employees.email
    FROM "purchases.csv"
    INNER JOIN "employees.csv" ON purchases.employee = employees.id
    WHERE lower(purchases.product) = lower(:product)
    ORDER BY purchases.id DESC
    LIMIT 5
visualizations: []
summarization: 'Describe these purchases'
suggested_follow_ups:
  - title: Show spend per product
    prompt: Show spend per product
```

The information produced by these queries is part of the conversation after use and can be used by the LLM to call other functions. Key components:

- The `description` field is used by the LLM to semantically map user prompts to the function. A good description should resemble the ways in which the function would expect to be invoked via a prompt. If the query is parameterized, it may also be effective to include sample prompts with real parameters in the description.
- The `parameters` field describes any parameters used in the query.
- `type` is the specific function class this function instance should call.
- `dataset` is the location of the data.
- `sqls` is a list of SQL queries that should be executed on function call. Note that the specific syntax differs depending on the specific function class (i.e. DuckDB vs BigQuery). It is also good practice to make any filtering on parameters flexible (for example, case independent), because incorrectly mapped parameters can result in empty or incorrect data returned.
- The `visualizations` field takes in a list of python visualizations functions to add charts to your output.
- The `summarization` field gives additional instructions to the LLM on how to summarize the data in the output.
- `suggested_follow_ups` is a list of recommended prompts that would appear following the LLM response (`title` is what the user sees and `prompt` is the prompt that is sent to the LLM). Suggested follow-ups are useful for directing the user along an optimal path in their chat. It is good practice to write the follow-up prompt as closely to the desired function description as you can to ensure that the LLM maps to the correct function

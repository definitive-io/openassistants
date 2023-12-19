---
sidebar_position: 3
---

# Data Modeling Column Standards Guide

This guide outlines the standards for defining and describing columns in data models, based loosely on the [dbt style guide](https://github.com/dbt-labs/corp/blob/main/dbt_style_guide.md). By adhering to these standards, we ensure consistency, clarity, and ease of use across our data models, making downstream use of the OpenAssistants platform easier and more effective

### Dimension Columns

1. **Identifiers**: These columns, like `entity_id` or `account_status`, serve as unique identifiers. They are crucial for distinguishing each record.
2. **Primary Keys**: Designated primary key columns, such as `primary_key_id`, should be consistent and identifiable across tables.

### Descriptive Columns

1. **Naming**: Use descriptive names, like `customer_name` or `product_description`, that provide a clear understanding of the column's content.
2. **Data Type & Category**: Indicate the data type (e.g., `INT64` for integers, `STRING` for text, `DATE` for dates) and category, such as `metric_value` for a numeric measurement.

### Metadata Columns

1. **Alias/Derived Names**: Columns like `nickname` or `calculated_age` can offer more context or derived information.
2. **Standard Naming Conventions**: Maintain consistent naming, like always using `_at` for timestamps (e.g., `created_at`).

### Quantitative Columns

1. **Units & Scale**: For columns like `price_usd` or `temperature_celsius`, indicate the unit and scale.
2. **Aggregation Level**: Specify if the column represents aggregated data, e.g., `total_sales_sum`.

### Qualitative Columns

1. **Enumerated Values**: Columns like `order_status` should list possible values, such as `['pending', 'completed', 'cancelled']`.
2. **Labels/Tags**: Use columns like `category_tag` for categorization.

### Temporal Columns

1. **Timestamps & Dates**: Stick to formats like `YYYY-MM-DD` for date columns such as `birth_date`.
2. **Event-Specific Naming**: Reflect the event, like `last_login_at`, in the column name.

### Boolean Columns

1. **Prefixes**: Use `is_` or `has_` prefixes for clarity, such as `is_active` or `has_dependents`.
2. **Clear Meaning**: Names should clearly convey the boolean condition.

### Textual and Large Data Columns

1. **Placement**: Position large text columns like `user_comments` towards the end.
2. **Description & Length**: Provide details on the expected content and size, e.g., `VARCHAR(255)`.

### General Consistency and Clarity

1. **Avoid Reserved Names**: Stay away from system-reserved keywords like `select` or `date`.
2. **Documentation**: Include descriptions for each column, explaining its role and expected data.

By following these standards, data modelers can create models that are intuitive, reliable, and easily navigable, enhancing the overall quality and usability of the data.

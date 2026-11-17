# ShopSense Milestone 3 — Database Schema & Entity Relationships

## 1. Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    users ||--o{ vendors : owns
    users ||--o{ transactions : places
    users ||--o{ customer_wishlists : saves
    users ||--o{ product_recommendations : receives
    users ||--o| customer_insight_profiles : has
    vendors ||--o{ products : supplies
    products ||--o| inventory : tracks
    products ||--o{ transactions : ordered_in
    products ||--o{ customer_wishlists : wished
    products ||--o{ product_recommendations : recommended

    users {
        int user_id PK
        string full_name
        string email UK
        string password_hash
        enum role "ADMIN, VENDOR, CUSTOMER"
        boolean is_active
        datetime created_at
    }

    vendors {
        int vendor_id PK
        int user_id FK
        string business_name
        string contact_phone
        string category
        enum status "ACTIVE, PENDING, SUSPENDED"
        datetime created_at
    }

    products {
        int product_id PK
        int vendor_id FK
        string product_name
        string category
        decimal price
        int stock
        datetime created_at
    }

    inventory {
        int inventory_id PK
        int product_id FK
        int current_stock
        int safety_stock
        int reorder_point
        string warehouse_location
        datetime last_restocked
    }

    transactions {
        int transaction_id PK
        int user_id FK
        int product_id FK
        int vendor_id FK
        int quantity
        decimal amount
        datetime transaction_date
    }

    customer_wishlists {
        int wishlist_id PK
        int user_id FK
        int product_id FK
        datetime added_at
    }

    product_recommendations {
        int id PK
        int user_id FK
        int product_id FK
        float score
        string recommendation_type
        string segment_name
        datetime created_at
    }

    customer_insight_profiles {
        int insight_id PK
        int user_id FK
        string segment_name
        float total_spent
        int total_orders
        float aov
        int recency_days
        boolean is_frequent
        string preferred_category
        datetime updated_at
    }
```

---

## 2. Table Specifications & Cardinalities

| Table Name | Primary Key | Key Foreign Keys | Purpose |
|---|---|---|---|
| `users` | `user_id` | — | Multi-role user accounts with hashed credentials and role claim. |
| `vendors` | `vendor_id` | `user_id` $\to$ `users.user_id` | Business profiles for marketplace sellers. |
| `products` | `product_id` | `vendor_id` $\to$ `vendors.vendor_id` | Product catalog with prices, stock levels, and categories. |
| `inventory` | `inventory_id` | `product_id` $\to$ `products.product_id` | Physical stock monitoring, reorder thresholds, and warehouse bins. |
| `transactions` | `transaction_id` | `user_id`, `product_id`, `vendor_id` | Historical purchase orders (1,184 records, ₹394,559.80 total). |
| `customer_wishlists` | `wishlist_id` | `user_id`, `product_id` | Customer-saved wishlist items with timestamp. |
| `product_recommendations` | `id` | `user_id`, `product_id` | Persisted personalized product recommendations and segment rankings. |
| `customer_insight_profiles` | `insight_id` | `user_id` $\to$ `users.user_id` | Persisted RFM scores, segment names, and frequency flags. |

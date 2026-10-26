-- ==============================================================================
-- APACHE HIVE & HADOOP HDFS DATA WAREHOUSE SCHEMA DEFINITION
-- SYSTEM: Customer Complaint Big Data Intelligence Platform
-- ==============================================================================

-- 1. Create Hive Database in Hadoop Data Lake
CREATE DATABASE IF NOT EXISTS complaint_intelligence_lake
COMMENT 'Enterprise Data Lake for Customer Complaints & Service Analytics'
LOCATION '/warehouse/tablespace/external/hive/complaint_intelligence_lake.db';

USE complaint_intelligence_lake;

-- 2. External Table Mapping to Raw Ingested HDFS Files
CREATE EXTERNAL TABLE IF NOT EXISTS raw_complaints_hdfs (
    id BIGINT,
    raw_complaint STRING,
    category STRING,
    priority STRING,
    department STRING,
    created_at STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/warehouse/tablespace/external/hive/raw_complaints/';

-- 3. Partitioned & Columnar ORC Table for Optimized Big Data OLAP Queries
CREATE TABLE IF NOT EXISTS complaints_partitioned_orc (
    complaint_id BIGINT,
    complaint_text STRING,
    category STRING,
    department STRING,
    created_timestamp TIMESTAMP
)
PARTITIONED BY (
    status STRING COMMENT 'Ticket status: Pending, In Progress, Resolved',
    priority STRING COMMENT 'Urgency level: High, Medium, Low'
)
STORED AS ORC
TBLPROPERTIES (
    "orc.compress"="SNAPPY",
    "transactional"="true"
);

-- ==============================================================================
-- SAMPLE BIG DATA ANALYTICAL OLAP QUERIES (HIVEQL)
-- ==============================================================================

-- Query 1: Top Bottlenecks by Department with High Priority Complaints
SELECT 
    department,
    status,
    COUNT(*) AS total_complaints,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY department), 2) AS pct_share
FROM complaints_partitioned_orc
WHERE priority = 'High'
GROUP BY department, status
ORDER BY total_complaints DESC;

-- Query 2: Rolling 7-Day Complaint Volume with Window Function
SELECT 
    department,
    TO_DATE(created_timestamp) AS complaint_date,
    COUNT(*) AS daily_volume,
    SUM(COUNT(*)) OVER (
        PARTITION BY department 
        ORDER BY TO_DATE(created_timestamp) 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_volume
FROM complaints_partitioned_orc
GROUP BY department, TO_DATE(created_timestamp);

-- Query 3: Most Frequent Root-Cause Categories Across Critical Fraud Complaints
SELECT 
    category,
    COUNT(*) AS incident_count,
    DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) as severity_rank
FROM complaints_partitioned_orc
WHERE priority = 'High' AND status != 'Resolved'
GROUP BY category
LIMIT 10;

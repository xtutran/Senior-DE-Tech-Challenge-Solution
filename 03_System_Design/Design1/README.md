# Data Access Strategy

## 1. Database Diagram 
![alt text](../../02_Databases/ER_Diagram.png)

## 2. Requirements
This database will be used by several teams within the company to track the orders of members

- <b>Logistics</b>:
  - Get the sales details (in particular the weight of the total items bought)
  - Update the table for completed transactions

- <b>Analytics</b>:
  - Perform analysis on the sales and membership status
  - Should not be able to perform updates on any tables

- <b>Sales</b>:
  - Update database with new items
  - Remove old items from database
  
## 3. Strategy
We will have to create one account for each team with following access permission at table level:

![alt text](access_control.png)

This is just very simple strategy for the requirement. For the real case scenario, we will need more than this, for example: will need a well-defined access control permission and data classification to allow particular team to have sufficient access to data at column level.
Customer sensitive data will need to be encrypted / anonymize or masked for any data analytics purpose. Strictly follow PII and PDPA 
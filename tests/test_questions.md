# MoSPI MCP Server - ChatGPT Test Questions

**Instructions for Testing:**
1. Ask ChatGPT each question below
2. After each response, ask: "Which MCP tools did you call for this query?"
3. Record the response and tool calls in your test log

---

## 1. PLFS (Periodic Labour Force Survey)

### Basic Queries
```
Q1.1: What is the unemployment rate in Rajasthan for 2023-24?
Expected Tool: get_plfs_data
Expected Category: state (Rajasthan), indicator (UR)

Q1.2: Show me labour force participation rates for urban areas across all states in 2023-24
Expected Tool: get_plfs_data
Expected Category: sector (Urban), indicator (LFPR)

Q1.3: What are the employment statistics for females in rural Karnataka for Q1 2023-24?
Expected Tool: get_plfs_data
Expected Category: state (Karnataka), sector (Rural), sex/gender (Female)

Q1.4: Compare unemployment rates between males and females in Delhi for 2023-24
Expected Tool: get_plfs_data (called twice, or with both gender codes)
Expected Category: state (Delhi), sex/gender (Male & Female)

Q1.5: What is the worker population ratio for people with higher education in urban areas?
Expected Tool: get_plfs_data
Expected Category: sector (Urban), education (higher education), indicator (WPR)
```

### Lookup Queries
```
Q1.6: What are all the PLFS state codes available?
Expected Tool: lookup_mospi_codes
Expected Category: State

Q1.7: Show me all education level categories in PLFS
Expected Tool: lookup_mospi_codes
Expected Category: Education

Q1.8: What indicator codes are available in PLFS?
Expected Tool: lookup_mospi_codes or know_about_mospi_api
```

---

## 2. CPI (Consumer Price Index)

### Basic Queries
```
Q2.1: What was the CPI for food items in Maharashtra in January 2024?
Expected Tool: get_cpi_group_index
Expected Category: state (Maharashtra), time_period (2024-01), commodity_group (food)

Q2.2: Show me rural CPI trends for all commodity groups in 2023
Expected Tool: get_cpi_group_index
Expected Category: sector (Rural), time_period (2023)

Q2.3: What is the current CPI for housing in urban Tamil Nadu?
Expected Tool: get_cpi_group_index
Expected Category: state (Tamil Nadu), sector (Urban), commodity_group (housing)

Q2.4: Compare CPI between rural and urban sectors for Uttar Pradesh in December 2023
Expected Tool: get_cpi_group_index (called multiple times or with both sectors)
Expected Category: state (Uttar Pradesh), sector (Rural & Urban), time_period (2023-12)

Q2.5: What was the inflation rate for fuel commodities across all states in Q4 2023?
Expected Tool: get_cpi_group_index
Expected Category: commodity_group (fuel), time_period (2023-10 to 2023-12)
```

### Lookup Queries
```
Q2.6: What are the CPI state codes?
Expected Tool: lookup_mospi_codes
Expected Category: State_code

Q2.7: Show me all commodity groups available in CPI
Expected Tool: lookup_mospi_codes
Expected Category: Group_code

Q2.8: What sub-commodity categories exist for food items?
Expected Tool: lookup_mospi_codes
Expected Category: Subgroup_code
```

---

## 3. IIP (Index of Industrial Production)

### Basic Queries
```
Q3.1: What was the industrial production index for manufacturing sector in 2023?
Expected Tool: get_iip_monthly
Expected Category: industry (manufacturing), time_period (2023)

Q3.2: Show me IIP trends for consumer goods for the last 6 months
Expected Tool: get_iip_monthly
Expected Category: use_based (consumer goods), time_period (recent months)

Q3.3: What is the IIP for electricity generation in January 2024?
Expected Tool: get_iip_monthly
Expected Category: industry (electricity), time_period (2024-01)

Q3.4: Compare IIP between mining and manufacturing sectors in 2023
Expected Tool: get_iip_monthly
Expected Category: industry (mining & manufacturing), time_period (2023)

Q3.5: What was the production index for capital goods in Q3 2023?
Expected Tool: get_iip_monthly
Expected Category: use_based (capital goods), time_period (2023-Q3)
```

### Lookup Queries
```
Q3.6: What industry categories are available in IIP?
Expected Tool: lookup_mospi_codes
Expected Category: Category

Q3.7: Show me all use-based classifications in IIP
Expected Tool: lookup_mospi_codes
Expected Category: Subcategory
```

---

## 4. ASI (Annual Survey of Industries)

### Basic Queries
```
Q4.1: What is the factory output in Gujarat for 2022-23?
Expected Tool: get_asi_data
Expected Category: state (Gujarat), year (2022-23)

Q4.2: Show me employment statistics in textile industry across India for 2022-23
Expected Tool: get_asi_data
Expected Category: nic_code (textile), indicator (employment)

Q4.3: What was the gross value added in Maharashtra's manufacturing sector for 2021-22?
Expected Tool: get_asi_data
Expected Category: state (Maharashtra), year (2021-22), indicator (GVA)

Q4.4: Compare number of factories between Tamil Nadu and Karnataka in 2022-23
Expected Tool: get_asi_data
Expected Category: state (Tamil Nadu & Karnataka), year (2022-23), indicator (factories)

Q4.5: What is the total investment in chemical industry for 2022-23?
Expected Tool: get_asi_data
Expected Category: nic_code (chemical), year (2022-23), indicator (investment)
```

### Lookup Queries
```
Q4.6: What are the ASI state codes?
Expected Tool: lookup_mospi_codes
Expected Category: State_code

Q4.7: Show me all NIC industry codes available in ASI
Expected Tool: lookup_mospi_codes
Expected Category: NIC

Q4.8: What indicators are tracked in ASI?
Expected Tool: lookup_mospi_codes
Expected Category: Indicator
```

---

## 5. WPI (Wholesale Price Index)

### Basic Queries
```
Q5.1: What was the wholesale price index for agricultural products in March 2024?
Expected Tool: get_wpi_records
Expected Category: commodity (agriculture), time_period (2024-03)

Q5.2: Show me WPI trends for fuel items in 2023
Expected Tool: get_wpi_records
Expected Category: commodity (fuel), time_period (2023)

Q5.3: What is the current WPI for manufactured products?
Expected Tool: get_wpi_records
Expected Category: commodity (manufactured)

Q5.4: Compare WPI between food articles and manufactured products in January 2024
Expected Tool: get_wpi_records
Expected Category: commodity (food & manufactured), time_period (2024-01)

Q5.5: What was the wholesale inflation for minerals in Q4 2023?
Expected Tool: get_wpi_records
Expected Category: commodity (minerals), time_period (2023-10 to 2023-12)
```

### Lookup Queries
```
Q5.6: What are the major commodity groups in WPI?
Expected Tool: lookup_mospi_codes
Expected Category: Majorgroup_code

Q5.7: Show me all subcommodity categories under food items
Expected Tool: lookup_mospi_codes
Expected Category: Subgroup_code

Q5.8: What specific items are tracked under manufactured goods?
Expected Tool: lookup_mospi_codes
Expected Category: Item_code
```

---

## 6. NAS (National Accounts Statistics)

### Basic Queries
```
Q6.1: What was India's GDP growth rate in 2023-24?
Expected Tool: get_nas_data
Expected Category: indicator (GDP), year (2023-24)

Q6.2: Show me quarterly GDP estimates for FY 2023-24
Expected Tool: get_nas_data
Expected Category: indicator (GDP), year (2023-24), frequency (Quarterly)

Q6.3: What is the GVA for agriculture sector in 2023-24?
Expected Tool: get_nas_data
Expected Category: indicator (GVA), sector (agriculture), year (2023-24)

Q6.4: Compare GDP by production and expenditure approach for 2022-23
Expected Tool: get_nas_data
Expected Category: indicator (GDP), year (2022-23), approach (production & expenditure)

Q6.5: What was the per capita income in 2023-24?
Expected Tool: get_nas_data
Expected Category: indicator (per capita income), year (2023-24)
```

### Lookup Queries
```
Q6.6: What indicators are available in NAS?
Expected Tool: lookup_mospi_codes
Expected Category: Indicator

Q6.7: Show me all industry sectors tracked in NAS
Expected Tool: lookup_mospi_codes
Expected Category: Industry
```

---

## 7. Energy Statistics

### Basic Queries
```
Q7.1: What was the total energy consumption in India in 2022-23?
Expected Tool: get_energy_statistics
Expected Category: indicator (consumption), year (2022-23)

Q7.2: Show me coal production statistics for 2023
Expected Tool: get_energy_statistics
Expected Category: source (coal), year (2023)

Q7.3: What is the renewable energy generation in Maharashtra for 2022-23?
Expected Tool: get_energy_statistics
Expected Category: state (Maharashtra), source (renewable), year (2022-23)

Q7.4: Compare energy consumption between industrial and residential sectors in 2023
Expected Tool: get_energy_statistics
Expected Category: sector (industrial & residential), year (2023)

Q7.5: What was the electricity generation from solar sources in 2023?
Expected Tool: get_energy_statistics
Expected Category: source (solar), year (2023)
```

---

## 8. HCES (Household Consumption Expenditure Survey)

### Basic Queries
```
Q8.1: What is the average monthly per capita consumption expenditure (MPCE) in rural India for 2022-23?
Expected Tool: get_hces_data
Expected Category: sector (Rural), year (2022-23), indicator (MPCE)

Q8.2: Show me consumption patterns in urban Maharashtra in 2022-23
Expected Tool: get_hces_data
Expected Category: state_code (Maharashtra), sector (Urban), year (2022-23)

Q8.3: What is the expenditure on food items across different fractile classes?
Expected Tool: get_hces_data
Expected Category: item_category (food), mpce_fractile_classes

Q8.4: Compare consumption expenditure between rural and urban areas in 2022-23
Expected Tool: get_hces_data (called twice or with both sectors)
Expected Category: sector (Rural & Urban), year (2022-23)

Q8.5: What is the average MPCE for SC/ST households in Rajasthan?
Expected Tool: get_hces_data
Expected Category: state (Rajasthan), social_group (SC/ST)

Q8.6: Show consumption expenditure by different employment categories
Expected Tool: get_hces_data
Expected Category: employment_of_households

Q8.7: What is the imputed rent value for rural households?
Expected Tool: get_hces_data
Expected Category: imputation_type, sector (Rural)

Q8.8: Compare cereal consumption patterns between states
Expected Tool: get_hces_data
Expected Category: cereal types, multiple states
```

### Lookup Queries
```
Q8.9: What social group codes are available in HCES?
Expected Tool: lookup_mospi_codes
Expected Category: social_group

Q8.10: Show me all item categories tracked in HCES
Expected Tool: lookup_mospi_codes
Expected Category: item_category
```

---

## 9. NSS78 (National Sample Survey Round 78)

### Basic Queries
```
Q9.1: What percentage of households have mobile phones in rural areas?
Expected Tool: get_nss78_data
Expected Category: Indicator (Usage of Mobile Phone), Sector_code (1=Rural)

Q9.2: Show me internet access statistics for urban youth
Expected Tool: get_nss78_data
Expected Category: Indicator (Internet Access), Sector_code (2=Urban), AgeGroup_code

Q9.3: What are the migration patterns from Bihar?
Expected Tool: get_nss78_data
Expected Category: State_code (Bihar), Indicator (Main Reason for Migration)

Q9.4: Compare access to improved sanitation between rural and urban areas
Expected Tool: get_nss78_data
Expected Category: Indicator (Improved Latrine), Sector_code (1 & 2)

Q9.5: What percentage of households have access to improved drinking water in Rajasthan?
Expected Tool: get_nss78_data
Expected Category: State_code (Rajasthan), Indicator (Improved Source of Drinking Water)

Q9.6: What are the main reasons people left their usual place of residence?
Expected Tool: get_nss78_data
Expected Category: Indicator (Main Reason for Leaving), Household_LeavingReason_code

Q9.7: Show gender-wise mobile phone usage across India
Expected Tool: get_nss78_data
Expected Category: Indicator (Usage of Mobile Phone), Gender_code (1, 2, 3)

Q9.8: What household assets are most common in urban areas?
Expected Tool: get_nss78_data
Expected Category: Indicator (Household Assets), Sector_code (2=Urban)

Q9.9: Compare sources of finance for migration between rural and urban households
Expected Tool: get_nss78_data
Expected Category: Indicator (Different Sources of Finance), SourceOfFinance_code, Sector_code
```

### Lookup Queries
```
Q9.10: What indicators are tracked in NSS Round 78?
Expected Tool: lookup_mospi_codes
Expected Category: Indicator_code

Q9.11: Show me all household leaving reason codes
Expected Tool: lookup_mospi_codes
Expected Category: Household_LeavingReason_code

Q9.12: What age group codes are available in NSS78?
Expected Tool: lookup_mospi_codes
Expected Category: AgeGroup_code
```

---

## 10. NFHS (National Family Health Survey)

### Basic Queries
```
Q10.1: What is the infant mortality rate in India according to NFHS-5?
Expected Tool: get_nfhs_data
Expected Category: indicator_code (4), survey_code (3=NFHS-5)

Q10.2: Show me infant and child mortality rates in Uttar Pradesh
Expected Tool: get_nfhs_data
Expected Category: indicator_code (4), state_code (Uttar Pradesh), sector (Combined)

Q10.3: What is the infant mortality rate in rural vs urban areas of Maharashtra?
Expected Tool: get_nfhs_data (called twice or with both sectors)
Expected Category: indicator_code (4), state_code (Maharashtra), sector_code (1=Rural & 2=Urban)

Q10.4: Compare family planning usage between NFHS-4 and NFHS-5
Expected Tool: get_nfhs_data
Expected Category: indicator_code (5), survey_code (2,3)

Q10.5: What are the marriage and fertility statistics for rural Rajasthan?
Expected Tool: get_nfhs_data
Expected Category: indicator_code (3), state_code (Rajasthan), sector_code (1=Rural)

Q10.6: Show population and household profile data for urban Tamil Nadu
Expected Tool: get_nfhs_data
Expected Category: indicator_code (1), state_code (Tamil Nadu), sector_code (2=Urban)

Q10.7: What is the neonatal mortality rate across all states in NFHS-5?
Expected Tool: get_nfhs_data
Expected Category: indicator_code (4), sub_indicator_code (neonatal), survey_code (3)

Q10.8: Compare child mortality rates between Kerala and Bihar
Expected Tool: get_nfhs_data
Expected Category: indicator_code (4), state_code (Kerala & Bihar)

Q10.9: What percentage of women use modern contraceptive methods in rural India?
Expected Tool: get_nfhs_data
Expected Category: indicator_code (5), sub_indicator_code (modern methods), sector_code (1)

Q10.10: Show trends in infant mortality from NFHS-4 to NFHS-5
Expected Tool: get_nfhs_data
Expected Category: indicator_code (4), survey_code (2,3)
```

### Lookup Queries
```
Q10.11: What health indicators are tracked in NFHS?
Expected Tool: lookup_mospi_codes
Expected Category: indicator

Q10.12: Show me all sub-indicators available for infant mortality
Expected Tool: lookup_mospi_codes
Expected Category: sub_indicator (filtered by indicator 4)

Q10.13: What states are covered in NFHS?
Expected Tool: lookup_mospi_codes
Expected Category: state
```

---

## 11. ASUSE (Annual Survey of Unincorporated Sector Enterprises)

### Basic Queries
```
Q11.1: How many unincorporated enterprises are there in India according to ASUSE 2021-22?
Expected Tool: get_asuse_data
Expected Category: indicator_code (1=Number of establishments), year (2021-22)

Q11.2: What is the total number of workers in unincorporated enterprises?
Expected Tool: get_asuse_data
Expected Category: indicator_code (2=Total workers)

Q11.3: Show me enterprises data for Maharashtra
Expected Tool: get_asuse_data
Expected Category: state_code (27=Maharashtra), indicator_code (1)
Expected Result: Should include metadata_context with state name
```

### State and Sector Queries
```
Q11.4: How many rural enterprises are there in India?
Expected Tool: get_asuse_data
Expected Category: sector_code (1=Rural), indicator_code (1)

Q11.5: Compare urban vs rural enterprises in Tamil Nadu
Expected Tool: get_asuse_data (called twice)
Expected Category: state_code (33=Tamil Nadu), sector_code (1=Rural, 2=Urban)

Q11.6: Show enterprise distribution across all states for 2021-22
Expected Tool: get_asuse_data
Expected Category: indicator_code (1), year (2021-22)
```

### Activity and Establishment Type Queries
```
Q11.7: How many manufacturing enterprises are there?
Expected Tool: lookup_mospi_codes (first to find manufacturing activity codes)
Expected Tool: get_asuse_data
Expected Category: activity_code (manufacturing codes), indicator_code (1)

Q11.8: Show data for Own Account Enterprises (OAE) only
Expected Tool: get_asuse_data
Expected Category: establishment_type_code (2=OAE), indicator_code (1)

Q11.9: What types of economic activities are tracked in ASUSE?
Expected Tool: lookup_mospi_codes
Expected Category: activity (50 types)
```

### Worker and Owner Characteristics
```
Q11.10: Show enterprises by gender of owner
Expected Tool: get_asuse_data
Expected Category: gender_code (1-5), indicator_code (1)

Q11.11: How many enterprises are owned by SC/ST communities?
Expected Tool: lookup_mospi_codes (first to find SC/ST codes)
Expected Tool: get_asuse_data
Expected Category: owner_social_group_code, indicator_code (1)

Q11.12: Show enterprises by owner's education level
Expected Tool: get_asuse_data
Expected Category: owner_education_level_code (1-8), indicator_code (1)

Q11.13: What is the distribution of worker types in unincorporated enterprises?
Expected Tool: lookup_mospi_codes (first to see worker types)
Expected Tool: get_asuse_data
Expected Category: worker_type_code (1-12), indicator_code (2=Total workers)
```

### Complex Filters
```
Q11.14: Show rural manufacturing enterprises owned by women in Maharashtra for 2021-22
Expected Tool: get_asuse_data
Expected Category: state_code (27), sector_code (1=Rural), gender_code (2=Female),
                  activity_code (manufacturing), year (2021-22), indicator_code (1)

Q11.15: How many enterprises use internet services?
Expected Tool: lookup_mospi_codes (first to understand internet usage codes)
Expected Tool: get_asuse_data
Expected Category: using_internet_code (1=Yes), indicator_code (1)

Q11.16: Show enterprises that maintain accounts and are registered
Expected Tool: get_asuse_data
Expected Category: account_holder_code (1=Yes), agency_registration_code (registered codes)
```

### Lookup Queries
```
Q11.17: What indicators are available in ASUSE?
Expected Tool: lookup_mospi_codes
Expected Category: indicator (39 indicators)

Q11.18: What are the different ownership types tracked?
Expected Tool: lookup_mospi_codes
Expected Category: ownership_type (10 types)

Q11.19: Show me all sub-indicators for worker characteristics
Expected Tool: lookup_mospi_codes
Expected Category: sub_indicator (19 sub-indicators)

Q11.20: What establishment types does ASUSE cover?
Expected Tool: lookup_mospi_codes
Expected Category: establishment_type (HWE, OAE, Combined)
```

---

## 12. Cross-Dataset Queries

### Complex Multi-Dataset Questions
```
Q12.1: Compare unemployment rate (PLFS) with GDP growth (NAS) for 2023-24
Expected Tools: get_plfs_data + get_nas_data

Q12.2: How does CPI inflation correlate with WPI inflation in 2023?
Expected Tools: get_cpi_group_index + get_wpi_records

Q12.3: Show industrial production (IIP) trends alongside energy consumption (Energy) for 2023
Expected Tools: get_iip_monthly + get_energy_statistics

Q12.4: Compare factory employment (ASI) with overall employment rates (PLFS) in Maharashtra
Expected Tools: get_asi_data + get_plfs_data

Q12.5: Analyze household consumption patterns (HCES) in relation to inflation (CPI) in 2023-24
Expected Tools: get_hces_data + get_cpi_group_index

Q12.6: Compare infant mortality rates (NFHS) with household consumption expenditure (HCES) by state
Expected Tools: get_nfhs_data + get_hces_data

Q12.7: Analyze mobile phone usage (NSS78) in relation to household income levels (HCES)
Expected Tools: get_nss78_data + get_hces_data

Q12.8: Compare unincorporated enterprise growth (ASUSE) with industrial production (IIP) trends
Expected Tools: get_asuse_data + get_iip_monthly

Q12.9: Analyze enterprise ownership patterns (ASUSE) alongside labour force participation (PLFS) by gender
Expected Tools: get_asuse_data + get_plfs_data
```

---

## 13. Edge Cases & Error Handling

### Invalid Input Tests
```
Q13.1: What is the unemployment rate in Hogwarts? (Invalid state)
Expected: Error handling / clarification

Q13.2: Show me CPI data for year 3000 (Invalid year)
Expected: Error handling / no data message

Q13.3: Get me PLFS data for "banana" category (Invalid category)
Expected: Error handling / clarification

Q13.4: What is the CPI in PLFS dataset? (Wrong dataset for metric)
Expected: Clarification / redirect to correct dataset
```

---

## Tool Call Tracking Template

Use this format to record your test results:

```
Question: [Copy question here]
ChatGPT Response: [Summary of response]
Tools Called: [List of tools ChatGPT reports using]
Parameters Used: [Key parameters extracted]
Success: ✅ / ❌
Notes: [Any issues or observations]
---
```

---

## How to Ask ChatGPT to Show Tool Calls

After each query, immediately follow up with:

**"Which MCP tools did you call to answer this? Please list all tool names and their main parameters."**

Or include in each query:

**"[Your question here] - Please also tell me which MCP tools you used."**

---

## Expected Results Summary

| Dataset | Total Questions | Lookup Questions | Data Questions |
|---------|----------------|------------------|----------------|
| PLFS    | 8              | 3                | 5              |
| CPI     | 8              | 3                | 5              |
| IIP     | 7              | 2                | 5              |
| ASI     | 8              | 3                | 5              |
| WPI     | 8              | 3                | 5              |
| NAS     | 7              | 2                | 5              |
| Energy  | 5              | 0                | 5              |
| HCES    | 5              | 0                | 5              |
| NSS78   | 5              | 0                | 5              |
| Cross   | 5              | 0                | 5              |
| Edge    | 4              | 0                | 4              |
| **Total** | **70**      | **16**           | **54**         |


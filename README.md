# Error Distinguishing Program for GEDCOM

This is a project for the SSW555 of Stevens Institute of Technology taught by geekiest professor Jim Rowland :P

## 0. Table of Content

1. [Intro of GEDCOM](#intro-of-gedcom)
2. [Project precondition](#project-precondition)

## 1. Intro of GEDCOM

GEDCOM is a standard format for genealogy data developed by The Church of Jesus Christ of Latter-day Saints.

### 1.1 Entities

GEDCOM identifies **two** major entities:

- **individuals**
- **families**

Characteristics of **individuals**:

- Unique individual ID
- Name
- Sex/Gender
- Birth Date
- Death Date
- Unique Family ID where the individual is a *child*
- Unique Family ID where the individual is a *spouse*

Characteristics of **families**:

- Unique family ID
- Unique individual ID of husband
- Unique individual ID of wife
- Unique individual ID of each child in the family
- Marriage date
- Divorce date, if appropriate

### 1.2 GEDCOM file format

GEDCOM is a line-oriented text file format where each line has three parts separated by blank space:

1. **level number** (0, 1 or 2)
2. **tag** (a string of 3 or 4 characters, usually UPPER CASE)
3. **arguments** (an optional character string)

Records with level number 1 or 2 are always in the form:

```sh
<level_number> <tag> <arguments>
```

Records with level number 0 has one of two different forms:

  1. `0 <id> <tag>`  
  where `<tag>` in `('INDI', 'FAM')`  
  `<id>` is a unique identifier for individual or family.

  2. `0 <tag> <arguments that may be ignored>`  
  where `<tag>` in `('HEAD', 'TRLR', 'NOTE')`

## 2 Project Precondition

### 2.1 Assumptions

We will assume that:

- The four records that require a date (BIRT, DEAT, DIV, MARR) will always be followed by a DATE record.
- The sex and birth date of every individual will be specified exactly once. (You cannot change your sex.)
- For each family specified in the file, the marriage and all family members will be specified.
- Each individual will be linked to every family where they are a child, for all those families that are described by the GEDCOM file.
- Each individual will be linked to every family where they are a spouse, for all those families that are described by the GEDCOM file.

We will make some assumptions when records are missing from the file:

- We will assume that an individual is alive if there is no DEAT record.
- We will assume no divorce has occurred for a marriage if there is no DIV record.
- Some families may not be specified, since the parents of the family are not specified in the file.
- This last condition describes the top of the genealogical tree - it has to stop somewhere.

### 2.2 Error Class

We are writing a **program** that looks for ***Error*** and ***Anomalies***.

- ***Errors*** are combinations of records that cannot logically all be true:

  - Death date occurring before birth date
  - Marriage of a dead person
  - Female husband in a family
  - **Note that you get no credit for detecting syntax errors. All data is assumed to bec syntactically correct.**

- ***Anomalies*** are combinations of records that appear to be erroneous, but might actually be true:

  - Birth of a child before his/her parents are married (potentially embarrassing if true)
  - Being a spouse in two marriages at the same time (polygamy, illegal in most places)

We are going to define two `class`es to represent errors and anomalies respectively.

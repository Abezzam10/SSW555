# SSW555 TeamAJRY: GEDCOM CLI

This is a project for the SSW555 of Stevens Institute of Technology taught by geekiest professor Jim Rowland.

---

- **Team Member**:

  - Yinghui Cai(Benji)
  - Rahil Patel(Ray)
  - Aniruddha Pimple(John)
  - Jiahua Zhou(Javer)

- **User stories for sprint 2**:

|Story ID|Story Name|Owner|
|:---:|:---:|:---:|
|US04|Marriage before divorce|John|
|US07|Less then 150 years old|Benji|
|US08|Birth before marriage of parents|Ray|
|US13|Siblings spacing|John|
|US14|Multiple births <= 5|Javer|
|US16|Male last names|Javer|
|US23|Unique name and birth date|Ray|
|US26|Corresponding entries|Benji|

---

## 0. Table of Content

1. [Lastest Change of the Code](#1-lastest-change-of-the-code)
2. [Installation & PyPI](#2-installation--pypi)
3. [Workflow of Version Control](#3-workflow-of-version-control)
4. [Project Overview Link](doc/Project_overview.md)
5. [Coding Style Guideline](doc/coding_style_specification.md)

## 1 Lastest Change of the Code

The major change happens in `gedcom_ajry.py`, changes in unit tests are the result of the change in this python file. Below is the major changes:

1. **class `Error` and `Warn` are deleted** for the sake of saving maintanence cost.
2. Instead of using the deleted classes to print the error/anomaly message, a multi-layered Python dictionary, `self.msg_collection`, is defined in the `Gedcom` object and used for storage of exceptions dctected by the program.
3. The dictionary is separated in two parts to store errors and anomaly respectively.
4. The most important part of the dictionary is the `msg_collection['err'|'anomaly']['msg_container']`. It's a dictionary with **user story ID** as keys, and **formatted messages** and **information tokens** as values. Please go to the code and read the `__init__` of `class Gedcom` carefully. ***Noted that developers MUST comment the elements structure of token tuple in every user story container.***
5. A new method of `class Gedcom`, `msg_print()`, is created to iterate the `msg_colletion` and pretty print the exception messages. The method is written under the assumption that all of the user stories' tokens are collected in a list. Please pay attention to it.

## 2 Installation & PyPI

We havn't update the [package on PyPI](https://pypi.org/project/GEDCOM-Benji/) for a while as it takes more effort than we thought for the update of product attributes. However you can use a `-e` or `--editable` option in `pip3` command to install a editable version of package in your environment. With `--editable` option, the functionality of the command line will change along with the change of code.

```sh
pip3 install --editable .
```

Note that it's required to use the dot(`.`) to represent the current directory instead of use the package name.

## 3 Workflow of Version control

1. On the GitHub repository webpage, create your own branch with the name pattern `sprint2_initial` (e.g. `sprint2_benji`) based on branch `sprint2`

2. Go to the command line and pull down your own branch with following steps, with the example of branch `sprint2_benji`:
    1. `git checkout sprint2_benji`
    2. `git pull --all`

3. Develop your user stories, test cases on your branch and push it on your own branch. I will do the merging carefully after you push the branch.

## 4 MongoDB Storage Data Structure

![mongodb-data-structure](pic/DB_Structure.png)

## 5 Project Overview

***We are using a MVC architecture for our project.***

To keep the README nice and clean, we have the *project overview* and *random ideas list* wrapped up in another [file](doc/Project_overview.md). Feel free to check it out!

## 6 Coding Style Specification

Please see the [file](doc/coding_style_specification.md) for the naming pattern suggestions.

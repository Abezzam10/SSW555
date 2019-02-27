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

1. [Installation & PyPI](#1-installation--pypi)
2. [Test Strategy](#2-workflow-of-version-control)
3. [Project Overview Link](Project_overview.md)
4. [Coding Style Guideline](coding_style_specification.md)

## 1 Installation & PyPI

We havn't update the [package on PyPI](https://pypi.org/project/GEDCOM-Benji/) for a while as it takes more effort than we thought for the update of product attributes. However you can use a `-e` or `--editable` option in `pip3` command to install a editable version of package in your environment. With `--editable` option, the functionality of the command line will change along with the change of code.

```sh
pip3 install --editable .
```

Note that it's required to use the dot(`.`) to represent the current directory instead of use the package name.

## 2 Workflow of Version control

1. Pull down all of the latest change of the repository with `git pull –all`.

2. Checkout to your own branch e.g. `git checkout sprint1-benji`.

3. Merge the latest change of branch sprint1 by `git merge sprint1`, and accept all of the incoming change.

4. Develop your user stories, test cases on your branch and push it on your own branch. I will do the merging carefully after you push the branch.

## 3 Project Overview

***We are using a MVC architecture for our project.***

To keep the README nice and clean, we have the *project overview* and *random ideas list* wrapped up in another [file](Project_overview.md). Feel free to check it out!

## 4 Coding Style Specification

Please see the [file](coding_style_specification.md) for the naming pattern suggestions.
